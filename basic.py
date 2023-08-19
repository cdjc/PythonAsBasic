import ast
import inspect
import io
import re
import sys
import types
from typing import Callable, Union
from goto import goto


class UnexpectedASTNode(Exception):

    def __init__(self, node: ast.AST, expected: type):
        super().__init__(f"Expected {expected.__name__} but got {node.__class__.__name__}")

class UnexpectedASTNodeValue(Exception):

    def __init__(self, msg):
        super().__init__(msg)

def isASTNodeType(node: ast.AST, expected: type):
    return isinstance(node, expected)


def checkASTNodeType(node: ast.AST, expected: type):
    if not isASTNodeType(node, expected):
        raise UnexpectedASTNode(node, expected)
    return node


# isModule = lambda n: isASTNodeType(n, ast.Module)
checkModule = lambda n: checkASTNodeType(n, ast.Module)
# isFunctionDef = lambda n: isASTNodeType(n, ast.FunctionDef)
checkFunctionDef = lambda n: checkASTNodeType(n, ast.FunctionDef)


re_line_no = re.compile(r'_[1-9][0-9]*')
re_line_no_prefix = re.compile(r'(_[1-9][0-9]*)\.')
re_tuple_line_no = re.compile(r'\((_[1-9][0-9]*)\..*\)')
re_print_fn = re.compile(r"PRINT\((.*)\)")
# TODO: Fix this for multidimensional arrays
re_dim = re.compile(r'DIM\.[A-Z][0-9A-Z]*\([0-9]+\)(, [A-Z][0-9A-Z]*\([0-9]+\))*')
re_assign = re.compile(r'(?P<LHSVar>[A-Z][0-9A-Z]*)(?P<array>\[.*\])?\s*=\s*(?P<expr>.*)')
re_input_var = re.compile(r"INPUT(\('(.*)'\))?\.([A-Z][0-9A-Z]*)")
re_if_stmt = re.compile(r"IF\((?P<expr>.*)\)\.THEN\.(?P<stmt>.*)")
# TODO Add step to FOR
re_for_stmt = re.compile(r"FOR\.(?P<var>[A-Z][A-Z0-9]*)\s*=\s*\((?P<expr_from>.*),\s*TO,\s*(?P<expr_to>.*)\)")
re_next_stmt = re.compile(f'NEXT\.[A-Z][A-Z0-9]*')

# expression rewriting
re_left_fn = re.compile(r'LEFT\(\s*(?P<var>[A-Z][A-Z0-9]*)\s*,\s*(?P<len>\d+\s*)\)')
re_rand_fn = re.compile(r'RND\([0-9]*\)')


for_stack = []
for_counter = 0
def rewrite_expression(line: str):
    line = re_left_fn.sub(lambda m: f'{m.group("var")}[:{m.group("len")}]', line)  # LEFT(A, 2) -> A[:2]
    line = line.replace('INT(', 'int(')
    line = re_rand_fn.sub('random.random()', line)
    print('expr',line)
    return line
