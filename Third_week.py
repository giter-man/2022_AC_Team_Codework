# 采用RISC-V 32I基础指令集，实现5种指令类型的微操作。
# 由于32I基础指令集只支持32位字节可寻址的地址空间，故内存大小为4GB。
# 定义内存文件，采用字节编址和小端存储，按双字对齐地址。首地址默认为 0x00000000
# 只实现通用寄存器，寄存器使用字典[Register_number : data/instruction]实现。
PC = 0x00000000
Register = {
    #RV32I有31个寄存器加上一个值恒为0的x0寄存器。
    0b00000 : 0x00000000,       #临时寄存器r0，需要设置只读权限，或者静态之类的，保证其值恒为0。
    0b00001 : 0x00000001,       #临时寄存器r1，初始内容为0
    0b00010 : 0x00000002,       #临时寄存器r2，初始内容为0
    0b00011 : 0x00000000,       #临时寄存器r3，初始内容为0
    0b00100 : 0x00000003,       #临时寄存器r4，初始内容为0
    0b00101 : 0x0000001F,       #临时寄存器r5，初始内容为0
}

Mem = {
    #内存存指令和数据，采用小端存储。
    #负数用原码表示（未来可以用补码表示）
    #每种类型测试一条指令，总共测试五种类型。这里仅测试功能，指令分别为：
    #add r3 r1 r2:  x[r3] = x[r1] + x[r2]
    #0000000 00010 00001 000 00011 0110011
    #0000 0000 0010 0000 1000 0001 1011 0011
    #0x00 20 81 B3
    0x00000000 : 0xB3,
    0x00000001 : 0x81,
    0x00000002 : 0x20,
    0x00000003 : 0x00,

    #jal r2 8:      x[r2] = pc+4; pc += 8
    #0000 0000 1000 0000 0000 00010 1101111
    #0x00 80 01 6F
    0x00000004 : 0x6F,
    0x00000005 : 0x01,
    0x00000006 : 0x80,
    0x00000007 : 0x00,

    #sw  r4 -4(r5):  Mem[x[r5] - 4] = x[r4]
    #-4(0b100000000100)
    #1000000 00100 00101 010 00100 0100011
    #1000 0000 0100 0010 1010 0010 0010 0011
    #0x80 42 A2 23
    0x00000008 : 0x23,
    0x00000009 : 0xA2,
    0x0000000A : 0x42,
    0x0000000B : 0x80,

    #lw  r3 24(r0):   x[r3] = Mem[0 + 24]
    #000000011000 00000 010 00011 0000011
    #0000 0001 1000 0000 0010 0001 1000 0011
    #0x01 80 21 83 
    0x0000000C : 0x83,
    0x0000000D : 0x21,
    0x0000000E : 0x80,
    0x0000000F : 0x01,
    
    #beq r3 r4 8:   if(r2 == r3) pc += -12(0b1000000001100) 
    #1000000 00011 00100 000 01100 1100011
    #1000 0000 0011 0010 0000 0110 0110 0011
    #0x80 32 06 63
    0x00000010 : 0x63,
    0x00000011 : 0x06,
    0x00000012 : 0x32,
    0x00000013 : 0x80,

    ####################数据区#########################
    
    0x00000014 : 0x63,
    0x00000015 : 0x04,
    0x00000016 : 0x32,
    0x00000017 : 0x00,

    0x00000018 : 0x63,
    0x00000019 : 0x04,
    0x0000001A : 0x32,
    0x0000001B : 0x00,

    0x0000001C : 0x63,
    0x0000001D : 0x04,
    0x0000001E : 0x32,
    0x0000001F : 0x00,
}

