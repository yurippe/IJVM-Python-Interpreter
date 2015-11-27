from ijvm import *

img = IJVMImage()
img.load("geq.bc")

startx = -2147483648
starty = -2147483648

maxx = 2147483647
maxy = 2147483647

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


        y += 1
        print "X=" + str(x) + ";Y=" + str(y)
    x += 1
    y = starty
print "DONE"
