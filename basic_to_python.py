#!/usr/bin/env python3
import sys
from dataclasses import dataclass
from enum import Enum, auto
import re

class Type(Enum):
    String = auto()
    Integer = auto()
    Float = auto()
    Variable = auto()
    Keyword = auto()
    Function = auto()
    Symbol = auto()
    Separator = auto()
    Comment = auto()


IntFunction = Enum('IntFunction', [
    'TAB',
    'INT',
    'RND',
    'LEN',
    'ASC'
])

StrFunction = Enum('StrFunction', [
    'LEFT',
    'MID',
])

class Keyword(Enum):
    PRINT = auto()
    IF = auto()
    THEN = auto()
    FOR = auto()
    TO = auto()
    STEP = auto()
    NEXT = auto()
    DIM = auto()
    INPUT = auto()
    GOTO = auto()
    END = auto()
    STOP = auto()


int_function_dict = {x.name:x.value for x in IntFunction}
str_function_dict = {x.name:x.value for x in StrFunction}
keyword_dict = {x.name:x.value for x in Keyword}

arrays_set = set()  # set for remembering arrays. TODO: Only 1 dimension allowed for now

@dataclass
class Token:
    tok_type: Type
    str_value: str
    num_value: int or float

    def __repr__(self):
        return f"{self.tok_type.name}: {self.str_value}"


def tokenise(line: str) -> list[Token]:
    # Keep chopping bits off the front of the line that we recognise until gone
    rval = []
    while line:
        #print(rval)
        ws = re.match(r'\s+', line)
        if ws is not None:
            line = line[ws.end():]
            continue

        digits = re.match(r'\d+', line)
        if digits is not None:
            rval.append(Token(tok_type=Type.Integer,
                              str_value=digits.group(),
                              num_value=int(digits.group())))
            line = line[digits.end():]
            continue

        word_match = re.match(r'[A-Z]+', line)
        if word_match is not None:
            word = word_match.group()
            # could be a keyword or a variable
            # string variables/functions end with a $

            # first check functions
            if word in int_function_dict:
                rval.append(Token(tok_type=Type.Function,
                                  str_value=word,
                                  num_value=None))
                line = line[word_match.end():]
                continue
            elif word in str_function_dict:
                rval.append(Token(tok_type=Type.Function,
                                  str_value=word,
                                  num_value=None))
                # Add 1 for the $ at the end of these functions
                line = line[word_match.end() + 1:]
                continue
            elif word in keyword_dict:
                rval.append(Token(tok_type=Type.Keyword,
                                  str_value=word,
                                  num_value=None))
                line = line[word_match.end():]
                continue
        # 2-letter symbols (has to be done before single-letter symbols
        if line[:2] in ('<>',):
            rval.append(Token(tok_type=Type.Symbol,
                              str_value='!=',  # translate <> to !=
                              num_value=None))
            line = line[2:]
            continue
        # single letter symbols
        if line[0] in "()+-*/=<>;,": #"('(',')','+','-','*','/','=',';',','):
            str_value = line[0]
            # could be double symbol: "<=" or ">="
            if line[:2] in ('<=', '<='):
                str_value = line[:2]
            rval.append(Token(tok_type=Type.Symbol,
                              str_value=str_value,
                              num_value=None))
            line = line[len(str_value):]  # chop off however much we took for the token.
            continue

        str_match = re.match(r'"[^"]*"', line)
        if str_match is not None:
            rval.append(Token(tok_type=Type.String,
                              str_value=str_match.group()[1:-1],
                              num_value=None))
            line = line[str_match.end():]
            continue

        if line[0] == ':':
            rval.append(Token(tok_type=Type.Separator,
                              str_value=line[0],
                              num_value=None))
            line = line[1:]
            continue

        if line.startswith('REM'):
            rval.append(Token(tok_type=Type.Comment,
                              str_value=line[3:].rstrip(),
                              num_value=None))
            line = ""
            continue

        # variables are 1 or 3 chars. second maybe a number. strings are followed by $
        # e.g. A A1 AA A1$
        # "TO" and "IF" will be matched higher up

        var_match = re.match(r'[A-Z][A-Z0-9]?\$?', line)
        if var_match is not None:
            variable = var_match.group()
            if variable.endswith('$'):
                variable = variable[:-1]+"str"
            rval.append(Token(tok_type=Type.Variable,
                              str_value=variable,
                              num_value=None))
            line = line[var_match.end():]
            continue

        print("Unknown tokens:", line)
        sys.exit(1)

    return rval


def separate_token_lines(tokens):
    lines = [[]]
    line_index = 0
    for token in tokens:
        if token.tok_type == Type.Separator:
            lines.append([])
        else:
            lines[-1].append(token)
    return lines


class TranslationError(ValueError):
    pass


