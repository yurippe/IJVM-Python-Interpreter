ALLOW_OVERFLOWS = False
MAX_INT = 2147483647 #Signed 32 bit integer

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

KEYWORDS = {"BIPUSH":OPCODE_BIPUSH, "DUP":OPCODE_DUP, "GOTO":OPCODE_GOTO, "IADD":OPCODE_IADD,
            "IAND":OPCODE_IAND, "IFEQ":OPCODE_IFEQ, "IFLT":OPCODE_IFLT, "IF_ICMPEQ":OPCODE_IF_ICMPEQ,
            "IINC":OPCODE_IINC, "ILOAD":OPCODE_ILOAD, "INVOKEVIRTUAL":OPCODE_INVOKEVIRTUAL,
            "IOR":OPCODE_IOR, "IRETURN":OPCODE_IRETURN, "ISTORE":OPCODE_ISTORE, "ISUB":OPCODE_ISUB,
            "LDC_W":OPCODE_LDC_W, "NOP":OPCODE_NOP, "POP":OPCODE_POP, "SWAP":OPCODE_SWAP, "WIDE":OPCODE_WIDE
            }

def int_overflow(val, maxint=2147483647):
    #maxint is the UPPER BOUND (usually ((2^x)-1))
    #default is set to a signed 32 bit int
    if not -maxint-1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val

class IJVMException(Exception):
    pass

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
        vb = b
        if signed and b < 0:
            b = b + 256
        bait = str(hex(b))[2:]
        while len(bait) < 2:
            bait = "0" + bait
        self.operations += [bait[i:i+2] for i in range(0, len(bait), 2)]
        self.voperations.append(str(vb))
        return self #allows for method chaining, so very pythonic
        
    def addWord(self, w, signed=False):
        vw = w
        if signed and w < 0:
            w = w + 65536
        word = str(hex(w))[2:]
        while len(word) < 4:
            word = "0" + word
        self.operations += [word[i:i+2] for i in range(0, len(word), 2)]
        self.voperations.append(str(vw))
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


class IJVMImage(object):

    def __init__(self):

        self.main_index = 0
        self.method_area = []
        self.method_area_size = len(self.method_area)
        self.constant_pool = []
        self.constant_pool_size = len(self.constant_pool)
        self.args = []
        
    def load(self, filename, convertToDecimal=True, verbose=False):
        with open(filename, "r") as f:
            content = f.read()

        ci = 0
        f1 = "main index: "
        f2 = "\n"
        i = content.find(f1, ci)
        ci = content.find(f2, i)
        self.main_index = int(content[i + len(f1):ci])
    
        f1 = "method area: "
        f2 = " bytes\n"
        i = content.find(f1, ci)
        ci = content.find(f2, i)
        self.method_area_size = int(content[i + len(f1):ci])

        i = ci + len(f2)
        while len(self.method_area) < self.method_area_size:
            if convertToDecimal:
                cont = int(content[i:i+2], base=16)
            else:
                cont = content[i:i+2]
            self.method_area.append(cont)
            i += 3

        f1 = "constant pool: "
        f2 = " words\n"
        i = content.find(f1, i)
        ci = content.find(f2, i)
        self.constant_pool_size = int(content[i + len(f1):ci])

        i = ci + len(f2)
        
        while len(self.constant_pool) < self.constant_pool_size:
            if convertToDecimal:
                cont = int(content[i:i+8], base=16)
            else:
                cont = content[i:i+8]
            self.constant_pool.append(cont)
            i += 9
        if verbose:   
            print "Main index: " + str(self.main_index)
            print "Method area size: " + str(self.method_area_size)
            print "Method Area: "
            for i in range(len(self.method_area)/16 + 1):
                print " ".join(self.method_area[i*16:(i+1)*16])
            print "Constant pool size: " + str(self.constant_pool_size)
            print "Constant pool: "
            print ", ".join(self.constant_pool)
            print "\n"

    def setArgs(self, args):
        self.args = [int(arg) for arg in args]
        
    def getMainIndex(self):
        return self.main_index

    def getMethodArea(self):
        return self.method_area
    def getConstantPool(self):
        return self.constant_pool
    def getArguments(self):
        return self.args

if __name__ == "__main__":

    img = IJVMImage()
    img.load("test.bc", False, True)
