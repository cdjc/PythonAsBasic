# Autogenerated code. Do not edit.
from basic import basic
from basic_functions import *

@basic
def basic_23matches():
    
    _20. PRINT(TAB(31),"23 MATCHES")
    _30. PRINT(TAB(15),"CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY")
    _40. PRINT
    PRINT
    PRINT
    _80. PRINT(" THIS IS A GAME CALLED '23 MATCHES'.")
    _90. PRINT
    _100. PRINT("WHEN IT IS YOUR TURN, YOU MAY TAKE ONE, TWO, OR THREE")
    _110. PRINT("MATCHES. THE OBJECT OF THE GAME IS NOT TO HAVE TO TAKE")
    _120. PRINT("THE LAST MATCH.")
    _130. PRINT
    _140. PRINT("LET'S FLIP A COIN TO SEE WHO GOES FIRST.")
    _150. PRINT("IF IT COMES UP HEADS, I WILL WIN THE TOSS.")
    _155. PRINT
    _160. REM
    _165. N=23
    _170. Q=INT(2*RND(5))
    _180. IF(Q==1).THEN._210
    _190. PRINT("TAILS! YOU GO FIRST. ")
    _195. PRINT
    _200. GOTO._300
    _210. PRINT("HEADS! I WIN! HA! HA!")
    _220. PRINT("PREPARE TO LOSE, MEATBALL-NOSE!!")
    _230. PRINT
    _250. PRINT("I TAKE 2 MATCHES")
    _260. N=N-2
    _270. PRINT("THE NUMBER OF MATCHES IS NOW",N)
    _280. PRINT
    _290. PRINT("YOUR TURN -- YOU MAY TAKE 1, 2 OR 3 MATCHES.")
    _300. PRINT("HOW MANY DO YOU WISH TO REMOVE"._)
    _310. INPUT.K
    _320. IF(K>3).THEN._430
    _330. IF(K<=0).THEN._430
    _340. N=N-K
    _350. PRINT("THERE ARE NOW",N,"MATCHES REMAINING.")
    _351. IF(N==4).THEN._381
    _352. IF(N==3).THEN._383
    _353. IF(N==2).THEN._385
    _360. IF(N<=1).THEN._530
    _370. Z=4-K
    _372. GOTO._390
    _380. PRINT
    _381. Z=3
    _382. GOTO._390
    _383. Z=2
    _384. GOTO._390
    _385. Z=1
    _390. PRINT("MY TURN ! I REMOVE",Z,"MATCHES")
    _400. N=N-Z
    _410. IF(N<=1).THEN._470
    _420. GOTO._270
    _430. PRINT("VERY FUNNY! DUMMY!")
    _440. PRINT("DO YOU WANT TO PLAY OR GOOF AROUND?")
    _450. PRINT("NOW, HOW MANY MATCHES DO YOU WANT"._)
    _460. GOTO._310
    _470. PRINT
    _480. PRINT("YOU POOR BOOB! YOU TOOK THE LAST MATCH! I GOTCHA!!")
    _490. PRINT("HA ! HA ! I BEAT YOU !!!")
    _500. PRINT
    _510. PRINT("GOOD BYE LOSER!")
    _520. GOTO._560
    _530. PRINT("YOU WON, FLOPPY EARS !")
    _540. PRINT("THINK YOU'RE PRETTY SMART !")
    _550. PRINT("LETS PLAY AGAIN AND I'LL BLOW YOUR SHOES OFF !!")
    _560. STOP
    _570. END


if __name__ == '__main__':
    basic_23matches()
    
