'''
for(i=999; i>=0 ; i =i-1)
    x[i] = x[i]+s;
'''

#浮点数，每个数占8个内存单元，1000个数共占用8000个内存单元，即0-7999（0x0000-0x1f3f），当x1 = 8000即x1 = 0x1f40时退出循环
base = {
    "x1":0x0000,
    "x2":0x1f40
        }
s = 1
instrlist = []
reg = {}
#寄存器初始化
def initReg():
    for i in range(32):
        if i < 10 :
            reg["f0" + str(i)] = 0x00
        else:
            reg["f" + str(i)] = 0x00
    return reg
mem = {}
# 内存初始化,默认数组中的元素全为0x000000000000000a
# 小端存储，举例：第一个数存储如下
# 0x00:0a
# 0x01:00
# 0x02:00
# 0x03:00
# 0x04:00
# 0x05:00
# 0x06:00
# 0x07:00
def initMem():
    for i in range(1000*8):
        mem[str(hex(i))] = 0x00
    for i in range(0,1000*8,8):
        mem[str(hex(i))] = hex(10)
    #     # print(str(hex(i)) + ":" + hex(10))
    # for i in range(1000 * 8):
    #     print(str(hex(i))+ ":" + str(mem[str(hex(i))]))

def fld(instr):
    # "fld f00,00(x1)"
    rd = instr[4:7]
    offset = instr[8:10]
    rs = instr[11:13]
    dataIndex = int(base[rs]) + int(offset)
    data = mem[str(hex(dataIndex))]
    reg[rd] = data
    return

def fadd(instr):
    # "fadd.d f4,f0,f2"
    rs1 = instr[11:14]
    rs2 = instr[15:18]
    rd = instr[7:10]
    temp = int(str(reg[rs1]),16) + int(reg[rs2])
    reg[rd] = str(hex(temp))
    return

def fsd(instr):
    # "fsd f04,00(x1)"
    rs = instr[4:7]
    if (instr[8] == "-"):
        offset = instr[9:11]
        rd = instr[12:14]
        dataIndex = int(base[rd]) - int(offset)
        mem[str(hex(dataIndex))] = reg[rs]
    else:
        offset = instr[8:10]
        rd = instr[11:13]
        dataIndex = int(base[rd]) + int(offset)
        mem[str(hex(dataIndex))] = reg[rs]
    return

def addi(instr):
    # "addi x1,x1,32"
    rs = instr[8:10]
    imm = instr[11:13]
    rd = instr[5:7]
    base[rd] = base[rs] + int(imm)
    return
def bne(instr):
    # "bne x1,x2,Loop"
    r1 = instr[4:6]
    r2 = instr[7:9]
    compare1 = int(base[r1])
    compare2 = int(base[r2])
    res = compare2 - compare1
    if res:
        return 1
    else:
        return 0

def judgeAndexec(instr):
    if(instr[0:4] == "fld "):
        fld(instr)
        return "fld"
    elif(instr[0:4] == "fadd"):
        fadd(instr)
        return "fadd"
    elif(instr[0:4] == "fsd "):
        fsd(instr)
        return "fsd"
    elif(instr[0:4] == "addi"):
        addi(instr)
        return "addi"
    elif(instr[0:4] == "bne "):
        bne(instr)
        return "bne"
    else:
        return "instruction error!"

def main():

    instrlist = [
        "fld f00,00(x1)",
        "fld f06,08(x1)",
        "fld f10,16(x1)",
        "fld f14,24(x1)",
        "fadd.d f04,f00,f02",
        "fadd.d f08,f06,f02",
        "fadd.d f12,f10,f02",
        "fadd.d f16,f14,f02",
        "fsd f04,00(x1)",
        "fsd f08,08(x1)",
        "addi x1,x1,32",
        "fsd f12,-16(x1)",
        "bne x1,x2,Loop",
        "fsd f16,-08(x1)"
    ]
    initReg()
    # 指定常数
    reg["f02"] = 1
    # 数据初始化
    initMem()
    print("——————————————————————————————数组中元素初始值为：")
    for i in range(1000 * 8):
        print(str(hex(i))+ ":" + str(mem[str(hex(i))]))
    flag = 1
    # 指令索引，共14条指令
    i = 0
    while(i<14):
        instr = instrlist[i]
        i = i + 1
        type = judgeAndexec(instr)
        if ( type == "bne") :
            flag = bne(instr)
        if flag:
            if i == 14:
                i = 0
    print("——————————————————————————————指令执行后数组中元素值为：")
    for i in range(1000 * 8):
        print(str(hex(i))+ ":" + str(mem[str(hex(i))]))
main()