def translate_print(tokens: list[Token]) -> str:
    """
    PRINT statement. Options:
    PRINT
    PRINT "FOO"
    PRINT "GUESS #";I,    (; joins with a space and supresses new line at the end)
    PRINT "FOO" N         ( space joins chars e.g. 23matches.bas line 270)
    a trailing comma jumps to next TAB stop (every 10 chars on C64 I think: https://www.c64-wiki.com/wiki/PRINT ).
    """
    #print(tokens)
    rval = 'PRINT('
    no_new_line = tokens[-1].tok_type == Type.Symbol and tokens[-1].str_value in ',;'
    if no_new_line:
        tokens = tokens[:-1]  # strip the trailing comma
    prev_is_string = False
    for i, token in enumerate(tokens):
        if i == 0:
            assert token.tok_type == Type.Keyword and token.str_value == Keyword.PRINT.name
            continue
        elif token.tok_type == Type.String:
            # if the previous token is not PRINT or ; then it might be a space and we insert ,
            prev_token = tokens[i-1]
            if not (prev_token.str_value == Keyword.PRINT.name or prev_token.str_value == ';'):
                rval += ','
            rval += '"'+token.str_value+'"'
            prev_is_string = True
            continue
        elif token.tok_type == Type.Symbol and token.str_value == ';':
            rval += ","
            prev_is_string = False
            continue
        else:
            if prev_is_string:
                # Could be space instead of ; like 23matches.bas line 270
                rval += ','
            rval += token.str_value

    if no_new_line:
        rval += '._'
    rval += ')'
    # If it's just a bare print, then we should remove the ()
    if rval == 'PRINT()':
        rval = 'PRINT'
    #print('#######', rval)
    return rval

def translate_dim(tokens: list[Token]) -> str:
    """
    DIM A1(6),A(3),B(3)
    becomes
    DIM.A1(6), A(3), B(3)
    """
    assert tokens[0].str_value == "DIM"
    rval = 'DIM.'
    rval += ''.join([x.str_value for x in tokens[1:]])
    arrays_set.update([x.str_value for x in tokens[1:] if x.tok_type == Type.Variable])
    #print(arrays_set)
    #print(tokens)
    return rval

def translate_input(tokens: list[Token]) -> str:
    """
    Examples:
    INPUT "WOULD YOU LIKE THE RULES (YES OR NO)";A$
    INPUT A$
    TODO: Variables can be separated by comma.
    """
    assert tokens[0].str_value == "INPUT"
    seen_str = False
    rval = 'INPUT'
    for i, token in enumerate(tokens[1:]):
        if token.tok_type == Type.String and i == 0:
            rval += ('("'+tokens[1].str_value+'")')
            seen_str = True
        elif token.tok_type == Type.Symbol and i == 1 and token.str_value == ';':
            continue
        elif token.tok_type == Type.Variable and i in (0,2):
            rval += ('.'+token.str_value)
        else:
            raise TranslationError("Could not translate:"+str(tokens))
    return rval

def translate_if(tokens: list[Token]) -> str:
    """
    Examples
    simple goto:
    IF(LEFT(AS, 1) == "N").THEN._150
    multi statement after THEN or nested (superstartrek.bas) TODO: do it
    IFS+E>10THENIFE>10ORD(7)=0THEN2060

    To find the 'problem' THENs:
    $ grep -o -e "THEN[^[:cntrl:]]*" *.bas | grep -v -e 'THEN \?[0-9]'
    """
    assert tokens[0].str_value == "IF"

    # Everything between the IF and the THEN must be converted to IF(y...).THEN

    tokens = fix_array_parens(tokens)

    rval = ''
    seen_then = False
    #print(tokens)
    for token in tokens:
        if seen_then:
            if token.tok_type != Type.Integer:
                # TODO For now, assume there's only a number after the THEN.
                raise TranslationError("Non numerical THENs not yet implemented")
            rval += '_'+token.str_value
            return rval
        if token.str_value == Keyword.IF.name:
            rval += 'IF('
            continue
        if token.str_value == Keyword.THEN.name:
            rval += ').THEN.'
            seen_then = True
            continue
        # change equals comparisons: = -> ==. The <> to != conversion has already been done.
        if token.tok_type == Type.Symbol:
            if token.str_value == '=':
                rval += '=='
                continue
        # add double quotes to a string
        if token.tok_type == Type.String:
            rval += '"'+token.str_value+'"'
            continue
        rval += token.str_value

    # We didn't see the final number
    raise SyntaxError("Missing number after THEN")

def fix_array_parens(tokens: list[Token]) -> list[Token]:
    """
    Go through the tokens and fix A(X) to A[X]

    Arrays are uniquely identified by a variable followed by a parenthesis
    """
    # loop through the tokens and find all array parens and convert to '[' or ']'
    # The index of the array could be an expression and have parenthetical expressions (or other arrays)
    # Consider something like A(5+B(C+(2*3)-1)+Z(5)) = 0 # A B and Z are arrays.

    stack = []
    could_be_array = False
    for i, token in enumerate(list(tokens)):
        if token.tok_type == Type.Variable:
            could_be_array = True
        elif token.str_value == '(':
            if could_be_array:
                stack.append('[')
                tokens[i].str_value = '['  # Change token list for array
                could_be_array = False
            else:
                stack.append('(')  # not an array
        elif token.str_value == ')':  # could be close paren or close array
            if not stack:
                raise SyntaxError("Too many close parentheses: TODO. Add tokens here")
            open_paren = stack.pop()
            if open_paren == '[':
                # is close of the array.
                tokens[i].str_value = ']'
        else:
            could_be_array = False
    if stack:
        raise SyntaxError("Not enough close parentheses. TODO. Add tokens here")

    return tokens


