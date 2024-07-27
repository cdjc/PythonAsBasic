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


checkModule = lambda n: checkASTNodeType(n, ast.Module)
checkFunctionDef = lambda n: checkASTNodeType(n, ast.FunctionDef)

re_line_no = re.compile(r'_[1-9][0-9]*')
re_line_no_prefix = re.compile(r'(_[1-9][0-9]*)\.')
re_tuple_line_no = re.compile(r'\((_[1-9][0-9]*)\..*\)')
re_print_fn = re.compile(r"PRINT\((.*)\)")
# TODO: Fix this for multidimensional arrays
re_dim = re.compile(r'DIM\.[A-Z][0-9A-Z]*\([0-9]+\)(, [A-Z][0-9A-Z]*\([0-9]+\))*')
re_assign = re.compile(r'(?P<LHSVar>[A-Z][0-9A-Z]*)(?P<array>\[.*\])?\s*=\s*(?P<expr>.*)')
re_input_var = re.compile(r"INPUT(\('(.*)'\))?\.([A-Z][0-9A-Za-z]*)")
re_if_stmt = re.compile(r"IF\((?P<expr>.*)\)\.THEN\.(?P<stmt>.*)")
# TODO Add step to FOR
re_for_stmt = re.compile(r"FOR\.(?P<var>[A-Z][A-Z0-9]*)\s*=\s*\((?P<expr_from>.*),\s*TO,\s*(?P<expr_to>.*)\)")
re_next_stmt = re.compile(r'NEXT\.[A-Z][A-Z0-9]*')
re_goto_stmt = re.compile(r'GOTO\._[1-9][0-9]*')
re_gosub_stmt = re.compile(r'GOSUB\._[1-9][0-9]*')
re_rem_stmt = re.compile(r'REM\.*')
re_end_stmt = re.compile(r'END')
re_stop_stmt = re.compile(r'STOP')
re_return_stmt = re.compile(r'RETURN')

for_stack = []
for_counter = 0

return_targets = []
next_line_is_return_target = False
return_stmt_nodes = []  # The return statement node
# the node with the ast.Constant which will need to be replaced by the target of the return after a gosub
# i.e. the label of the next line after the gosub
gosub_return_target_nodes = []
def rewrite_statement(node: ast.AST):
    global for_counter, return_targets, return_stmt_nodes, next_line_is_return_target
    global gosub_return_target_nodes
    gosub_return_stmt = False

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

    if line_no_str and next_line_is_return_target:
        return_targets.append(line_no_str)
        next_line_is_return_target = False

    # print(line_no_str,'->',line)

    if line == 'PRINT':
        new_line = 'print()'
    elif line == 'RANDOMIZE':  # TODO: We should tweak this so we can run repeatable tests
        new_line = 'pass'
    elif match := re_print_fn.fullmatch(line):
        exp = match[1]
        noln = exp[-2:] == '._'
        if noln:
            exp = exp[:-2]
            end = "' '"
        else:
            end = r"'\n'"
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
        rhs = match['expr']
        lhsvar = match['LHSVar']
        lhsarray = match['array']
        lhs = lhsvar
        if lhsarray is not None:
            # TODO: lhsarray could be multidimensional and are expressions.
            lhs = lhs + lhsarray
        new_line = lhs + ' = '+rhs
    elif match := re_input_var.fullmatch(line):
        # could be string or integer depending on variable. string is A$ which is Astr
        input_str = 'input()'
        if not match[3].endswith('str'):
            input_str = 'int(input())'

        if match[2]:
            new_line = f"print('{match[2]}', end=' ');{match[3]} = {input_str}"
        else:
            new_line = f'{match[3]} = {input_str}'
        new_line += '\nprint()'  # implied newline after INPUT
    elif match := re_if_stmt.fullmatch(line):
        exp = match.group('expr')
        stmt = match.group('stmt')
        if line_no := re_line_no.fullmatch(stmt):
            stmt = f'goto.{line_no[0]}'
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
        start_expr = start_expr_raw
        end_expr = end_expr_raw
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
    elif match := re_gosub_stmt.fullmatch(line):
        new_line = f"_gosub_stack.append('FILLMEIN')\n"
        new_line += line.replace('GOSUB', 'goto')
        next_line_is_return_target = True
    elif match := re_return_stmt.fullmatch(line):
        gosub_return_stmt = True
        new_line = "return"  # marker to find and replace later
    elif match := re_goto_stmt.fullmatch(line):
        new_line = line.replace('GOTO', 'goto')
    elif match := re_rem_stmt.fullmatch(line):
        new_line = line.replace('REM', 'pass #')
    elif match := re_end_stmt.fullmatch(line):
        new_line = line.replace('END', 'if __name__: return')
    elif match := re_stop_stmt.fullmatch(line):
        new_line = line.replace('STOP', 'return')
    else:
        #raise Exception("Don't know this line: "+line)

        # pass through Python lines
        # If we raise an exception instead, we can catch translation errors
        # At "compile" time instead of run time.
        new_line = line

    if line_no_str:
        new_line = 'label .'+line_no_str+'\n'+new_line
    # print('NL',new_line)

    new_line = f'''_line="""{str(raw_line)}"""\npy_lineno={node.lineno}\n{new_line}'''

    new_module = ast.parse(new_line, __name__, mode='exec')
    new_nodes = new_module.body
    for new_node in new_nodes:
        fix_line_nos(new_node, node)
        if gosub_return_stmt and type(new_node) is ast.Return:
            return_stmt_nodes.append(new_node)
            gosub_return_stmt = False
        if next_line_is_return_target and \
                type(new_node) is ast.Expr and \
                type(new_node.value) is ast.Call and \
                type(new_node.value.args[0]) is ast.Constant:
            gosub_return_target_nodes.append(new_node.value.args[0])

    return new_nodes

