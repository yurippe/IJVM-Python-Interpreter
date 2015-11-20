from ijvm import *
################
#Interpreter####
################
class IJVMInterpreter(IJVM):

    def __init__(self):

        def addLocals(interp):
            linkptr = interp.stack.stack[self.lv]
            linkptr += 1
            interp.stack.stack[self.lv] = linkptr
            interp.stack.stack = interp.stack.stack[:1] + [570] + interp.stack.stack[1:]
            interp.sp = interp.sp + 1
            return Operation("addlocal")
        
        self.customOpCodes = {0xEF: addLocals}
        self.customOpKeywords = {"ADDLOCAL":0xEF}
        self.stack = Stack()
        self.cpp = ConstantPool()
        self.method = MethodArea()

        #Set it to be 0 arguments 0 locals and a NOP, Add some more nops, so we have an empty buffer
        self.method.setMethodArea([0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.cpp.setConstantPool([0x00])
        self.stack.setStack([])
        
        self.sp = self.stack.getSize() - 1          
        self.lv = 0                 
        self.pc = INITIAL_PC
        self.wide = False

        self.initial_sp = self.sp;

        self.push(INITIAL_OBJ_REF)

        
        self.invoke_virtual(0)

    def fetchByte(self, signed=False):
        b = self.method[self.pc]
        self.pc = self.pc + 1
        return b

    def fetchWord(self, signed=False):
        return self.fetchByte(signed)
            
    def start(self):
        operCount = 0
        print str(Operation("Initial Stack")) + "\tstack = " + ", ".join(self.stack.getStack())
        print "----"
        while self.active():
            oldpc = self.pc
            inp = raw_input(">>")
            inp = inp.split(" ")
            if inp[0].upper() in KEYWORDS.keys():
                self.method.methodarea[self.pc] = KEYWORDS[inp[0].upper()]
                for i in range(len(inp) - 1):
                    self.method.methodarea[self.pc + i + 1] = int(inp[i+1])
            elif inp[0].upper() in self.customOpKeywords.keys():
                self.method.methodarea[self.pc] = self.customOpKeywords[inp[0].upper()]
                for i in range(len(inp) - 1):
                    self.method.methodarea[self.pc + i + 1] = int(inp[i+1])
            else:
                self.method.methodarea[self.pc] = 0x00 #NOP
                
            executedOperation = self.execute_opcode()
            print str(executedOperation) + "\tstack = " + ", ".join(self.stack.getStack())
            operCount += 1

            self.pc = oldpc

        self.print_result()
        print "Operations count: " + str(operCount)

if __name__ == "__main__":
    ijvmi = IJVMInterpreter()
    ijvmi.start()
