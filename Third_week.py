# 采用RISC-V 32I基础指令集，实现5种指令类型的微操作。
# 由于32I基础指令集只支持32位字节可寻址的地址空间，故内存大小为4GB。
# 定义内存文件，采用字节编址和小端存储，按双字对齐地址。首地址默认为 0x00000000
# 只实现通用寄存器，寄存器使用字典[Register_number : data/instruction]实现。

Register = {
    # RV32I有31个寄存器加上一个值恒为0的x0寄存器。
    0b00001: 0x00000000,  # 临时寄存器r1，初始内容为0
    0b00010: 0x00000001,  # 临时寄存器r2，初始内容为0
    0b00011: 0x00000002,  # 临时寄存器r3，初始内容为0

    0b00100: 0x00000010  #
}

Mem = {
    # 内存存指令和数据
    # RR型
    # add r1,r2,r3
    # 0000000 00010 00011 000 00001 0110011
    # 0000 0000 0010 0001 1000 0000 1011 0011
    0x00000000: 0x00,
    0x00000001: 0x21,
    0x00000002: 0x80,
    0x00000003: 0xb3
}

def Decode(I_code):
    global PC
    #所有位全部是0/1是非法的RV32I指令。
    opcode = I_code & 0b111111
    if(opcode == 0x00000000):
        print("ERROR0")
    if(opcode == 0xFFFFFFFF):
        print("ERROR1")

    match opcode:
        case 0b0110111 | 0b0010111 | 0b1101111 | 0b1100111:#跳转类指令
            offset = Jump(I_code)
            if(offset):
                PC = offset - 4
        case 0b1100011:#B型指令
            offset = Branch(I_code)
            if(offset):
                PC = offset - 4
        case 0b0110011:#R型指令
            RR(I_code)
        case 0b0000011 | 0b0010011 | 0b0001111 | 0b1110011:#I型指令
            RI(I_code)
        case 0b0100011:#S型指令
            Store(I_code)
        case _:
            print("ERROR3")   

def Jump(I_code):
    #函数返回偏移量
    #用于长立即数的U型指令和用于无条件跳转的J型指令
    opcode = I_code & 0b111111
    rd = (I_code >> 7) & 0b11111
    match opcode:
        case 0b0110111:#lui
            return 
        case 0b0010111:#auipc
            return
        case 0b1101111:#jal: x[rd] = pc+4; pc += sext(offset)
            Register[rd] = PC#rd默认为1
            imm1_j = (I_code >> 21) & 0b111111111   #[10:1]
            imm2_j = I_code >> 20                   #[11]
            imm3_j = (I_code >> 12) & 0b111111111   #[19:12]
            sign = I_code >> 31                     #[20]
            if(sign == 0b0):
                offset = imm1_j << 1 + imm2_j << 11 + imm3_j << 12
            else:
                offset = (-1) * (imm1_j << 1 + imm2_j << 11 + imm3_j << 12)
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
    imm1 = (I_code >> 8) & 0b1111
    imm2 = (I_code >> 25) & 0b111111
    imm3 = (I_code >> 7) & 0b1
    sign = I_code >> 31
    if(sign == 0b0):
        offset = imm1 << 1 + imm2 << 5 + imm3 << 10
    else:
        offset = (-1) * (imm1 << 1 + imm2 << 5 + imm3 << 10)
    match funct3:
        case 0b000:#Beq：相等即跳转
            if(rs2 == rs1):
                return offset
        case _:
            print("待定") 
    return 0

def RR(I_code):
    #用于寄存器-寄存器操作的R型指令
    funct3 = (I_code >> 12) & 0b111
    rd = (I_code >> 7) & 0b11111
    rs2 = (I_code >> 20) & 0b11111
    rs1 = (I_code >> 15) & 0b11111
    funct7 = (I_code >> 25) & 0b1111111

    match funct3:
        case 0b000:
            if(funct7 == 0b0000000):#add: x[rd] = x[rs1] + x[rs2]
                Register[rd] = Register[rs1] + Register[rs2]
                print(Register[rd])
            elif(funct7 == 0b0100000):#sub: x[rd] = x[rs1] + x[rs2]
                Register[rd] = Register[rs1] + Register[rs2] 
        case _:
            print("待定") 

def RI(I_code):
    #用于短立即数和访存操作的I型指令
    opcode = I_code & 0b111111
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
        offset = imm1 + imm2 << 5
    else:
        offset = (-1) * (imm1 + imm2 << 5)
    match funct3:
        case 0b000:#sb: M[x[rs1] + sext(offset)] = x[rs2][7: 0]
            Mem[Register[rs1]+offset] = Register[rs2] & 0x00
        case 0b001:#sh: M[x[rs1] + sext(offset)] = x[rs2][15: 0]
            Mem[Register[rs1]+offset] = Register[rs2] & 0x0000
        case 0b010:#sw: M[x[rs1] + sext(offset)] = x[rs2][31: 0]
            Mem[Register[rs1]+offset] = Register[rs2] 

# 取指令
def defInstr(addr):  # 传入参数为指令在内存的地址
    instru = 0x00000000
    for i in range(4):
        instru = instru * 256 + Mem[addr + i]
    return instru

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

    PC = 0x00000000
    I_code = defInstr(PC)
    print("当前指令为：" + "0x%08x" % (I_code))
    Decode(I_code)
    # while(1):
    #     Decode(I_code)
    #     I_code = Mem[PC]
    #     PC += 4

main()