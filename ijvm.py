from ijvmutil import *

class Stack(object):
    def __init__(self):
        self.stack = []

    def setStack(self, l):
        self.stack = l

    def getSize(self):
        return len(self.stack)

    def pop(self, sp):
        self.stack.pop()

    def cuttop(self, index):
        self.stack = self.stack[:index+1]

    def silentpush(self, w):
        self.stack.append(w)

    def __getitem__(self, key):
        return self.stack[key]

    def __setitem__(self, key, value):
        key = int(key)
        if key >= len(self.stack):
            self.stack.append(value)
        else:
            self.stack[key] = value

class ConstantPool(object):
    def __init__(self):
        self.constantpool = []

    def setConstantPool(self, l):
        for li in l:
            if type(li) == str:
                self.constantpool.append(int(li, base=16))
            elif type(li) == int:
                self.constantpool.append(li)
        #self.constantpool = l

    def getSize(self):
        return len(self.constantpool)
        
    def __getitem__(self, key):
        if type(key) == int: return self.constantpool[key]
        else: return self.constantpool[int(key, base=16)]

class MethodArea(object):
    def __init__(self):
        self.methodarea = []
        
    def setMethodArea(self, l):
        for li in l:
            if type(li) == str:
                self.methodarea.append(int(li, base=16))
            elif type(li) == int:
                self.methodarea.append(li)
        #self.methodarea = l

    def getSize(self):
        return len(self.methodarea)

    def __getitem__(self, key):
        if type(key) == int: return self.methodarea[key]
        else: return self.methodarea[int(key, base=16)]


        

