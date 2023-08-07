import ast
import inspect
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
        nodes.extend(process_basic_statement(statement))
    fn.body = nodes


def basic(fn: Callable) -> Callable:
    source = inspect.getsource(fn)
    # peel off this decorator from the code.
    fn_source = source[source.find('\n') + 1:]
    root = ast.parse(fn_source)
    print(ast.dump(root, indent=' '))
    print(ast.unparse(root))

    process_statements(root)

    module_code = compile(root, fn.__code__.co_filename, mode='exec')
    function_code = module_code.co_consts[0]  # The function is the first thing in the "module"
    return types.FunctionType(function_code, fn.__globals__)


# @basic
def prnt():
    _10. PRINT
    #print()
    #_20. PRINT("here")

@basic
def print_here():
    _10. PRINT("HERE")
    _20 .PRINT
    _30 .PRINT("THERE")
    _40 .PRINT;PRINT("CHAIN")

#@basic
def b2():
    _30. DIM.A1(6), A(3), B(3)
    _40. RANDOMIZE;Y = 0;T = 255
    _70. INPUT("Y/N"); AS
    _90. IF.AS = "NO".THEN._150
    _150. FOR.I = 1, TO, 3
    _160. A[I] = INT(10 * RND)
    _170. FOR.J = 1, TO, I - 1
    _180. IF.A[i] = A[j].THEN._160
    _190. NEXT.J
    _200. NEXT.I
    _210. PRINT;PRINT("O.K.  I HAVE A NUMBER IN MIND")
    _220. FOR.I = 1, TO, 20
    _295. GOTO._320



#prnt()
print_here()