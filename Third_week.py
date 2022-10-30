# 采用RISC-V 32I基础指令集，实现5种指令类型的微操作。
# 由于32I基础指令集只支持32位字节可寻址的地址空间，故内存大小为4GB。
# 定义内存文件，采用字节编址和小端存储，按双字对齐地址。首地址默认为 0x00000000
# 只实现通用寄存器，寄存器使用字典[register_number : data/instruction]实现。

from ast import iter_child_nodes
import struct


Register = {
    #RV32I有31个寄存器加上一个值恒为0的x0寄存器。
    0b00001 : 0x00000000,       #临时寄存器r1，初始内容为0
    0b00010 : 0x00000000,       #临时寄存器r2，初始内容为0
    0b00011 : 0x00000000,       #临时寄存器r3，初始内容为0

    0b00100 : 0x00000010        #基址寄存器ba(rs1)，初始内容为逻辑地址0的内存地址0x00000010
}

def Decode():
    #所有位全部是0/1是非法的RV32I指令。
    return

def Jump():
    #用于长立即数的U型指令和用于无条件跳转的J型指令
    return
def Branch():
    #用于条件跳转操作的B型指令
    return
def RR():
    #用于寄存器-寄存器操作的R型指令
    return
def RI():
    #用于短立即数和访存操作的I型指令
    return 
def Store():
    #用于访存操作的S型指令
    return 



def main():
    #RISC-V指令集中程序计数器PC是用硬件实现的，这里仅对PC功能进行描述。
    with open('Memory.bin', 'rb') as f:
        PC = f
        I_code = bytes(4)
        for i in range(4):
            I_code = I_code + PC.read(2)#一行存一个字节
        I_code = bytes(I_code)
        print(I_code)
        print(I_code.hex('-'))
        
         
            
        
    # Decode(I_code)
    return
main()