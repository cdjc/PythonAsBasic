import unittest
from basic import basic
import io
import sys

from basic_to_python import *
class TestTranslate(unittest.TestCase):

    def test_input(self):

        self.assertEqual("INPUT.Astr", translate_tokens(tokenise("INPUT A$")))
        self.assertEqual('INPUT("FOO").Astr', translate_tokens(tokenise('INPUT "FOO";A$')))

    def test_vars(self):
        self.assertEqual("A=5", translate_tokens(tokenise("A=5")))
        self.assertEqual("A[I]=INT(10*RND(1))", translate_tokens(tokenise("A(I)=INT(10*RND(1))")))
        self.assertEqual("A[5+B[C+(2*3)-1]+Z[5]]=0", translate_tokens(tokenise("A(5+B(C+(2*3)-1)+Z(5)) = 0")))
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise("A=(5))"))
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise("A=(5"))

    def test_print(self):
        self.assertEqual("PRINT", translate_tokens(tokenise("PRINT")))
        self.assertEqual('PRINT("FOO")', translate_tokens(tokenise('PRINT "FOO"')))
        self.assertEqual('PRINT("FOO",I._)', translate_tokens(tokenise('PRINT "FOO";I,')))
        self.assertEqual('PRINT("FOO",(I+J))', translate_tokens(tokenise('PRINT "FOO";(I+J)')))
        self.assertEqual('PRINT(TAB(33),"BAGELS")', translate_tokens(tokenise('PRINT TAB(33);"BAGELS"')))

    def test_dim(self):
        self.assertEqual('DIM.A(3)', translate_tokens(tokenise("DIM A(3)")))
        self.assertEqual('DIM.A(3),B1(2+3)', translate_tokens(tokenise("DIM A(3),B1(2+3)")))

    def test_if(self):
        self.assertEqual('IF(LEFT(Astr,1)=="N").THEN._150', translate_tokens(tokenise('IF LEFT$(A$,1)="N" THEN 150')))
        self.assertEqual('IF(I-1==0).THEN._200', translate_tokens(tokenise('IF I-1=0 THEN 200')))
        self.assertEqual('IF(LEN(Astr)!=3).THEN._630', translate_tokens(tokenise('IF LEN(A$)<>3 THEN 630')))
        self.assertEqual('IF(B(1)==B(2)).THEN._650', translate_tokens(tokenise('IF B(1)=B(2) THEN 650')))
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('IF B(1)=B(2) THEN'))

    def test_for(self):
        self.assertEqual('FOR.I=1,TO,3', translate_tokens(tokenise('FOR I=1 TO 3')))
        self.assertEqual('FOR.I=1+(3*Z),TO,3*Q', translate_tokens(tokenise('FOR I=1+(3*Z) TO 3*Q')))

    def test_next(self):
        self.assertEqual('NEXT', translate_tokens(tokenise('NEXT')))
        self.assertEqual('NEXT.F', translate_tokens(tokenise('NEXT F')))
        with self.assertRaises(SyntaxError):
            translate_next(tokenise('NEXT F 2'))

    def test_goto(self):
        self.assertEqual('GOTO._200', translate_tokens(tokenise('GOTO 200')))
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('GOTO'))
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('GOTO 200,400'))

    def test_end(self):
        self.assertEqual('END', translate_tokens(tokenise('END')))

    def test_bad_token(self):
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('35'))  # line num with no line
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('<'))  # bad token
        with self.assertRaises(SyntaxError):
            translate_tokens(tokenise('TO'))  # Keyword in wrong place

    def test_comment(self):
        self.assertEqual('REM # foo', translate_tokens(tokenise('REM foo')))
        self.assertEqual('REM', translate_tokens(tokenise('REM')))

if __name__ == '__main__':
    unittest.main()