from ijvm import *

MAX_INT = 2**3 - 1
img = IJVMImage()
img.load("geq.bc")

startx = - MAX_INT - 1
starty = - MAX_INT - 1

maxx = MAX_INT
maxy = MAX_INT

x = startx
y = starty


while x <= maxx:
    while y <= maxy:

        img.setArgs([x,y])
        ijvm = IJVM(img)
        val = ijvm.simulate()
        
        if x == y:
            if not val == 1:
                print "X=" + str(x) +";Y=" + str(y) + " gave: " + str(val) + " EXPECTED: 1"
        else:
            if not val == 0:
                print "X=" + str(x) +";Y=" + str(y) + " gave: " + str(val) + " EXPECTED: 0"

        print "X=" + str(x) + ";Y=" + str(y) + " " + str(x == y)
        y += 1
    x += 1
    y = starty
print "DONE"
