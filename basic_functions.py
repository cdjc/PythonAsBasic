"""
BASIC "runtime" functions.
More or less following the semantics found at:
https://hackage.haskell.org/package/vintage-basic-1.0/src/doc/Vintage_BASIC_Users_Guide.html
"""
import random
import math


def ASC(val):
    return ord(val)


def COS(val):
    return math.cos(val)


def CHR(val):
    return chr(val)  # Can print bell (7) or backspace (10), or TAB (11)


def INT(val):
    return int(val)


def LEFT(string: str, num: int):
    return string[:num]


def LEN(val):
    return len(val)


_prev_rand_val = 0


def RND(val):
    global _prev_rand_val
    if val > 0:
        _prev_rand_val = random.random()
        return _prev_rand_val
    elif val < 0:
        random.seed(val)
    else:  # == 0
        return _prev_rand_val


def SIN(val):
    return math.sin(val)


def SGN(val):
    if val == 0:
        return 0
    elif val > 0:
        return 1
    return -1


def TAB(num: int):  # TODO: Actually, this implementation is not right
    return ' ' * num


def TAN(val):
    return math.tan(val)