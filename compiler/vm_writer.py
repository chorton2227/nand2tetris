#!/usr/bin/python3

class VMWriter:
    def __init__(self, outfile):
        self._out = open(outfile, 'w')

    def writePush(self, segment, index):
        self._out.write("push {0} {1}\n".format(segment.value, index))

    def writePop(self, segment, index):
        self._out.write("pop {0} {1}\n".format(segment.value, index))

    def writeArithmetic(self, command):
        self._out.write("{0}\n".format(command.value))

    def writeLabel(self, label):
        self._out.write("label {0}\n".format(label))

    def writeGoto(self, label):
        self._out.write("goto {0}\n".format(label))

    def writeIf(self, label):
        self._out.write("if-goto {0}\n".format(label))

    def writeCall(self, name, nArgs):
        self._out.write("call {0} {1}\n".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        self._out.write("function {0} {1}\n".format(name, nLocals))

    def writeReturn(self):
        self._out.write("return\n")

    def close(self):
        self._out.close()
