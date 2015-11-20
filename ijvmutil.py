MEMORY_SIZE = 640 << 10
INITIAL_OBJ_REF = 42
INITIAL_PC = 1

OPCODE_BIPUSH = 0x10
OPCODE_DUP = 0x59
OPCODE_GOTO = 0xA7
OPCODE_IADD = 0x60
OPCODE_IAND = 0x7E
OPCODE_IFEQ = 0x99
OPCODE_IFLT = 0x9B
OPCODE_IF_ICMPEQ = 0x9F
OPCODE_IINC = 0x84
OPCODE_ILOAD = 0x15
OPCODE_INVOKEVIRTUAL = 0xB6
OPCODE_IOR = 0x80
OPCODE_IRETURN = 0xAC
OPCODE_ISTORE = 0x36
OPCODE_ISUB = 0x64
OPCODE_LDC_W = 0x13
OPCODE_NOP = 0x00
OPCODE_POP = 0x57
OPCODE_SWAP = 0x5F
OPCODE_WIDE = 0xC4

class Operation(object):

    def __init__(self, name):
        self.name = name
        self.operations = []#list of bytes
        self.voperations = []
        self.description = ""
        self.opcode = ""

        self.str_format = "{0:<9}\t\t{1:<9}"

    def setFormat(self, f):
        self.str_format = f
        return self
        
    def addByte(self, b, signed=False):
        if signed and b < 0:
            b = b + 256
        bait = str(hex(b))[2:]
        while len(bait) < 2:
            bait = "0" + bait
        self.operations += [bait[i:i+2] for i in range(0, len(bait), 2)]
        self.voperations.append(str(b))
        return self #allows for method chaining, so very pythonic
        
    def addWord(self, w, signed=False):
        if signed and w < 0:
            w = w + 65536
        word = str(hex(w))[2:]
        while len(word) < 4:
            word = "0" + word
        self.operations += [word[i:i+2] for i in range(0, len(word), 2)]
        self.voperations.append(str(w))
        return self #allows for method chaining, so very pythonic

    def setDescription(self, txt):
        self.description = txt
        return self

    def setOpCode(self, code):
        opc = str(hex(code))[2:]
        while len(opc) < 2:
            opc = "0" + opc
        self.opcode = str(opc)
        return self

    def __str__(self):
        if len(self.operations) > 0 or not self.opcode == "": lside = "["; rside = "]"
        else: lside = ""; rside = ""
        return self.str_format.format(self.name + " " + " ".join(self.voperations),
               lside + " ".join([self.opcode] + self.operations) + rside)                   

    
class Method_Area(object):

    def __init__(self):
        self.method_area = []

    def getSize(self):
        return len(self.method_area)

class Constant_Pool(object):

    def __init__(self):
        self.constant_pool = []

    def getSize(self):
        return len(self.constant_pool)

class IJVMImage(object):

    def __init__(self):

        self.main_index = 0
        self.method_area = Method_Area()
        self.method_area_size = self.method_area.getSize()
        self.constant_pool = Constant_Pool()
        self.constant_pool_size = self.constant_pool.getSize()
        self.args = []

    def getMainIndex(self):
        return self.main_index

    def getMethodArea(self):
        return self.method_area
    def getConstantPool(self):
        return self.constant_pool
    def getArguments(self):
        return self.args