def Decode(I_code):
    global PC
    #所有位全部是0/1是非法的RV32I指令。
    opcode = I_code & 0b1111111
    if(opcode == 0x00000000):
        print("ERROR0")
    if(opcode == 0xFFFFFFFF):
        print("ERROR1")

    match opcode:
        case 0b0110111 | 0b0010111 | 0b1101111 | 0b1100111:#跳转类指令
            upc = PC
            PC += Jump(I_code,upc)
            print("跳转后的指令地址为：", PC)
        case 0b1100011:#B型指令
            offset = Branch(I_code)
            if(offset):
                PC += offset
            print("分支后的指令地址为：", PC)
        case 0b0110011:#R型指令
            RR(I_code)
        case 0b0000011 | 0b0010011 | 0b0001111 | 0b1110011:#I型指令
            RI(I_code)
        case 0b0100011:#S型指令
            Store(I_code)
        case _:
            print(hex(opcode))
            print("ERROR3")   

def Jump(I_code,upc):
    #函数返回偏移量
    #用于长立即数的U型指令和用于无条件跳转的J型指令
    opcode = I_code & 0b1111111
    rd = (I_code >> 7) & 0b11111
    match opcode:
        case 0b0110111:#lui
            return 
        case 0b0010111:#auipc
            return
        case 0b1101111:#jal: x[rd] = pc+4; pc += sext(offset)
            Register[rd] = upc#rd默认为1
            imm1_j = (I_code >> 21) & 0b1111111111   #[10:1]
            imm2_j = I_code >> 20 & 0b1              #[11]
            imm3_j = (I_code >> 12) & 0b11111111     #[19:12]
            sign = I_code >> 31                      #[20]
            if(sign == 0b0):
                offset = (imm1_j << 1) + (imm2_j << 11) + (imm3_j << 12)
            else:
                offset = (-1) * ((imm1_j << 1) + (imm2_j << 11) + (imm3_j << 12))
            print("指令jal r2 8功能验证，跳转前下一条指令的地址为：", Register[rd])
            return offset
        case 0b1100111:#jalr: x[rd] = pc+4; pc=(x[rs1]+sext(offset))&~1
            Register[rd] = PC#rd默认为1
            rs1 = (I_code >> 15) & 0b11111
            imm_jr = (I_code >> 20) & 0b1111111111 #[10:0]
            sign = I_code >> 31                     #[20]
            if(sign == 0b0):
                offset = Register[rs1] + imm_jr
            else:
                offset = Register[rs1] + (-1) * imm_jr
            return offset
    return 0

def Branch(I_code):
    #函数返回偏移量
    #用于条件跳转操作的B型指令
    #B型指令： immediate[12|10:5]  rs2  rs1     funct3  immediate[4:1|11] opcode
    funct3 = (I_code >> 12) & 0b111
    rs2 = (I_code >> 20) & 0b11111
    rs1 = (I_code >> 15) & 0b11111
    imm1 = (I_code >> 8) & 0b1111       #[4:1]
    imm2 = (I_code >> 25) & 0b111111    #[10:5]
    imm3 = (I_code >> 7) & 0b1          #[11]
    sign = I_code >> 31
    if(sign == 0b0):
        offset = (imm1 << 1) + (imm2 << 5) + (imm3 << 11)
    else:#负数涉及二进制原码与整数的转换
        offset_b = (imm1 << 1) + (imm2 << 5) + (imm3 << 11)
        offset = -1 * offset_b
    match funct3:
        case 0b000:#beq：相等即跳转
            print("指令beq r3 r4 8功能验证：")
            print("寄存器r3中的值为：", Register[rs1])
            print("寄存器r4中的值为：", Register[rs2])
            if(Register[rs2] == Register[rs1]):
                return offset
            # print("---",bin(offset_b))
            # print("---",offset_b)
            # print("---",bin(offset))
            # print("---",offset)
        case _:
            print("待定") 
    return 0