def fix_line_nos(to_node: ast.AST, from_node: ast.AST):
    """
    Recursively inherit line numbers and column offsets from from_node

    Note: this is not the same as ast.fix_missing_locations or ast.copy_location
    """
    to_node.lineno = from_node.lineno
    to_node.end_lineno = from_node.end_lineno
    to_node.col_offset = from_node.col_offset
    to_node.end_col_offset = from_node.end_col_offset
    for child_node in ast.iter_child_nodes(to_node):
        fix_line_nos(child_node, to_node)


def fix_up_return_statements(allnodes: list[ast.AST]) -> list[ast.AST]:
    """
    We don't know what GOSUB we came from, so we need to look at the GOSUB stack
    to see what the most recent RETURN target is, and GOTO that.
    :return:
    """
    global return_targets, return_stmt_nodes
    rval = []
    for i, node in enumerate(allnodes):
        if node not in return_stmt_nodes:
            rval.append(node)
            continue
        line = '_target = _gosub_stack.pop()\n'
        for target in return_targets:
            line += f'if _target == "{target}": goto.{target}\n'
        new_module = ast.parse(line, __name__, mode='exec')
        new_nodes = new_module.body
        for new_node in new_nodes:
            fix_line_nos(new_node, node)

        rval.extend(new_nodes)
    return rval

def fix_up_gosub_return_targets():
    """
    When we first see a GOSUB, we don't know the next line (the line after the GOSUB)
    that the RETURN should come back to. So put in a placeholder and fix it here.
    :return:
    """
    global return_targets, gosub_return_target_nodes
    assert len(return_targets) == len(gosub_return_target_nodes)
    for return_target,constant_ast in zip (return_targets, gosub_return_target_nodes):
        constant_ast : ast.Constant
        constant_ast.value = return_target


def make_header_ast(fn_node):
    """
    Required at the start of each function
    """

    header = """_gosub_stack = []"""
    new_module = ast.parse(header, __name__, mode='exec')
    new_nodes = new_module.body
    for new_node in new_nodes:
        fix_line_nos(new_node, fn_node)
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
    print(return_targets, return_stmt_nodes)
    print(gosub_return_target_nodes)
    fix_up_gosub_return_targets()
    nodes = fix_up_return_statements(nodes)
    fn.body = nodes
    print(ast.unparse(fn))


def basic(fn: Callable) -> Callable:
    # source = inspect.getsource(fn)
    sourcelines, lnum = inspect.getsourcelines(fn)
    # peel off this decorator (the first line) from the code.
    # fn_source = source[source.find('\n') + 1:]
    fn_source = ''.join(sourcelines[1:])

    indent = fn_source.find('def')
    fn_source = '\n'.join(x[indent:] for x in fn_source.split('\n'))

    #print('-'*8)
    #print(fn_source)
    root = ast.parse(fn_source)
    ast.increment_lineno(root, lnum)

    process_statements(root)

    module_code = compile(root, fn.__code__.co_filename, mode='exec')
    function_code = module_code.co_consts[0]  # The function is the first thing in the "module"
    fn = types.FunctionType(function_code, fn.__globals__)
    fn = goto(fn)
    return fn


class auto_input:
    def __init__(self, text: str, seed: int = None):
        self.buffer = io.StringIO(text)
        self.seed = seed

    def __enter__(self):
        self.old_stdin = sys.stdin
        sys.stdin = self.buffer
        if self.seed:
            random.seed(self.seed)

    def __exit__(self, *_):
        sys.stdin = self.old_stdin


if __name__ == '__main__':

    from basic_functions import *
    @basic
    def prnt():
        _10. FOR.I=1,TO,2
        _12. GOSUB._70
        _15. FOR.J=4,TO,5
        _18. GOSUB._90
        _20. PRINT(I,J)
        _40. NEXT.J
        _30. NEXT.I
        _45. A="ABC"
        _50. PRINT(LEFT("ABC", 2))
        _55. A=5
        print(A,A,A)
        #_56. PRINT(D)
        _60. END
        _70. PRINT("SUB 1")
        _80. RETURN
        _90. PRINT("SUB 2")
        _100. RETURN

    prnt()