def translate_assignment(tokens: list[Token]) -> str:
    """
    Examples
    A=5
    D=D+1
    A(I)=INT(10*RND(1))
    B(J)=A1(J)-48

    """

    tokens = fix_array_parens(tokens)
    return ''.join(t.str_value for t in tokens)

def translate_for(tokens: list[Token]) -> str:
    """
    Examples:

    FOR I=1 TO 3
    FOR J=1 TO I-1

    TODO: Add STEP
    """

    assert tokens[0].str_value == Keyword.FOR.name

    # Add . after FOR, add commas before and after TO
    rval = ''
    for token in tokens:
        if token.tok_type == Type.Keyword and token.str_value == Keyword.FOR.name:
            rval += 'FOR.'
            continue
        if token.tok_type == Type.Keyword and token.str_value == Keyword.TO.name:
            rval += ',TO,'
            continue
        rval += token.str_value
    return rval

def translate_next(tokens: list[Token]) -> str:
    """
    Could be a bare NEXT

    Examples:
    NEXT I
    NEXT
    """

    assert tokens[0].str_value == Keyword.NEXT.name
    if len(tokens) == 1:
        return 'NEXT'
    elif len(tokens) == 2:
        return 'NEXT.'+tokens[1].str_value
    raise SyntaxError('Too many tokens after NEXT')

def translate_goto(tokens: list[Token]) -> str:
    """
    Standard GOTO.

    TODO: Does not support computed gotos: ("ON X GOTO 200,300,400")
    See computed gotos with $ grep -e 'ON[^\"]*GOTO' *.bas
    21/106 programs have computed goto.
    """
    assert tokens[0].str_value == Keyword.GOTO.name
    if len(tokens) != 2:
        raise SyntaxError('Malformed GOTO')
    return 'GOTO._'+tokens[1].str_value

def translate_tokens(tokens: list[Token]) -> str:
    rval = ''
    i = 0
    if tokens[0].tok_type == Type.Integer:  # line number
        rval += '_'+tokens[0].str_value+". "
        i = 1
        if len(tokens) == 1:
            raise SyntaxError('Line number with no line')
    token = tokens[i]
    if token.tok_type == Type.Keyword:
        if token.str_value == Keyword.PRINT.name:
            rval += translate_print(tokens[i:])
        elif token.str_value == Keyword.DIM.name:
            rval += translate_dim(tokens[i:])
        elif token.str_value == Keyword.INPUT.name:
            rval += translate_input(tokens[i:])
        elif token.str_value == Keyword.IF.name:
            rval += translate_if(tokens[i:])
        elif token.str_value == Keyword.FOR.name:
            rval += translate_for(tokens[i:])
        elif token.str_value == Keyword.NEXT.name:
            rval += translate_next(tokens[i:])
        elif token.str_value == Keyword.GOTO.name:
            rval += translate_goto(tokens[i:])
        elif token.str_value == Keyword.END.name or token.str_value == Keyword.STOP.name:
            rval += token.str_value
        else:
            raise SyntaxError('Unknown keyword: '+token.str_value)
    elif token.tok_type == Type.Comment:
        if token.str_value:
            rval += "REM #"+token.str_value
        else:
            rval += 'REM'
    elif token.tok_type == Type.Variable:  # assignment
        rval += translate_assignment(tokens[i:])
    else:
        raise SyntaxError('Unrecognised token: ' + token.str_value)
    return rval


def translate_basic_line(raw_line: str) -> list[str]:
    lines = []
    tokens = tokenise(raw_line)

    token_lines = separate_token_lines(tokens)
    for line in token_lines:
        #print(line)
        lines.append(translate_tokens(line))
    return lines

def read_basic(basic_lines: list[str]) -> list[str]:
    rval = []
    for line in basic_lines:
        rval.extend(translate_basic_line(line))
    return rval

def translate_file(fname: str) -> None:
    """
    Read a .bas file and produce a corresponding PythonAsBasic .bas.py file
    """

    header = '''# Autogenerated code. Do not edit.
from basic import basic
from basic_functions import *

@basic
def {name}():
    '''

    footer = '''

if __name__ == '__main__':
    {name}()
    '''

    lines = read_basic(open(fname).readlines())
    # I'm happy with foo.bas.py as a filename
    # It's less likely to be confused with a real python file.
    pyname = fname+'.py'
    func_name = fname.split('.')[0]
    func_name = 'basic_'+func_name  # some files start with a digit
    with open(pyname,'w') as fid:
        print(header.format(name=func_name), file=fid)
        for line in lines:
            print('    '+line, file=fid)
        print(footer.format(name=func_name), file=fid)

if __name__ == '__main__':
    #tokenise('5 PRINT TAB(33);"BAGELS"')
    #lines = read_basic(open("bagels.bas").readlines())
    #for line in lines:
    #    print(line)
    #print("Hello")
    translate_file('23matches.bas')