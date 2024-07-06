# test code to rewrite python function but still get error messages on
# correct line, and debugger and coverage still working.

import ast
import inspect
import types


def fn():
    print('line 1')
    print('line 2')
    #print(l)
    print('line 4')

def fix_line_nos(to_node: ast.AST, from_node: ast.AST):
    to_node.lineno = from_node.lineno
    to_node.end_lineno = from_node.end_lineno
    to_node.col_offset = from_node.col_offset
    to_node.end_col_offset = from_node.end_col_offset
    for child_node in ast.iter_child_nodes(to_node):
        fix_line_nos(child_node, to_node)



lines, lnum = inspect.getsourcelines(fn)
#s = '\n'*(lnum-1)+''.join(lines)
s = ''.join(lines)
r = ast.parse(s)
ast.increment_lineno(r, lnum-1)
print(s)
print(r)
ss = r.body[0].body
#ns = [ss[0], ss[0],ss[1],ss[2]]
ns = []
print(ss)
for node in ss:
    raw = ast.unparse(node)
    nm = ast.parse(raw, __name__, mode='exec')
    nns = nm.body
    nn = nns[0]
    #nn.value.lineno = node.value.lineno
    #nn.value.end_lineno = node.value.end_lineno
    # nn.value = node.value
    #ast.copy_location(nn, node)
    # ast.fix_missing_locations(nn)
    fix_line_nos(nn, node)
    ns.append(nn)
print(ns)
r.body[0].body = ns
m = compile(r, fn.__code__.co_filename, mode='exec')
print(m)
fn2_code = m.co_consts[0]

print(fn2_code)
fn2 = types.FunctionType(fn2_code, fn.__globals__)
# fn2.__code__.co_firstlineno = 9
print(fn2)
fn2()