# 采用RISC-V 32I基础指令集，实现5种指令类型的微操作。
# 由于32I基础指令集只支持32位字节可寻址的地址空间，故内存大小为4GB。
# 定义内存文件，采用字节编址和小端存储，按双字对齐地址。首地址默认为 0x00000000
# 只实现通用寄存器，寄存器使用字典[register_number : data/instruction]实现。

Register = {
    #RV32I有31个寄存器加上一个值恒为0的x0寄存器。
    0b00001 : 0x00000000,       #临时寄存器r1，初始内容为0
    0b00010 : 0x00000000,       #临时寄存器r2，初始内容为0
    0b00011 : 0x00000000,       #临时寄存器r3，初始内容为0

    0b00100 : 0x00000010        #
}

Mem = {

}

def Decode(I_code):
    global PC
    #所有位全部是0/1是非法的RV32I指令。
    opcode = I_code & 111111
    if(opcode == 0x00000000):
        print("ERROR0")
    if(opcode == 0xFFFFFFFF):
        print("ERROR1")

    match opcode:
        case 0b0110111 | 0b0010111 | 0b1101111:#J型指令
            offset = Jump(I_code)
            if(offset):
                PC = offset - 4
        case 0b1100011:#B型指令
            offset = Branch(I_code)
            if(offset):
                PC = offset - 4
        case 0b0110011:#R型指令
            RR(I_code)
        case 0b1100111 | 0b0000011 | 0b0010011 | 0b0001111 | 0b1110011:#I型指令
            RI(I_code)
        case 0b0100011:#S型指令
            Store(I_code)
        case _:
            print("ERROR3")   
def Jump(I_code):
    #函数返回偏移量
    #用于长立即数的U型指令和用于无条件跳转的J型指令
    return 0
def Branch(I_code):
    #函数返回偏移量
    #用于条件跳转操作的B型指令
    #B型指令： immediate[12|10:5]  rs2  rs1     funct3  immediate[4:1|11] opcode
    funct3 = (I_code >> 12) & 0b111
    rs2 = (I_code >> 15) & 0b11111
    rs1 = (I_code >> 20) & 0b11111
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
    return
def RI(I_code):
    #用于短立即数和访存操作的I型指令
    return 
def Store():
    #用于访存操作的S型指令
    return 



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
    I_code = Mem[PC]
    while(1):
        PC += 4
        Decode(I_code)
        I_code = Mem[PC]
        
    return
main()