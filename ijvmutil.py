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
