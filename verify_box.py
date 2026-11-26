code=[int(l,2) for l in open('Box.hack').read().split()]
def run(key):
    ram=[0]*32768; ram[24576]=key
    # preload screen with garbage to test clearing
    for i in range(16384,24576): ram[i]=-1 if key==0 else 0
    A=D=pc=0
    def s(x): x&=0xffff; return x-65536 if x&0x8000 else x
    for _ in range(20000):
        if pc>=len(code): break
        i=code[pc]
        if not i&0x8000: A=i; pc+=1; continue
        a=(i>>12)&1; c=(i>>6)&0x3f; d=(i>>3)&7; j=i&7
        y=ram[A] if a else A
        t={0b101010:0,0b111111:1,0b111010:-1,0b001100:D,0b110000:y,0b001101:~D,0b110001:~y,0b001111:-D,0b110011:-y,0b011111:D+1,0b110111:y+1,0b001110:D-1,0b110010:y-1,0b000010:D+y,0b010011:D-y,0b000111:y-D,0b000000:D&y,0b010101:D|y}[c]
        t=s(t)
        oldA=A
        if d&1: ram[oldA]=t
        if d&2: D=t
        if d&4: A=t&0x7fff if False else t&0xffff
        jmp=(j&4 and t<0) or (j&2 and t==0) or (j&1 and t>0)
        pc=oldA if jmp else pc+1
    return ram
for key in (65,0):
    r=run(key)
    words=[i-16384 for i in range(16384,24576) if r[i]!=0]
    rows=sorted({w//32 for w in words}); cols=sorted({w%32 for w in words})
    print("key",key,"-> rows",(rows[0],rows[-1]) if rows else None,"cols",cols,"count",len(words))