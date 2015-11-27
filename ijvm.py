import sys
from ijvmutil import *

class Stack(object):
    def __init__(self):
        self.stack = []

    def setStack(self, l):
        self.stack = l

    def getStack(self, asString=True):
        if asString:
            return [str(element) for element in self.stack[::-1]]
        else:
            return [element for element in self.stack[::-1]]

    def getSize(self):
        return len(self.stack)

    def pop(self, sp):
        self.stack.pop()

    def cuttop(self, index):
        self.stack = self.stack[:index+1]

    def silentpush(self, w):
        self.stack.append(w)

    def __getitem__(self, key):
        if ALLOW_OVERFLOWS: return int_overflow(self.stack[key], MAX_INT)
        return self.stack[key]

    def __setitem__(self, key, value):
        key = int(key)
        if ALLOW_OVERFLOWS: value = int_overflow(value, MAX_INT)
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

    def getSize(self):
        return len(self.methodarea)

    def __getitem__(self, key):
        if type(key) == int: return self.methodarea[key]
        else: return self.methodarea[int(key, base=16)]




class IJVM(object):
    
    def __init__(self, image):
        self.image = image
        
        self.customOpCodes = {}
        self.customOpKeywords = {}
        
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

        ##Check how many arguments the main method takes
        address = self.cpp[self.image.getMainIndex()]
        nargs = self.method[address] * 256 + self.method[address + 1]
        ##Raise an error if the number supplied does not correspond
        if not len(self.image.getArguments()) == nargs - 1:
            raise IJVMException("Wrong number of arguments (main takes exactly " +
                                str(nargs - 1) + " arguments)")
        
        #Set everything up
        self.push(INITIAL_OBJ_REF)
        #Push all arguments here
        for arg in self.image.getArguments():
            if CAP_ARGS:
                arg = int(arg)
                if arg > MAX_INT: arg = MAX_INT
                if arg < - MAX_INT - 1: arg = - MAX_INT - 1
            self.push(arg)
        
        self.invoke_virtual(self.image.getMainIndex())

    def addCustomOPCode(self, code, func):
        self.customOpCodes[code] = func

    def mapCustomOPCode(self, code, s):
        self.customOpKeywords[str(s).upper()] = code

    def simulate(self):
        #No printing, but returns return value
        while self.active():
            self.execute_opcode()
        return self.stack[self.sp]
    
    def start(self):
        p_format = "{0} \tstack {1:>5} = {2}"

        #Print header
        header_format = "{0} \t       {1} \t {2}"
        header_op = Operation("Operation")
        header_op.opcode = "OPCode"
        print "---------------------------------------------------------------------------"
        print header_format.format(str(header_op), "Size", "Stack")
        print "---------------------------------------------------------------------------"
        #
        
        operCount = 0
        largestStackSize = self.stack.getSize()
        
        print p_format.format(str(Operation("Initial Stack")), "[" + str(self.stack.getSize()) + "]", ", ".join(self.stack.getStack()))
        print "----"
        print ""
        while self.active():
            executedOperation = self.execute_opcode()
            stackSize = self.stack.getSize()
            if stackSize > largestStackSize: largestStackSize = stackSize
            print p_format.format(str(executedOperation), "[" + str(stackSize) + "]", ", ".join(self.stack.getStack()))
            operCount += 1

        self.print_result()
        print ""
        print "Operations count: \t" + str(operCount)
        print "Largest stack size: \t" + str(largestStackSize)
        print ""
        
    def fetchByte(self, signed=False):
        b = self.method[self.pc]
        self.pc = self.pc + 1

        if signed and b > 127:
            b = (b - 256)
            
        return b

    def fetchWord(self, signed=False):
        word = self.method[self.pc] * 256 + self.method[self.pc + 1]
        self.pc = self.pc + 2

        if signed and word > 32767:
            word = (word - 65536)

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

        operation = Operation("?")

        if opcode == OPCODE_BIPUSH:
            a = self.fetchByte(signed=True)
            self.push(a)
            operation = Operation("bipush").addByte(a, signed=True)

        elif opcode == OPCODE_DUP:
            self.push(self.stack[self.sp])
            operation = Operation("dup")
            
        elif opcode == OPCODE_GOTO:
            offset = self.fetchWord(signed=True)
            self.pc = opc + offset
            operation = Operation("goto").addWord(offset, signed=True)
            
        elif opcode == OPCODE_IADD:
            a = self.pop()
            b = self.pop()
            self.push(a+b)
            operation = Operation("iadd")

        elif opcode == OPCODE_IAND:
            a = self.pop()
            b = self.pop()
            self.push(int(a and b))
            operation = Operation("iand")

        elif opcode == OPCODE_IFEQ:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            if(a == 0):
                self.pc = opc + offset
            operation = Operation("ifeq").addWord(offset, signed=True)
                
        elif opcode == OPCODE_IFLT:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            if(a < 0):
                self.pc = opc + offset
            operation = Operation("iflt").addWord(offset, signed=True)

        elif opcode == OPCODE_IF_ICMPEQ:
            offset = self.fetchWord(signed=True)
            a = self.pop()
            b = self.pop()
            if(a == b):
                self.pc = opc + offset
            operation = Operation("if_icmpeq").addWord(offset, signed=True)

        elif opcode == OPCODE_IINC:
            varnum = self.fetchByte()
            a = self.fetchByte(signed=True)
            self.stack[self.lv + varnum] += a
            operation = Operation("iinc").addByte(varnum).addByte(a, signed=True)
            
        elif opcode == OPCODE_ILOAD:
            operation = Operation("iload") #Slightly different order, because it is conditional
            if (self.wide):
                varnum = self.fetchWord()
                operation.addWord(varnum)
            else:
                varnum = self.fetchByte()
                operation.addByte(varnum)
                
            self.push(self.stack[self.lv + varnum])
            

        elif opcode == OPCODE_INVOKEVIRTUAL:
            index = self.fetchWord()
            self.invoke_virtual(index)
            operation = Operation("invokevirtual").addWord(index)

        elif opcode == OPCODE_IOR:
            a = self.pop()
            b = self.pop()
            self.push(a or b)
            operation = Operation("ior")

        elif opcode == OPCODE_IRETURN:
            self.ireturn()
            operation = Operation("ireturn")

        elif opcode == OPCODE_ISTORE:
            operation = Operation("istore") #Different order because it is conditional
            if(self.wide):
                varnum = self.fetchWord()
                operation.addWord(varnum)
            else:
                varnum = self.fetchByte()
                operation.addByte(varnum)
            a = self.pop()
            self.stack[self.lv + varnum] = a

        elif opcode == OPCODE_ISUB:
            a = self.pop()
            b = self.pop()
            self.push(b - a)
            operation = Operation("isub")

        elif opcode == OPCODE_LDC_W:
            index = self.fetchWord()
            self.push(self.cpp[index])
            operation = Operation("ldc_w").addWord(index)

        elif opcode == OPCODE_NOP:
            operation = Operation("nop")
        
        elif opcode == OPCODE_POP:
            self.pop()
            operation = Operation("pop")

        elif opcode == OPCODE_SWAP:
            a = self.stack[self.sp]
            self.stack[self.sp] = self.stack[self.sp - 1]
            self.stack[self.sp - 1] = a
            operation = Operation("swap")

        elif opcode == OPCODE_WIDE:
            self.wide = True
            operation = Operation("wide")

        else:
            if opcode in self.customOpCodes.keys():
                operation = self.customOpCodes[opcode](self)
            
        if not opcode == OPCODE_WIDE:
            self.wide = False

        operation.setOpCode(opcode)
        return operation
    
    def active(self):
        return not self.pc == INITIAL_PC

    def print_result(self):
        print "return value: " + str(self.stack[self.sp])



if __name__ == "__main__":
    try:
        args = []
        if len(sys.argv) > 2:
            filename = sys.argv[1]
            args = sys.argv[2:]
        elif len(sys.argv) == 2:
            filename = sys.argv[1]
        else:
            print "What file do you want to open?"
            filename = raw_input("Filename>> ")
            print "Arguments to pass (seperated by spaces)"
            args = raw_input("").split(" ")
            
        image = IJVMImage()
        print ""
        image.load(filename, convertToDecimal=False, verbose=True)
        image.setArgs(args)
        
        ijvm = IJVM(image)
        ijvm.start()

        x = raw_input("Press enter to exit...")
    except IJVMException as e:
        print "------------------------------"
        print "IJVM Error:"
        print "------------------------------"
        print e
        print "------------------------------"
        x = raw_input("Press enter to exit...")
    except Exception as e:
        print "------------------------------"
        print "An error occured with python,"
        print "Please report this!"
        print "------------------------------"
        print e
        x = raw_input("Press enter to exit...")
