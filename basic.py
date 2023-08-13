import ast
import inspect
import io
import re
import sys
import types
from typing import Callable, Union


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


isModule = lambda n: isASTNodeType(n, ast.Module)
checkModule = lambda n: checkASTNodeType(n, ast.Module)
isFunctionDef = lambda n: isASTNodeType(n, ast.FunctionDef)
checkFunctionDef = lambda n: checkASTNodeType(n, ast.FunctionDef)
isExpr = lambda n: isASTNodeType(n, ast.Expr)
checkExpr = lambda n: checkASTNodeType(n, ast.Expr)
isCall = lambda n: isASTNodeType(n, ast.Call)
checkCall = lambda n: checkASTNodeType(n, ast.Call)
isAttribute = lambda n: isASTNodeType(n, ast.Attribute)
#checkAttribute = lambda n: checkASTNodeType(n, ast.Attribute)

def checkAttribute(n: ast.AST): return checkASTNodeType(n, ast.Attribute)
def isName(n: ast.AST): return isASTNodeType(n, ast.Name)
def checkName(n: ast.AST): return checkASTNodeType(n, ast.Name)


def m_label_expr(name: ast.Name):

    label = ast.Name('label', ast.Load())
    label_attr = ast.Attribute(label, name.id, ast.Load())
    ast.copy_location(label, name)
    ast.copy_location(label_attr, name)

    return ast.Expr(label_attr)

def m_single_statement(node: ast.Expr):
    '''
    _10. PRINT
    [Expr [Attribute [Name '_10'] 'PRINT']]

    [Expr [Attribute [Name 'label] '_10']]
    [Expr [Call [Name 'print']]]
    '''
    checkExpr(node)
    attr = checkAttribute(node.value)
    name = checkName(attr.value)

    print_name = ast.Name('print', ast.Load())
    print_call = ast.Call(print_name, [], [])
    print_expr = ast.Expr(print_call)
    ast.copy_location(print_call, node)
    ast.copy_location(print_name, node)
    ast.copy_location(print_expr, node)

    print('print_expr')
    ast.dump(print_expr)

    return [print_expr]

def m_single_functioncall(node: ast.Expr):
    '''
    _10. PRINT("HERE")

    [Expr [Call [Attribute [Name '_10] 'PRINT'] args=[Constant 'HERE']]]

    [Expr [Attribute [Name 'label] '_10']]
    [Expr [Call [Name 'print']] args=[Constant 'HERE']

    '''
    checkExpr(node)
    call = checkCall(node.value)
    attr = checkAttribute(call.func)
    name = checkName(attr.value)
    args = call.args

    print_name = ast.Name('print', ast.Load())
    print_call = ast.Call(print_name, args, [])
    print_expr = ast.Expr(print_call)
    ast.copy_location(print_call, node)
    ast.copy_location(print_name, node)
    ast.copy_location(print_expr, node)

    return [print_expr]

def m_bare_functioncall(node: ast.Expr):
    '''
    _10. PRINT; PRINT("HERE")
                ^^^^^^^^^^^^^
    Has no label, so no attribute. Can just translate the function name
    '''
    checkExpr(node)
    call = checkCall(node.value)
    name = checkName(call.func)

    if name.id == 'PRINT':
        name.id = 'print'
        return [node]
    raise UnexpectedASTNodeValue(name.id)

def process_basic_statement(node: Union[ast.Expr, ast.Assign]):

    print('line:',ast.unparse(node))
    try:
        return m_single_statement(node)
    except UnexpectedASTNode:
        pass

    try:
        return m_single_functioncall(node)
    except UnexpectedASTNode:
        pass

    try:
        return m_bare_functioncall(node)
    except UnexpectedASTNode:
        pass


re_line_no = re.compile(r'_[1-9][0-9]*')
re_line_no_prefix = re.compile(r'_([1-9][0-9]*)\.')
re_tuple_line_no = re.compile(r'\(_([1-9][0-9]*)\..*\)')
#re_print_fn = re.compile(r"PRINT\('(.*)'(\.\_)?\)")
re_print_fn = re.compile(r"PRINT\((.*)\)")
# TODO: Fix this for multidimensional arrays
re_dim = re.compile(r'DIM\.[A-Z][0-9A-Z]*\([0-9]+\)(, [A-Z][0-9A-Z]*\([0-9]+\))*')
re_assign = re.compile(r'[A-Z][0-9A-Z]*\ =\ (.*)')
re_input_var = re.compile(r"INPUT(\('(.*)'\))?\.([A-Z][0-9A-Z]*)")
re_if_stmt = re.compile(r"IF\((?P<expr>.*)\)\.THEN\.(?P<stmt>.*)")