def rewrite_statement(node: ast.AST):
    global for_counter

    raw_line = ast.unparse(node)

    # strip off the line number if present

    line_no_str = None
    if line_no_match := re_line_no_prefix.match(raw_line):
        line_no_str = line_no_match.group(1)
        line = raw_line[line_no_match.end():]
    elif tuple_line_match := re_tuple_line_no.fullmatch(raw_line):
        line_no_str = tuple_line_match.group(1)
        line = raw_line[tuple_line_match.end(1)+1:-1]
    else:
        line = raw_line


    print(line_no_str,'->',line)

    if line == 'PRINT':
        new_line = 'print()'
    elif line == 'RANDOMIZE':  # TODO: We should tweak this so we can run repeatable tests
        new_line = 'pass'
    elif match := re_print_fn.fullmatch(line):
        exp = match[1]
        noln = exp[-2:] == '._'
        if noln:
            exp = exp[:-2]
            end = "''"
        else:
            end = r"'\n'"
        exp = rewrite_expression(exp)
        new_line = f"print({exp}, end={end})"
    elif match := re_dim.fullmatch(line):
        # strip off the leading DIM.
        nodimline = line[4:]
        # TODO: The dim list could be expressions
        var_list = re.findall(r'[A-Z][0-9A-Z]*', nodimline)
        dim_list = re.findall(r'\([1-9][0-9]*\)', nodimline)
        assert len(var_list) == len(dim_list)
        var_str = ','.join(var_list)
        # NOTE: array size is dim + 1 https://www.c64-wiki.com/wiki/DIM
        dim_str = ','.join(f'[0]*(({x})+1)' for x in dim_list)
        new_line = var_str + '=' + dim_str
    elif match := re_assign.fullmatch(line):
        rhs = rewrite_expression(match['expr'])
        lhsvar = match['LHSVar']
        lhsarray = match['array']
        lhs = lhsvar
        if lhsarray is not None:
            # TODO: lhsarray could me multidimensional and are expressions.
            lhs = lhs + lhsarray
        new_line = lhs + ' = '+rhs
    elif match := re_input_var.fullmatch(line):
        if match[2]:
            new_line = f"print('{match[2]}', end=' ');{match[3]} = input()"
        else:
            new_line = f'{match[3]} = input()'
        new_line += '\nprint()'  # implied newline after INPUT
    elif match := re_if_stmt.fullmatch(line):
        exp = match.group('expr')
        stmt = match.group('stmt')
        exp = rewrite_expression(exp)
        if line_no := re_line_no.fullmatch(stmt):
            stmt = f'GOTO.{line_no[0]}'
        new_line = f'if {exp}:\n    {stmt}'
    elif match := re_for_stmt.fullmatch(line):
        # FOR statement calcs:
        # FOR I = X TO Y STEP Z
        # <code>
        # NEXT I

        # see https://www.c64-wiki.com/wiki/FOR
        # see also https://archive.org/details/1984-11-compute-magazine
        # see ECMA-55 1st edition 1978 pdf page 18

        # We always assume for-nexts are balanced correctly (like parentheses). We don't follow C64 semantics.

        for_counter += 1
        for_label = f'for_loop_{for_counter}'
        for_step_var = f'{for_label}_step'
        post_for_label = f'for_end_{for_counter}'

        # I = X
        # label .for_loop_1
        # if (I - Y) * sign(Z) > 0: goto for_end_1
        # <code>
        # I = I + Z    # NEXT I
        # goto .for_loop_1
        # label .for_end_1

        var = match['var']
        start_expr_raw = match['expr_from']
        end_expr_raw = match['expr_to']
        start_expr = rewrite_expression(start_expr_raw)
        end_expr = rewrite_expression(end_expr_raw)
        step_expr = '1'  # TODO: add step expr in regular expression
        line_assign = f'{var} = {start_expr}'
        line_step_assign = f'{for_step_var} = {step_expr}'
        line_start_label = f'label. {for_label}'
        line_test = f'if ({var} - ({end_expr})) * [-1,1][{for_step_var}>=0] > 0:'  # Use hack for sign function
        line_goto_end = f'    goto .{post_for_label}'

        for_stack.append((for_counter, var))

        new_line = '\n'.join([line_assign, line_step_assign, line_start_label, line_test, line_goto_end])
    elif match := re_next_stmt.fullmatch(line):
        for_count, var = for_stack.pop()
        for_label = f'for_loop_{for_count}'
        for_step_var = f'{for_label}_step'
        post_for_label = f'for_end_{for_count}'

        line_incr = f'{var} = {var} + {for_step_var}'
        line_goto = f'goto .{for_label}'
        line_end = f'label .{post_for_label}'

        new_line = '\n'.join((line_incr, line_goto, line_end))
    else:
        raise Exception("Don't know this line: "+line)

    if line_no_str:
        new_line = 'label .'+line_no_str+'\n'+new_line
    # print('NL',new_line)

    new_line = f'line="""{str(raw_line)}"""\n{new_line}'
    new_module = ast.parse(new_line, __name__, mode='exec')
    new_nodes = new_module.body
    for new_node in new_nodes:
        ast.copy_location(new_node, node)
        ast.fix_missing_locations(new_node)
    return new_nodes


