# 采用RISC-V定长指令集，指令长度为32位。
# 主存地址空间为：2^32 * 8bit，地址长度为32位，一个字节8位，按字节寻址。
# 寄存器大小为32位，指令长度为32位，数据长度为32位。

# RISC-V指令集指令编码方式：
# R型指令： funct7           rs2 rs1     funct3  rd             opcode
# I型指令： immediate[11:0]      rs1     funct3  rd             opcode
# S型指令： immediate[11:5]  rs2 rs1     funct3  immediate[4:0] opcode

Register = {
    # risc指令集中第0号寄存器恒存0
    0b00001 : 0x00000000,       #临时寄存器r1，初始内容为0
    0b00010 : 0x00000000,       #临时寄存器r2，初始内容为0
    0b00011 : 0x00000000,       #临时寄存器r3，初始内容为0

    0b00100 : 0x00000010        #基址寄存器ba(rs1)，初始内容为逻辑地址0的内存地址0x00000010
}

Memory = {
    # 为实现方便，采用小端存储，其中指令与数据都存在内存中。
    # load和store的支持的唯一寻址模式是符号扩展 12 位立即数到基地址寄存器
    #lw r1, #0
    #imm[11:0]     rs1     func3    rd      opcode
    #000000000000  00100   010      00001   0000011
    #imm =+0       ba      lw       r1      load
    #0x00022083采用小端方式存储，内容为0x83 20 02 00
    0x00000000 : 0x83,
    0x00000001 : 0x20,
    0x00000002 : 0x02,
    0x00000003 : 0x00,
 
    #lw r2, #1，这里偏移量为4
    #imm[11:0]     rs1     func3    rd      opcode
    #000000000100  00100   010      00010   0000011
    #imm =+0       ba      lw       r2      load
    #0x00422103采用小端方式存储，内容为0x03 21 42 00
    0x00000004 : 0x03,
    0x00000005 : 0x21,
    0x00000006 : 0x42,
    0x00000007 : 0x00,
 
    #add r3, r1, r2
    #funct7     rs2     rs1     funct3      rd      opcode
    #0000000    00001   00010   000         00011   0110011
    #           r1      r2                  r3
    #内容为0x00 11 01 B3
    0x00000008 : 0xB3,
    0x00000009 : 0x01,
    0x0000000A : 0x11,
    0x0000000B : 0x00,

    #store r3, #3，这里偏移量为12
    #imm[11:5]      rs2     rs1     func3       imm[4:0]        opcode
    #0000000        00011   00100   010         01100           0100011
    #imm =+0        r3      ba      sw          imm =+0         load
    #内容为0x00 32 26 23
    0x0000000C : 0x23,
    0x0000000D : 0x26,
    0x0000000E : 0x32,
    0x0000000F : 0x00,
 
    #逻辑地址0的数据
    #不妨令第一个加数为1：0x00000001，小端存储为0x01000000
    0x00000010 : 0x01,
    0x00000011 : 0x00,
    0x00000012 : 0x00,
    0x00000013 : 0x00,
 
    #逻辑地址1的数据
    #不妨令第二个加数为2：0x00000002，小端存储为0x02000000
    0x00000014 : 0x02,
    0x00000015 : 0x00,
    0x00000016 : 0x00,
    0x00000017 : 0x00,
 
    #逻辑地址3的数据
    #不妨初始为0
    0x0000001C : 0x00,
    0x0000001D : 0x00,
    0x0000001E : 0x00,
    0x0000001F : 0x00
}

Opcode = {
    0b0000011 : 'load',
    0b0110011 : 'add',
    0b0100011 : 'store'
}

def Get_I(I_addr):
    I_code = 0x00000000
    for i in range(4):
        I_code += Memory[I_addr + i] * (256**i)
    return I_code

def Decode(I_code):
    I_Opcode = I_code & 0b1111111
    if I_Opcode == 0b0000011 :
#           print(hex(I_code))
            load(I_code)
    elif I_Opcode == 0b0110011:
            add(I_code)
            print("两数之和为：",Register[0b00011]) 
    elif I_Opcode == 0b0100011:
            store(I_code)
        
def load(I_code):
    offset = I_code >> 20 #偏移量表示编译的字节数，这里的偏移量注意不是逻辑地址偏移量，是物理地址偏移量
#   print(offset)
    rd = (I_code >> 7) & 0b11111
    Register[rd] = Memory[Register[0b00100] + offset]
#   print(hex(Register[0b00100]))

def store(I_code):
    rs2 = (I_code >> 20) & 0b11111
    offset_1 = (I_code >> 25)
    offset_2 = (I_code >> 7) & 0b11111
    offset = offset_1 << 5 + offset_2
    Memory[Register[0b00100] + offset] = Register[rs2]
    

def add(I_code):
    rs2 = (I_code >> 20) & 0b11111
    rs1 = (I_code >> 15) & 0b11111
    rd = (I_code >> 7) & 0b11111
#   print(Register[rs1],Register[rs2],Register[rd])
    print("逻辑地址0存的数为：",Register[rs1])
    print("逻辑地址0存的数为：",Register[rs2])

    #采用二进制加法以判断溢出
    a1 = Register[rs1]
    a2 = Register[rs2]
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
    

def main():
    # PC指向下一条指令的地址
    PC=0x00000000
    while(1):
        I_code = Get_I(PC)
        PC += 4 #这里先只考虑顺序执行
        if(PC>16):#这里只实现四条指令
            break
        Decode(I_code)

main()