# expression rewriting
re_left_fn = re.compile(r'LEFT\(\s*(?P<var>[A-Z][A-Z0-9]*)\s*,\s*(?P<len>\d+\s*)\)')

def rewrite_expression(line: str):
    line = re_left_fn.sub(lambda m: f'{m.group("var")}[:{m.group("len")}]', line)  # LEFT(A, 2) -> A[:2]
    print('line',line)
    return line
def rewrite_statement(node: ast.AST):
    line = ast.unparse(node)

    # strip off the line number if present

    line_no_str = None
    if line_no_match := re_line_no_prefix.match(line):
        line_no_str = line_no_match.group(1)
        line = line[line_no_match.end():]
    elif tuple_line_match := re_tuple_line_no.fullmatch(line):
        line_no_str = tuple_line_match.group(1)
        line = line[tuple_line_match.end(1)+1:-1]


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
        line = line[4:]
        var_list = re.findall(r'[A-Z][0-9A-Z]*', line)
        dim_list = re.findall(r'\([1-9][0-9]*\)', line)
        assert len(var_list) == len(dim_list)
        var_str = ','.join(var_list)
        dim_str = ','.join(f'[0]*{x}' for x in dim_list)
        new_line = var_str + '=' + dim_str
    elif match := re_assign.fullmatch(line):
        # TODO: Translate assignment RHS?
        new_line = line
    elif match := re_input_var.fullmatch(line):
        if match[2]:
            new_line = f"print('{match[2]}', end=' ');{match[3]} = input()"
        else:
            new_line = f'{match[3]} = input()'
    elif match := re_if_stmt.fullmatch(line):
        exp = match.group('expr')
        stmt = match.group('stmt')
        exp = rewrite_expression(exp)
        if line_no := re_line_no.fullmatch(stmt):
            stmt = f'GOTO.{line_no[0]}'
        new_line = f'if {exp}:\n    {stmt}'
    else:
        raise Exception("Don't know this line: "+line)

    print('NL',new_line)
    new_module = ast.parse(new_line, __name__, mode='exec')
    new_nodes = new_module.body
    for new_node in new_nodes:
        ast.copy_location(new_node, node)
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
    nodes = []
    for statement in fn.body:
        print('!',ast.unparse(statement))
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

    module_code = compile(root, fn.__code__.co_filename, mode='exec')
    function_code = module_code.co_consts[0]  # The function is the first thing in the "module"
    return types.FunctionType(function_code, fn.__globals__)


class auto_input:
    def __init__(self, text: str):
        self.buffer = io.StringIO(text)

    def __enter__(self):
        self.old_stdin = sys.stdin
        sys.stdin = self.buffer

    def __exit__(self, *_):
        sys.stdin = self.old_stdin


# @basic
def prnt():
    _10. PRINT
    #print()
    #_20. PRINT("here")

#@basic
def print_here():
    #_10. PRINT("HERE")
    #_20 .PRINT
    #_30 .PRINT("THERE")
    #_40 .PRINT;PRINT("CHAIN")
    PRINT('F'._);PRINT('G')

    _30. DIM.A1(6),A(3),B(3)
    _40. RANDOMIZE;Y=0;T=255
    _70. INPUT("Y/N").AS
    _90. IF(LEFT(AS, 1) == "N").THEN._150
    #_150. FOR.I=1, TO, 3


#@basic
def b2():
    _30. DIM.A1(6), A(3), B(3)
    _40. RANDOMIZE;Y = 0;T = 255
    _70. INPUT("Y/N"); AS
    _90. IF.AS = "NO".THEN._150
    _150. FOR.I = 1, TO, 3
    _160. A[I] = INT(10 * RND)
    _165. IF(I - 1 == 0).THEN._200
    _170. FOR.J = 1, TO, I - 1
    _180. IF.A[i] = A[j].THEN._160
    _190. NEXT.J
    _200. NEXT.I
    _210. PRINT;PRINT("O.K.  I HAVE A NUMBER IN MIND")
    _220. FOR.I = 1, TO, 20
    _295. GOTO._320




#prnt()
#with auto_input("Y\n"):
#    print_here()