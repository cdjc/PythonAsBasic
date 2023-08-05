import ast
import inspect
import types
from typing import Callable, Union


class UnexpectedASTNode(Exception):

    def __init__(self, node: ast.AST, expected: type):
        super().__init__(f"Expected {expected.__name__} but got {node.__class__.__name__}")


def isASTNodeType(node: ast.AST, expected: type):
    return isinstance(node, expected)


def checkASTNodeType(node: ast.AST, expected: type):
    if not isASTNodeType(node, expected):
        raise UnexpectedASTNode(node, expected)


isModule = lambda n: isASTNodeType(n, ast.Module)
checkModule = lambda n: checkASTNodeType(n, ast.Module)
isFunctionDef = lambda n: isASTNodeType(n, ast.FunctionDef)
checkFunctionDef = lambda n: checkASTNodeType(n, ast.FunctionDef)
isExpr = lambda n: isASTNodeType(n, ast.Expr)
checkExpr = lambda n: checkASTNodeType(n, ast.Expr)


def process_basic_statement(node: Union[ast.Expr, ast.Assign]):

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
    for statement in fn.body:
        process_basic_statement(statement)


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
def smoke_test():
    return True


#@basic
def prnt():
    _10.PRINT("here")

@basic
def b2():
    _30.DIM.A1(6), A(3), B(3)
    _40.RANDOMIZE;
    Y = 0;
    T = 255
    _70.INPUT("Y/N"), AS
    _90.IF(AS == "NO").THEN._150
    _150.FOR.I = 1, TO, 3
    _160.A[I] = INT(10 * RND)
    _170.FOR.J = 1, TO, I - 1
    _180.IF(A[i] == A[j]).THEN._160
    _190.NEXT.J
    _200.NEXT.I
    _210.PRINT;
    PRINT("O.K.  I HAVE A NUMBER IN MIND")
    _220.FOR.I = 1, TO, 20


print('smoke_test pass:', smoke_test())
prnt()