def RR(I_code):
    #用于寄存器-寄存器操作的R型指令
    funct3 = (I_code >> 12) & 0b111
    rd = (I_code >> 7) & 0b11111
    rs1 = (I_code >> 15) & 0b11111
    rs2 = (I_code >> 20) & 0b11111
    funct7 = (I_code >> 25) & 0b1111111

    match funct3:
        case 0b000:
            if(funct7 == 0b0000000):#add: x[rd] = x[rs1] + x[rs2]
                Register[rd] = Register[rs1] + Register[rs2]
                print("指令add r3 r1 r2功能验证：")
                print("r1的内容为：", Register[rs1])
                print("r2的内容为：", Register[rs2])
                print("r3的内容为：", Register[rd])
            elif(funct7 == 0b0100000):#sub: x[rd] = x[rs1] + x[rs2]
                Register[rd] = Register[rs1] + Register[rs2] 
        case _:
            print("待定") 

def RI(I_code):
    #用于短立即数和访存操作的I型指令
    opcode = I_code & 0b1111111
    funct3 = (I_code >> 12) & 0b111
    rs1 = (I_code >> 15) & 0b11111
    rd = (I_code >> 7) & 0b11111
    sign = I_code >> 31
    imm = (I_code >> 20) & 0b1111111111
    if(sign == 0b0):
        offset = imm
    else:
        offset = (-1) * imm
    match opcode:
        case 0b0000011:#load 指令
            if(funct3 == 0b010):#lw: x[rd] = sext(M[x[rs1] + sext(offset)][31:0])
                Register[rd] = Mem[Register[rs1] + offset]
                print("lw  r3 24(r0)指令功能验证：")
                print(f'对应的内存单元的地址为：{Register[rs1]+offset}， 内容为：{Mem[Register[rs1]+offset]}')
                print("寄存器r3中的内容为：", Register[rd])
            else:
                print("待定")
        case _: 
            print("待定")  

def Store(I_code):
    #用于访存操作的S型指令
    funct3 = (I_code >> 12) & 0b111
    rs2 = (I_code >> 20) & 0b11111
    rs1 = (I_code >> 15) & 0b11111
    imm1 = (I_code >> 7) & 0b11111      #[4:0]
    imm2 = (I_code >> 25) & 0b111111    #[10:5]
    sign = I_code >> 31
    if(sign == 0b0):
        offset = imm1 + (imm2 << 5)
    else:
        offset = (-1) * (imm1 + (imm2 << 5))
    match funct3:
        case 0b000:#sb: M[x[rs1] + sext(offset)] = x[rs2][7: 0]
            Mem[Register[rs1]+offset] = Register[rs2] & 0x00
        case 0b001:#sh: M[x[rs1] + sext(offset)] = x[rs2][15: 0]
            Mem[Register[rs1]+offset] = Register[rs2] & 0x0000
        case 0b010:#sw: M[x[rs1] + sext(offset)] = x[rs2][31: 0]
            Mem[Register[rs1]+offset] = Register[rs2]
            print("指令sw  r4 -4(r5)功能验证：")
            print("r4中的值为：", Register[rs2]) 
            print("对应的内存单元的地址为：", Register[rs1]+offset)
            print("内容为：", Mem[Register[rs1]+offset])

def Get_I(I_addr):
    I_code = 0x00000000
    for i in range(4):
        I_code += Mem[I_addr + i] * (256**i)
    return I_code

def main():
    #RISC-V指令集中程序计数器PC是用硬件实现的，这里仅对PC功能进行描述。
    
    # with open('Memory.bin', 'rb') as f:
    #     PC = f
    #     I_code = bytes(4)
    #     for i in range(4):
    #         #一行存一个字节
    #         I_code = bytes(I_code)
    #     print(I_code)
    #     print(I_code.hex('-'))
    #可以借助format函数对内存文件进行读写
    
    global PC
    I_code = Get_I(PC)#这里将指令拼接
    while(1):
        print("PC:", PC)
        if(PC == 0x00000014):
            break
        PC += 4
        Decode(I_code)
        I_code = Get_I(PC)

main()