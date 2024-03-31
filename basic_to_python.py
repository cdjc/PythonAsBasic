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
])

StrFunction = Enum('StrFunction', [
    'ASC',
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
        if line[:2] in ('<>'):
            rval.append(Token(tok_type=Type.Symbol,
                              str_value=line[:2],
                              num_value=None))
            line = line[2:]
            continue
        # single letter symbols
        if line[0] in "()+-*/=<>;,": #"('(',')','+','-','*','/','=',';',','):
            rval.append(Token(tok_type=Type.Symbol,
                              str_value=line[0],
                              num_value=None))
            line = line[1:]
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
            rval.append(Token(tok_type=Type.Variable,
                              str_value=var_match.group(),
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

def translate_print(tokens: list[Token]) -> str:
    '''
    PRINT statement. Options:
    PRINT
    PRINT "FOO"
    PRINT "GUESS #";I,    (; joins with a space and supresses new line at the end)
    a trailing comma jumps to next TAB stop (every 10 chars on C64 I think: https://www.c64-wiki.com/wiki/PRINT ).
    '''
    rval = 'PRINT('
    element_count = 0
    in_expression = False
    no_new_line = tokens[-1].tok_type == Type.Symbol and tokens[-1].str_value in ',;'
    if no_new_line:
        tokens = tokens[:-1]  # strip the trailing comma
    for i, token in enumerate(tokens):
        if i == 0:
            assert token.tok_type == Type.Keyword and token.str_value == Keyword.PRINT.name
            continue
        elif token.tok_type == Type.String:
            # if element_count > 0:
            #     rval += " + "
            rval += '"'+token.str_value+'"'
            in_expression = False
            element_count += 1
            continue
        elif token.tok_type == Type.Symbol and token.str_value == ';':
            if in_expression:
                rval += ')'
                in_expression = False
            rval += ", "
            continue
        else:
            if not in_expression:
                in_expression = True
                element_count += 1
            rval += token.str_value

    if no_new_line:
        rval += '._'
    # if element_count > 1:
    #     rval += ', sep=" "'
    rval += ')'
    #print('#######', rval)
    return rval

def translate_dim(tokens: list[Token]) -> str:
    '''
    DIM A1(6),A(3),B(3)
    becomes
    DIM.A1(6), A(3), B(3)
    '''
    rval = 'DIM.'
    rval += ''.join([x.str_value for x in tokens[1:]])
    arrays_set.update([x.str_value for x in tokens[1:] if x.tok_type == Type.Variable])
    #print(arrays_set)
    #print(tokens)
    return rval

def translate_tokens(tokens: list[Token]) -> str:
    rval = ''
    for i, token in enumerate(tokens):
        # line number
        if i == 0 and tokens[0].tok_type == Type.Integer:
            rval += '_'+tokens[0].str_value+". "
            continue
        elif token.tok_type == Type.Keyword and token.str_value == Keyword.PRINT.name:
            rval += translate_print(tokens[i:])
            break
        elif token.tok_type == Type.Comment:
            rval += "REM # "+token.str_value
            break
        elif token.tok_type == Type.Keyword and token.str_value == Keyword.DIM.name:
            rval += translate_dim(tokens[i:])
            break
        else:
            print(tokens)
            break
    return rval


def translate_basic_line(raw_line: str) -> list[str]:
    tokens = tokenise(raw_line)

    token_lines = separate_token_lines(tokens)
    for line in token_lines:
        #print(line)
        new_line = translate_tokens(line)


def read_basic(basic_lines: list[str]) -> list[str]:
    rval = []
    for line in basic_lines:
        translate_basic_line(line)
    return []



if __name__ == '__main__':
    #tokenise('5 PRINT TAB(33);"BAGELS"')
    read_basic(open("bagels.bas").readlines())
    print("Hello")