# 指令集架构为RISC-V RV32C
# 代码只实现RV32C下的总共32条16位指令
# 指令为格式为： 
# R型： func4        rd/rs1      rs2             op
# I型： func3  imm   rd/rs1      imm             op
# SS型：func3           imm      rs2             op
# IW型：func3           imm              rd'     op
# L型： func3   imm      rs1'    imm     rd'     op
# S型： func3   imm      rs1'    imm     rs2'    op
# B型： func3   offset   rs1'    offset          op
# J型： func3        jump target                 op

from ftplib import error_perm
from http.cookiejar import LWPCookieJar

from First_week import Memory


Register = {
    # risc指令集中第0号寄存器恒存0
    0b00001 : 0x00000000,       #临时寄存器a0，初始内容为0
    0b00010 : 0x00000000,       #临时寄存器a1，初始内容为0
    0b00011 : 0x00000000,       #临时寄存器a2，初始内容为0
    0b00100 : 0x00000000,       #临时寄存器a3，初始内容为0
    0b00101 : 0x00000000,       #临时寄存器a4，初始内容为0
    0b00110 : 0x00000000,       #临时寄存器a5，初始内容为0

    0b00111 : 0x00000000,       #保存寄存器s0，初始内容为0
    0b01000 : 0x00000000,       #保存寄存器s1，初始内容为0

    0b01001 : 0x00000000,       #   栈指针sp， 初始内容为0
    0b01010 : 0x00000000,       #返回寄存器ra，初始内容为0
}

def Decode(I_code):
    I_Opcode = I_code & 0b11
    if(I_Opcode == 0b00):
        type1(I_code)
    elif(I_Opcode == 0b01):
        type2(I_code)
    elif(I_Opcode == 0b10):
        type3(I_code)
        
def type1(I_code):
    I_func3 = I_code >> 13
    match I_func3:
        case 0b000:
            if(I_code == 0):
                return error_perm
            else:
                c_addi4spn(I_code)
        case 0b001:
            c_fld(I_code)
        case 0b010:
            c_lw(I_code)
        case 0b011:
            c_flw(I_code)
        case 0b101:
            c_fsd(I_code)
        case 0b110:
            c_sw(I_code)
        case 0b111:
            c_fsw(I_code)
        case _:
            print("ERROR")
        
        
        
        
        
        
            

        

def type2(I_code):
    return
def type3(I_code):
    return

def c_addi4spn(I_code):
def c_fld(I_code):
def c_lw(I_code):
def c_flw(I_code):
def c_fsd(I_code):
def c_sw(I_code):
def c_fsw(I_code):
    return


def Get_I(I_addr):
    I_code = 
    return I_code

def main():
    # 程序放在开辟的一片连续的内存空间中，PC指向空间中的第一条指令。
    # 参照手册，仍然每次从内存中取4个字节，寄存器也是32位的。
    # 参照手册，RISC-V是按照小尾端字节序来存储指令和数据的。
   
    with open('Memory_Inst.tex','rb',) as f:
        #这里暂时对内存文件只读，即不考虑对文件的读写
        #如果考虑文件的读写，已知只有load和store指令可以对内存进行访问，这时候需要对内存文件中的特定地址的数据进行写
        read_data = f.read(4)
        #如已到达文件末尾，f.read() 返回空字符串（''）。
    
    PC=0x00000000
    
    while(1):
        I_code = Get_I(PC)
        PC += 4
        if(PC == 1):
            break
        Decode(I_code)
    return
main()