class IJVM(object):
    
    def __init__(self, image):
        self.image = image

        self.stack = Stack()
        self.cpp = ConstantPool()
        self.method = MethodArea()

        
        self.method.setMethodArea(image.getMethodArea())
        self.cpp.setConstantPool(image.getConstantPool())
        self.stack.setStack([])
        
        self.sp = self.stack.getSize() - 1          
        self.lv = 0                 
        self.pc = INITIAL_PC
        self.wide = False



        self.initial_sp = self.sp;

        #Set everything up
        self.push(INITIAL_OBJ_REF)
        #Push all arguments here
        
        self.invoke_virtual(self.image.getMainIndex())
        
    def start(self):
        print "Stack: " + str(self.stack.stack)
        while self.active():
            self.execute_opcode()
            tmp = [str(x) for x in self.stack.stack]
            try:
                tmp[self.sp] = "SP->" + tmp[self.sp]
                tmp[self.lv] = "LV->" + tmp[self.lv]
            except: pass
            print "-----------"
            print "Stack: " + str(self.stack.stack[::-1])
            print tmp[::-1]
            print "-----------"

        self.print_result()

    def fetchByte(self, signed=False):
        b = self.method[self.pc]
        self.pc = self.pc + 1

        if signed and b > 127:
            b = (256 - b) * (-1)
            
        return b

    def fetchWord(self, signed=False):
        word = self.method[self.pc] * 256 + self.method[self.pc + 1]
        self.pc = self.pc + 2

        if signed and word > 32767:
            word = (65536 - word) * (-1)

        return word

    def push(self, word):
        self.sp = self.sp + 1;
        self.stack[self.sp] = word

    def silentpush(self, word):
        self.stack.silentpush(word)

    def pop(self):
        result = self.stack[self.sp]
        self.stack.pop(self.sp)
        self.sp = self.sp - 1
        return result


    def invoke_virtual(self, index):
        if(index >= 0x8000):
            print("index >= 0x8000")
            return
        address = self.cpp[index]
        nargs = self.method[address] * 256 + self.method[address + 1]
        nlocals = self.method[address + 2] * 256 + self.method[address + 3]
        #self.sp = self.sp + nlocals #<-Instead of this

        #We initialize the local variables to 0
        for x in range(nlocals):
            self.push(0)
            
        self.push(self.pc)
        self.push(self.lv)
        self.lv = self.sp - nargs - nlocals - 1
        self.stack[self.lv] = self.sp - 1
        self.pc = address + 4

    def ireturn(self):
        linkptr = self.stack[self.lv]
        self.stack[self.lv] = self.stack[self.sp]
        self.sp = self.lv
        self.pc = self.stack[linkptr]
        self.lv = self.stack[linkptr + 1]
        self.stack.cuttop(self.sp)

    def execute_opcode(self):

        opc = self.pc
        opcode = self.fetchByte()

        print "PC:" + str(opc) + "; OPCODE: [" + str(hex(opcode)) + "]"


        if opcode == OPCODE_BIPUSH:
            self.push(self.fetchByte(signed=True))
            
        elif opcode == OPCODE_DUP:
            self.push(self.stack[self.sp])
            
        elif opcode == OPCODE_GOTO:
            offset = self.fetchWord(signed=True)
            self.pc = opc + offset
            
        elif opcode == OPCODE_IADD:
            a = self.pop()
            b = self.pop()
            self.push(a+b)

        elif opcode == OPCODE_IAND:
            a = self.pop()
            b = self.pop()
            self.push(int(a and b))

        elif opcode == OPCODE_IFEQ:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            if(a == 0):
                self.pc = opc + offset
                
        elif opcode == OPCODE_IFLT:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            if(a < 0):
                self.pc = opc + offset

        elif opcode == OPCODE_IF_ICMPEQ:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            b = self.pop()
            if(a == b):
                self.pc = opc + offset

        elif opcode == OPCODE_IINC:
            varnum = self.fetchByte()
            a = self.fetchByte(signed=True)
            self.stack[self.lv + varnum] += a

        elif opcode == OPCODE_ILOAD:
            if (self.wide):
                varnum = self.fetchWord()
            else:
                varnum = self.fetchByte()
            self.push(self.stack[self.lv + varnum])

        elif opcode == OPCODE_INVOKEVIRTUAL:
            index = self.fetchWord()
            self.invoke_virtual(index)

        elif opcode == OPCODE_IOR:
            a = self.pop()
            b = self.pop()
            self.push(a or b)

        elif opcode == OPCODE_IRETURN:
            self.ireturn()

        elif opcode == OPCODE_ISTORE:
            if(self.wide):
                varnum = self.fetchWord()
            else:
                varnum = self.fetchByte()
            a = self.pop()
            self.stack[self.lv + varnum] = a

        elif opcode == OPCODE_ISUB:
            a = self.pop()
            b = self.pop()
            self.push(b - a)

        elif opcode == OPCODE_LDC_W:
            index = self.fetchWord()
            self.push(self.cpp[index])

        elif opcode == OPCODE_NOP:
            pass
        
        elif opcode == OPCODE_POP:
            self.pop()

        elif opcode == OPCODE_SWAP:
            a = self.stack[self.sp]
            self.stack[self.sp] = self.stack[self.sp - 1]
            self.stack[self.sp - 1] = a

        elif opcode == OPCODE_WIDE:
            self.wide = True

            
        if not opcode == OPCODE_WIDE:
            self.wide = False
            
    def active(self):
        return not self.pc == INITIAL_PC

    def print_result(self):
        print "return value: " + str(self.stack[self.sp])

        
if __name__ == "__main__":

    image = IJVMImage()
    image.method_area = ['0x00', '0x03', '0x00', '0x01', '0x10', '0x00', '0x36', '0x03', '0x15', '0x01', '0x9b', '0x00', '0x19', '0x15', '0x01', '0x99', '0x00', '0x14', '0x15', '0x01', '0x10', '0x01', '0x64', '0x36', '0x01', '0x15', '0x03', '0x15', '0x02', '0x60', '0x36', '0x03', '0xa7', '0xff', '0xe8', '0x15', '0x03', '0xac', '0x00', '0x01', '0x00', '0x00', '0x10', '0x2c', '0x10', '0x0a', '0x10', '0x49', '0xb6', '0x00', '0x00', '0xac']
    image.constant_pool = [0x00000000, 0x26]
    image.main_index = 1
    i = 0
    tmp = []
    print "Method area"
    for x in image.method_area:
        tmp.append(str(i) + ": " + x)
        i += 1
    print tmp
    print "Constant pool"
    print image.constant_pool
    ijvm = IJVM(image)

    ijvm.start()

