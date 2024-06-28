import unittest
from basic import basic
import io
import sys

from basic_to_python import *
class TestTranslate(unittest.TestCase):

    def test_input(self):

        self.assertEqual("INPUT.Astr", translate_input(tokenise("INPUT A$")))
        self.assertEqual('INPUT("FOO").Astr', translate_input(tokenise('INPUT "FOO";A$')))

    def test_vars(self):
        self.assertEqual("A=5", translate_assignment(tokenise("A=5")))
        self.assertEqual("A[I]=INT(10*RND(1))", translate_assignment(tokenise("A(I)=INT(10*RND(1))")))
        self.assertEqual("A[5+B[C+(2*3)-1]+Z[5]]=0", translate_assignment(tokenise("A(5+B(C+(2*3)-1)+Z(5)) = 0")))
        with self.assertRaises(SyntaxError):
            translate_assignment(tokenise("A=(5))"))
        with self.assertRaises(SyntaxError):
            translate_assignment(tokenise("A=(5"))


if __name__ == '__main__':
    unittest.main()