def make_header_ast(fn_ast: ast.FunctionDef):
    header = '''
import random
'''
    new_module = ast.parse(header, __name__, mode='exec')
    new_nodes = new_module.body
    for new_node in new_nodes:
        ast.copy_location(new_node, fn_ast)
        ast.fix_missing_locations(new_node)
    return new_nodes


def process_statements(root: ast.Module):
    '''
    Process each statement for transformation
    :param root: an AST of a Module with a single Function with 1+ PaB statements
    :return: None
    '''
    checkModule(root)
    fn = root.body[0]
    checkFunctionDef(fn)
    nodes = make_header_ast(fn)
    for statement in fn.body:
        #print('!',ast.unparse(statement))
        nodes.extend(rewrite_statement(statement))
        #nodes.extend(process_basic_statement(statement))
    fn.body = nodes
    print(ast.unparse(fn))


def basic(fn: Callable) -> Callable:
    source = inspect.getsource(fn)
    # peel off this decorator from the code.
    fn_source = source[source.find('\n') + 1:]

    indent = fn_source.find('def')
    fn_source = '\n'.join(x[indent:] for x in fn_source.split('\n'))

    print('-'*8)
    print(fn_source)
    root = ast.parse(fn_source)
    #print(ast.dump(root, indent=' '))
    #print(ast.unparse(root))

    process_statements(root)

    # print('-'*8)
    # print(ast.unparse(root))

    module_code = compile(root, fn.__code__.co_filename, mode='exec')
    function_code = module_code.co_consts[0]  # The function is the first thing in the "module"
    fn = types.FunctionType(function_code, fn.__globals__)
    fn = goto(fn)
    return fn


class auto_input:
    def __init__(self, text: str):
        self.buffer = io.StringIO(text)

    def __enter__(self):
        self.old_stdin = sys.stdin
        sys.stdin = self.buffer

    def __exit__(self, *_):
        sys.stdin = self.old_stdin


if __name__ == '__main__':
    #@basic
    def prnt():
        _10. FOR.I=1,TO,2
        _15. FOR.J=4,TO,5
        _20. PRINT(I,J)
        _40. NEXT.J
        _30. NEXT.I
        #A[1] = 5
        #print()
        #_20. PRINT("here")

    @basic
    def print_here():
        #_10. PRINT("HERE")
        #_20 .PRINT
        #_30 .PRINT("THERE")
        #_40 .PRINT;PRINT("CHAIN")
        #PRINT('F'._);PRINT('G')

        _30. DIM.A1(6),A(3),B(3)
        _40. Y=0;T=255
        _70. INPUT("Y/N").AS
        _90. IF(LEFT(AS, 1) == "N").THEN._150
        #_101. PRINT('PREFOR')
        _150. FOR.I=1, TO, 3
        #_151. PRINT('FORI',I)
        _160. A[I]=INT(10*RND(1))
        #_161. PRINT('A[I],I',A[I],I)
        _165. IF(I - 1 == 0).THEN._200
        _170. FOR.J = 1, TO, I-1
        #_171. PRINT("J",J)
        #_172. PRINT('I,A[I],J,A[J]',I,A[I],J,A[J])
        _180. IF(A[I] == A[J]).THEN._160
        _190. NEXT.J
        _200. NEXT.I
        _210. PRINT(A[1], A[2], A[3])
        _220. PRINT('DONE')


    #@basic
    def b2():
        pass
        # _30. DIM.A1(6), A(3), B(3)
        # _40. RANDOMIZE;Y = 0;T = 255
        # _70. INPUT("Y/N"); AS
        # _90. IF.AS = "NO".THEN._150
        # _150. FOR.I = 1, TO, 3
        # _160. A[I] = INT(10 * RND)
        # _165. IF(I - 1 == 0).THEN._200
        # _170. FOR.J = 1, TO, I - 1
        # _180. IF.A[i] = A[j].THEN._160
        # _190. NEXT.J
        # _200. NEXT.I
        # _210. PRINT;PRINT("O.K.  I HAVE A NUMBER IN MIND")
        # _220. FOR.I = 1, TO, 20
        # _295. GOTO._320




    #prnt()
    with auto_input("Y\n"):
        pass
        #prnt()
        print_here()