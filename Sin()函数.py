#基于risc-v指令集
#小端模式
Register = {
    #risc指令集中第零号寄存器恒存0
    0b00001 : 0x00000010,       #第一条指令基址寻址的基址寄存器
    0b00010 : 0x00000000,       #第一条指令load的目的寄存器，初始内容为0
    0b00011 : 0x00000014,       #第二条load指令基址寻址的基址寄存器
    0b00100 : 0x00000000,       #第二条load指令的目的寄存器，初始内容为0
    0b00101 : 0x00000000,       #用来存储add指令的计算结果
    0b00110 : 0x00000018        #store指令中基址寄存器

}
 
Memory = {
    #load r1, #0
    #采用基址寻址和寄存器间接寻址，通过寄存器中的内容加offset得到内存中的地址，然后去内存中取源操作数
    #load 指令为0 00 00 11
    #imm[11:0]     rs1     func3    rd      opcode
    #offset        base    width    dst     load
    #000000000000  00001   010      00010   0000011
    #imm =+0       rs1=1   lw       rd=2    load
    #0x000 0A 1 03采用小端方式存储，内容为0x03 A1 00 00
    0x00000000 : 0x03,
    0x00000001 : 0xA1,
    0x00000002 : 0x00,
    0x00000003 : 0x00,
 
    #load r2, #1
    #imm[11:0]     rs1     func3    rd      opcode
    #offset        base    width    dst     load
    #000000000000  00011   010      00100   0000011
    #imm =+0       rs1=3   lw       rd=4    load
    #0x000 1A 2 03采用小端方式存储，内容为0x03 A2 01 00
    0x00000004 : 0x03,
    0x00000005 : 0xA2,
    0x00000006 : 0x01,
    0x00000007 : 0x00,
 
    #add r3, r1, r2
    #这里r3的地址为：0b00101，r1的地址为：0b00010，r2的地址为：0b00100
    #funct7     rs2     rs1     funct3      rd      opcode
    #0000000    00100   00010   000         00101   0110011
    #其中funct7和funct3的组合表示加法运算
    #16进制表示为0x 00 41 02 B3小端模式表示为0xB3 02 41 00
    0x00000008 : 0xB3,
    0x00000009 : 0x02,
    0x0000000A : 0x41,
    0x0000000B : 0x00,
 
    #store r3, #3
    #r3为0b00101，#3采用基址寻址+间接寻址，内存起始地址为0x00000019，基址寄存器为0b00110，offset为0
    #               rs2需要存储的数据
    #                       rs1基址寄存器
    #imm[11:5]      rs2     rs1     func3       imm[4:0]        opcode
    #0000000        00101   00110   010         00000           0100011
    #其十六进制表示为0x00 53 20 23
    0x0000000C : 0x23,
    0x0000000D : 0x20,
    0x0000000E : 0x53,
    0x0000000F : 0x00,
 
    #这个内存地址用来存放第一条load指令的数据
    #令第一个加数为1：0x00000001，小端存储为0x01000000
    0x00000010 : 0x01,
    0x00000011 : 0x00,
    0x00000012 : 0x00,
    0x00000013 : 0x00,
 
    #这个内存地址用来存放第二条load指令的数据
    #令第二个加数为2：0x00000002，小端存储为0x02000000
    0x00000014 : 0x02,
    0x00000015 : 0x00,
    0x00000016 : 0x00,
    0x00000017 : 0x00,
 
    #这个内存地址用来存放store指令的数据
    #初始为0
    0x00000018 : 0x00,
    0x00000019 : 0x00,
    0x0000001A : 0x00,
    0x0000001B : 0x00
}
 
#指令类型
Instruction = {
    0b0000011 : 'load',
    0b0110011 : 'add',
    0b0100011 : 'store'
}
 
#读取指令，根据pc中的内容，读取memory中的内容，大小为四个存储单元
#读取到的内容进行解析
#大端，小端，以及左右顺序问题
#对操作码的解析：0-6，表示操作码，如何模拟查询操作？
#需要定义指令集
def defInstr(addr):#传入参数为指令在内存的地址
    instru = 0x00000000
    for i in range(4):
        #print(hex(addr + i))
        #print(hex(Memory[addr + i]))
        instru += Memory[addr + i] * (256**i)
        #print(hex(instru))
    return instru
 
def judgeType(instru):
    return Instruction[instru & 0b1111111]
 
#load指令
def load(instru):
    #offset     base        width       dst     load
    #imm[11:0]  rs1         func3       rd      opcode
    #1 找到base中的内容
    #2 base中的内容和offset相加，得到内存地址
    #3 将内存单元的内容复制到dst
    offset = instru >> 20
    rs1 = (instru >> 15) & 0b11111
    rd = (instru >> 7) & 0b11111
    Register[rd] = defInstr(Register[rs1] + offset)
 
 
#add指令
def add(instru):
    #funct7     rs2     rs1     funct3      rd      opcode
    #1 取出rs2和rs1，rd
    #2 做加法运算
    #3 判断溢出（通过抑或）
    rs2 = (instru >> 20) & 0b11111
    rs1 = (instru >> 15) & 0b11111
    rd = (instru >> 7) & 0b11111
    #print(Register[rs1],Register[rs2],Register[rd])
    a1=Register[rs1]
    a2=Register[rs2]
    R1=[0]*33
    R2=[0]*33
    R3=[0]*33
    for i in range(0,32):
        R1[32-i]=a1%2
        R2[32-i]=a2%2
        a1=a1>>1
        a2=a2>>1
    R1[0]=R1[1]
    R2[0]=R2[1]
    carry=0
    for i in range(0,33):
        R3[32-i]=(carry+R1[32-i]+R2[32-i])%2
        carry=(carry+R1[32-i]+R2[32-i])>>1
    if R3[0]!=R3[1]:
        return 0
    for i in range(1,33):
        Register[rd]=Register[rd]*2+R3[i]
 
#store指令
def store(instru):
    #imm[11:5]      rs2     rs1     func3       imm[4:0]    opcode
    #1 读取寄存器和offset的内容
    #2 拼接出offset的大小
    #3 rs2存储数据，rs1表示基址寄存器，里面的内容和offset相加得到内存地址
    #4 将rs2中的内容存放到内存中
    rs2 = (instru >> 20) & 0b11111
    rs1 = (instru >> 15) & 0b11111
    im1 = (instru >> 25)
    im2 = (instru >> 7) & 0b11111
    im = im1 << 5 + im2
    memAddr = rs1 + im
    for i in range(4):
        Memory[memAddr + i] = Register[rs2] & 0xff
        Register[rs2] = Register[rs2] >> 8
        print(hex(Memory[memAddr + i]))
 
def main():
    #首先进行，pc加一这种操作
    #pc指向指令在内存中的地址，32位
    #寄存器，32个，需要5位寻找一个寄存器
    #内存：32位地址，说明pc的内容占32位
    #pc的初值：设为0地址
    #pc+1怎么实现：取决于risc-v是定长指令系统还是不定长指令，32位定长指令集
    pc = 0x00000000
    while (1):
        #首先读取指令，然后根据指令判断进行pc+1还是进行跳转
        #读取指令：读取pc指向内存地址的内容
        instru = defInstr(pc)
        print(hex(pc))
        print(hex(instru))
        print (judgeType(instru))
        if judgeType(instru) == 'load':
            load(instru)
        elif judgeType(instru) == 'add':
            add(instru)
            print(Register[0b00101])
        elif judgeType(instru) == 'store':
            store(instru)
        pc += 4#这里小端模式的处理方式有待商榷
        print(pc)
 
main()#程序入口