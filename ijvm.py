from ijvmutil import *

class Stack(object):
    def __init__(self):
        self.stack = []

    def setStack(self, l):
        self.stack = l

    def __getitem__(self, key):
        #return str(key) + "works"
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
        self.constantpool = l
        
    def __getitem__(self, key):
        if type(key) == int: return key
        else: return int(self.constantpool[key], base=16)

class MethodArea(object):
    def __init__(self):
        self.methodarea = []
        
    def setMethodArea(self, l):
        self.methodarea = l

    def __getitem__(self, key):
        if type(key) == int: return key
        else: return int(self.constantpool[key], base=16)


        

class IJVM(object):
    
    def __init__(self, image):
        self.image = image
        
        self.sp = 0           
        self.lv = 0                 
        self.pc = INITIAL_PC
        self.wide = False

        self.stack = Stack()
        self.cpp = ConstantPool()
        self.method = MethodArea()

        self.stack.setStack([])
        self.cpp.setConstantPool(image.getConstantPool())
        self.method.setMethodArea(image.getMethodArea())

        self.initial_sp = self.sp;

        #Set everything up
        self.push(INITIAL_OBJ_REF)
        #Push all arguments here

        
        self.invoke_virtual(self.image.getMainIndex())

        print self.stack.stack
    def start(self):
        while self.active:
            self.execute_opcode()
            print self.stack.stack

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

    def pop(self):
        result = self.stack[self.sp]
        self.sp = self.sp - 1
        return result


    def invoke_virtual(self, index):
        if(index >= 0x8000):
            print("index >= 0x8000")
            return
        address = self.cpp[index]
        nargs = self.method[address] * 256 + self.method[address + 1]
        nlocals = self.method[address + 2] * 256 + self.method[address + 3]
        
        self.sp = self.sp + nlocals
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

    def execute_opcode(self):

        opc = self.pc
        opcode = self.fetchByte()

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
            self.stack[self.lv +varnum] = self.pop()

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
    image.method_area = [0x00,0x01,0x00,0x00,0x10,0x01,0x10,0x02,0x60,0x10,0x04,0x60,0x10,0x03,0x60]
    image.constant_pool = [0x00000000]

    print image.method_area
    print image.constant_pool
    ijvm = IJVM(image)

    ijvm.start()

