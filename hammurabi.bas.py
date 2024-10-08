# Autogenerated code. DO NOT EDIT.
# Generated using basic_to_python.py at 2024-07-06T17:17:19.384298+12:00

from basic import basic
from basic_functions import *

@basic
def basic_hammurabi():
    
    _10. PRINT(TAB(32),"HAMURABI")
    _20. PRINT(TAB(15),"CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
    _30. PRINT
    PRINT
    PRINT
    _80. PRINT("TRY YOUR HAND AT GOVERNING ANCIENT SUMERIA")
    _90. PRINT("FOR A TEN-YEAR TERM OF OFFICE.")
    PRINT
    _95. D1=0
    P1=0
    _100. Z=0
    P=95
    S=2800
    H=3000
    E=H-S
    _110. Y=3
    A=H/Y
    I=5
    Q=1
    _210. D=0
    _215. PRINT
    PRINT
    PRINT("HAMURABI:  I BEG TO REPORT TO YOU,")
    Z=Z+1
    _217. PRINT("IN YEAR",Z,",",D,"PEOPLE STARVED,",I,"CAME TO THE CITY,")
    _218. P=P+I
    _227. IF(Q>0).THEN._230
    _228. P=INT(P/2)
    _229. PRINT("A HORRIBLE PLAGUE STRUCK!  HALF THE PEOPLE DIED.")
    _230. PRINT("POPULATION IS NOW",P)
    _232. PRINT("THE CITY NOW OWNS ",A,"ACRES.")
    _235. PRINT("YOU HARVESTED",Y,"BUSHELS PER ACRE.")
    _250. PRINT("THE RATS ATE",E,"BUSHELS.")
    _260. PRINT("YOU NOW HAVE ",S,"BUSHELS IN STORE.")
    PRINT
    _270. IF(Z==11).THEN._860
    _310. C=INT(10*RND(1))
    Y=C+17
    _312. PRINT("LAND IS TRADING AT",Y,"BUSHELS PER ACRE.")
    _320. PRINT("HOW MANY ACRES DO YOU WISH TO BUY"._)
    _321. INPUT.Q
    IF(Q<0).THEN._850
    _322. IF(Y*Q<=S).THEN._330
    _323. GOSUB._710
    _324. GOTO._320
    _330. IF(Q==0).THEN._340
    _331. A=A+Q
    S=S-Y*Q
    C=0
    _334. GOTO._400
    _340. PRINT("HOW MANY ACRES DO YOU WISH TO SELL"._)
    _341. INPUT.Q
    IF(Q<0).THEN._850
    _342. IF(Q<A).THEN._350
    _343. GOSUB._720
    _344. GOTO._340
    _350. A=A-Q
    S=S+Y*Q
    C=0
    _400. PRINT
    _410. PRINT("HOW MANY BUSHELS DO YOU WISH TO FEED YOUR PEOPLE"._)
    _411. INPUT.Q
    _412. IF(Q<0).THEN._850
    _418. REM # *** TRYING TO USE MORE GRAIN THAN IS IN SILOS?
    _420. IF(Q<=S).THEN._430
    _421. GOSUB._710
    _422. GOTO._410
    _430. S=S-Q
    C=1
    PRINT
    _440. PRINT("HOW MANY ACRES DO YOU WISH TO PLANT WITH SEED"._)
    _441. INPUT.D
    IF(D==0).THEN._511
    _442. IF(D<0).THEN._850
    _444. REM # *** TRYING TO PLANT MORE ACRES THAN YOU OWN?
    _445. IF(D<=A).THEN._450
    _446. GOSUB._720
    _447. GOTO._440
    _449. REM # *** ENOUGH GRAIN FOR SEED?
    _450. IF(INT(D/2)<=S).THEN._455
    _452. GOSUB._710
    _453. GOTO._440
    _454. REM # *** ENOUGH PEOPLE TO TEND THE CROPS?
    _455. IF(D<10*P).THEN._510
    _460. PRINT("BUT YOU HAVE ONLY",P,"PEOPLE TO TEND THE FIELDS!  NOW THEN,")
    _470. GOTO._440
    _510. S=S-INT(D/2)
    _511. GOSUB._800
    _512. REM # *** A BOUNTIFUL HARVEST!
    _515. Y=C
    H=D*Y
    E=0
    _521. GOSUB._800
    _522. IF(INT(C/2)!=C/2).THEN._530
    _523. REM # *** RATS ARE RUNNING WILD!!
    _525. E=INT(S/C)
    _530. S=S-E+H
    _531. GOSUB._800
    _532. REM # *** LET'S HAVE SOME BABIES
    _533. I=INT(C*(20*A+S)/P/100+1)
    _539. REM # *** HOW MANY PEOPLE HAD FULL TUMMIES?
    _540. C=INT(Q/20)
    _541. REM # *** HORROS, A 15% CHANCE OF PLAGUE
    _542. Q=INT(10*(2*RND(1)-.3))
    _550. IF(P<C).THEN._210
    _551. REM # *** STARVE ENOUGH FOR IMPEACHMENT?
    _552. D=P-C
    IF(D>.45*P).THEN._560
    _553. P1=((Z-1)*P1+D*100/P)/Z
    _555. P=C
    D1=D1+D
    GOTO._215
    _560. PRINT
    PRINT("YOU STARVED",D,"PEOPLE IN ONE YEAR!!!")
    _565. PRINT("DUE TO THIS EXTREME MISMANAGEMENT YOU HAVE NOT ONLY")
    _566. PRINT("BEEN IMPEACHED AND THROWN OUT OF OFFICE BUT YOU HAVE")
    _567. PRINT("ALSO BEEN DECLARED NATIONAL FINK!!!!")
    GOTO._990
    _710. PRINT("HAMURABI:  THINK AGAIN.  YOU HAVE ONLY")
    _711. PRINT(S,"BUSHELS OF GRAIN.  NOW THEN,")
    _712. RETURN
    _720. PRINT("HAMURABI:  THINK AGAIN.  YOU OWN ONLY",A,"ACRES.  NOW THEN,")
    _730. RETURN
    _800. C=INT(RND(1)*5)+1
    _801. RETURN
    _850. PRINT
    PRINT("HAMURABI:  I CANNOT DO WHAT YOU WISH.")
    _855. PRINT("GET YOURSELF ANOTHER STEWARD!!!!!")
    _857. GOTO._990
    _860. PRINT("IN YOUR 10-YEAR TERM OF OFFICE,",P1,"PERCENT OF THE")
    _862. PRINT("POPULATION STARVED PER YEAR ON THE AVERAGE, I.E. A TOTAL OF")
    _865. PRINT(D1,"PEOPLE DIED!!")
    L=A/P
    _870. PRINT("YOU STARTED WITH 10 ACRES PER PERSON AND ENDED WITH")
    _875. PRINT(L,"ACRES PER PERSON.")
    PRINT
    _880. IF(P1>33).THEN._565
    _885. IF(L<7).THEN._565
    _890. IF(P1>10).THEN._940
    _892. IF(L<9).THEN._940
    _895. IF(P1>3).THEN._960
    _896. IF(L<10).THEN._960
    _900. PRINT("A FANTASTIC PERFORMANCE!!!  CHARLEMANGE, DISRAELI, AND")
    _905. PRINT("JEFFERSON COMBINED COULD NOT HAVE DONE BETTER!")
    GOTO._990
    _940. PRINT("YOUR HEAVY-HANDED PERFORMANCE SMACKS OF NERO AND IVAN IV.")
    _945. PRINT("THE PEOPLE (REMIANING) FIND YOU AN UNPLEASANT RULER, AND,")
    _950. PRINT("FRANKLY, HATE YOUR GUTS!!")
    GOTO._990
    _960. PRINT("YOUR PERFORMANCE COULD HAVE BEEN SOMEWHAT BETTER, BUT")
    _965. PRINT("REALLY WASN'T TOO BAD AT ALL. ",INT(P*.8*RND(1)),"PEOPLE")
    _970. PRINT("WOULD DEARLY LIKE TO SEE YOU ASSASSINATED BUT WE ALL HAVE OUR")
    _975. PRINT("TRIVIAL PROBLEMS.")
    _990. PRINT
    FOR.N=1,TO,10
    PRINT(CHR(7)._)
    NEXT.N
    _995. PRINT("SO LONG FOR NOW.")
    PRINT
    _999. END


if __name__ == '__main__':
    basic_hammurabi()
    
