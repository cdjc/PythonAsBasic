import unittest
from basic import basic
import io
import sys

import contextlib

contextlib.redirect_stdout
class auto_inout:
    def __init__(self, text: str = ''):
        self.in_buffer = io.StringIO(text)
        self.out_buffer = io.StringIO()

    def __enter__(self):
        self.old_stdin = sys.stdin
        sys.stdin = self.in_buffer
        self.old_stdout = sys.stdout
        sys.stdout = self.out_buffer
        return self.out_buffer

    def __exit__(self, *_):
        sys.stdin = self.old_stdin
        sys.stdout = self.old_stdout



class PrintTests(unittest.TestCase):

    def test_print_bare(self):

        @basic
        def print_bare():
            _10. PRINT

        with auto_inout() as f:
            print_bare()

        self.assertEqual('\n', f.getvalue())

    def test_print_string(self):

        @basic
        def print_string():
            _10.PRINT("foo")

        with auto_inout() as f:
            print_string()

        self.assertEqual('foo\n', f.getvalue())

    def test_print_no_newline(self):

        @basic
        def print_string():
            _10.PRINT("foo"._)

        with auto_inout() as f:
            print_string()

        self.assertEqual('foo', f.getvalue())


    def test_print_num(self):

        @basic
        def print_num():
            _20. PRINT(5)

        with auto_inout() as f:
            print_num()

        self.assertEqual('5\n', f.getvalue())

    def test_print_var(self):

        @basic
        def print_var():
            _10. A = 5
            _20. PRINT(A)

        with auto_inout() as f:
            print_var()

        self.assertEqual('5\n', f.getvalue())

class InputTests(unittest.TestCase):

    def test_input_bare(self):

        @basic
        def input_bare():
            _5. INPUT.A
            _10. PRINT(A)

        with auto_inout('in1') as f:
            input_bare()

        self.assertEqual('in1\n', f.getvalue())

    def test_input_prompt(self):

        @basic
        def input_bare():
            _5. INPUT('One').A
            _10. PRINT(A)

        with auto_inout('Two') as f:
            input_bare()

        self.assertEqual('One Two\n', f.getvalue())


class IfTests(unittest.TestCase):

    def test_if(self):

        @basic
        def if_stmt():
            _10. A = 4
            _20. IF(A == 4).THEN._40
            _30. A = 3
            _40. PRINT(A._)

        with auto_inout() as f:
            if_stmt()

        self.assertEqual('4', f.getvalue())

if __name__ == '__main__':
    unittest.main()
