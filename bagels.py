from basic import basic
from basic_functions import *

@basic
def bagels():
    _5.PRINT(TAB(33),"BAGELS")
    _30.DIM.A1(6), A(3), B(3)
    _40.Y = 0;
    T = 255
    _70.INPUT("Y/N").AS
    _90.IF(LEFT(AS, 1) == "N").THEN._150
    # _101. PRINT('PREFOR')
    _150.FOR.I = 1, TO, 3
    # _151. PRINT('FORI',I)
    _160.A[I] = INT(10 * RND(1))
    # _161. PRINT('A[I],I',A[I],I)
    _165.IF(I - 1 == 0).THEN._200
    _170.FOR.J = 1, TO, I - 1
    # _171. PRINT("J",J)
    # _172. PRINT('I,A[I],J,A[J]',I,A[I],J,A[J])
    _180.IF(A[I] == A[J]).THEN._160
    _190.NEXT.J
    _200.NEXT.I
    # _205. PRINT(A[1], A[2], A[3])
    # _220. PRINT('DONE')
    _210.PRINT;
    PRINT("O.K.  I HAVE A NUMBER IN MIND.")
    _220.FOR.I = 1, TO, 20
    _230.PRINT("GUESS #", I._)
    _240.INPUT.AS
    _245.IF(LEN(AS) != 3).THEN._630
    _250.FOR.Z = 1, TO, 3;
    A1[Z] = ASC(MID(AS, Z, 1));
    NEXT.Z
    _260.FOR.J = 1, TO, 3
    _270.IF(A1[J] < 48).THEN._300
    _280.IF(A1[J] > 57).THEN._300
    _285.B[J] = A1[J] - 48
    _290.NEXT.J
    _295.GOTO._320
    _300.PRINT("WHAT?")
    _310.GOTO._230
    _320.IF(B[1] == B[2]).THEN._650
    _330.IF(B[2] == B[3]).THEN._650
    _340.IF(B[3] == B[1]).THEN._650
    _350.C = 0;
    D = 0
    _360.FOR.J = 1, TO, 2
    _370.IF(A[J] != B[J + 1]).THEN._390
    _380.C = C + 1
    _390.IF(A[J + 1] != B[J]).THEN._410
    _400.C = C + 1
    _410.NEXT.J
    _420.IF(A[1] != B[3]).THEN._440
    _430.C = C + 1
    _440.IF(A[3] != B[1]).THEN._460
    _450.C = C + 1
    _460.FOR.J = 1, TO, 3
    _470.IF(A[J] != B[J]).THEN._490
    _480.D = D + 1
    _490.NEXT.J
    _500.IF(D == 3).THEN._680
    _505.IF(C == 0).THEN._545
    _520.FOR.J = 1, TO, C
    _530.PRINT("PICO"._)
    _540.NEXT.J
    _545.IF(D == 0).THEN._580
    _550.FOR.J = 1, TO, D
    _560.PRINT("FERMI"._)
    _570.NEXT.J
    _580.IF(C + D != 0).THEN._600
    _590.PRINT("BAGELS"._)
    _600.PRINT
    _605.NEXT.I
    _610.PRINT("OH WELL.")
    _615.PRINT("THAT'S TWENTY GUESSES.  MY NUMBER WAS", 100 * A(1) + 10 * A(2) + A(3))
    _620.GOTO._700
    _630.PRINT("TRY GUESSING A THREE-DIGIT NUMBER.");
    GOTO._230
    _650.PRINT("OH, I FORGOT TO TELL YOU THAT THE NUMBER I HAVE IN MIND")
    _660.PRINT("HAS NO TWO DIGITS THE SAME.");
    GOTO._230
    _680.PRINT("YOU GOT IT!!!");
    PRINT
    _690.Y = Y + 1
    _700.PRINT("PLAY AGAIN. TODO")


if __name__ == '__main__':
    bagels()