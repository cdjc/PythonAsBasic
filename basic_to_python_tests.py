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

    def test_print(self):
        self.assertEqual("PRINT", translate_print(tokenise("PRINT")))
        self.assertEqual('PRINT("FOO")', translate_print(tokenise('PRINT "FOO"')))
        self.assertEqual('PRINT("FOO", I._)', translate_print(tokenise('PRINT "FOO";I,')))
        self.assertEqual('PRINT("FOO", (I+J))', translate_print(tokenise('PRINT "FOO";(I+J)')))

    def test_dim(self):
        self.assertEqual('DIM.A(3)', translate_dim(tokenise("DIM A(3)")))
        self.assertEqual('DIM.A(3),B1(2+3)', translate_dim(tokenise("DIM A(3),B1(2+3)")))

if __name__ == '__main__':
    unittest.main()