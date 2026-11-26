//// Box.asm -- K = 64
// Start row = 64 -> SCREEN + 32*64 = 18432
// Width = 16 * ((64 mod 4) + 1) = 16 pixels = 1 word
// Height = 20 rows

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE
    @color
    M=0
    @DRAW
    0;JMP
(BLACK)
    @color
    M=-1
(DRAW)
    @18432
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D
(ROWLOOP)
    @1
    D=A
    @cols
    M=D
    @addr
    D=M
    @p
    M=D
(COLLOOP)
    @color
    D=M
    @p
    A=M
    M=D
    @p
    M=M+1
    @cols
    M=M-1
    D=M
    @COLLOOP
    D;JGT
    @32
    D=A
    @addr
    M=D+M
    @rows
    MD=M-1
    @ROWLOOP
    D;JGT
    @LOOP
    0;JMP