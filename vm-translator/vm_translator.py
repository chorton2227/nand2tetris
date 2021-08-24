#!/usr/bin/python3

import sys
import os
from constants import *
from parser import Parser
from code_writer import CodeWriter


class VMTranslator:
    def translate(self, vmfiles, outfile):
        codewriter = CodeWriter(outfile)
        codewriter.writeInit()
        for vmfile in vmfiles:
            self._translateVmFile(vmfile, codewriter)
        codewriter.close()

    def _translateVmFile(self, vmfile, codewriter):
        parser = Parser(vmfile)
        while parser.hasMoreCommands():
            parser.advance()
            commandType = parser.commandType()
            arg1 = parser.arg1()
            arg2 = parser.arg2()

            if commandType == C_ARITHMETIC:
                codewriter.writeArithmetic(arg1)
            elif commandType == C_PUSH or commandType == C_POP:
                codewriter.writePushPop(commandType, arg1, arg2)
            elif commandType == C_LABEL:
                codewriter.writeLabel(arg1)
            elif commandType == C_GOTO:
                codewriter.writeGoto(arg1)
            elif commandType == C_IF:
                codewriter.writeIf(arg1)
            elif commandType == C_CALL:
                codewriter.writeCall(arg1, arg2)
            elif commandType == C_RETURN:
                codewriter.writeReturn()
            elif commandType == C_FUNCTION:
                codewriter.writeFunction(arg1, arg2)
            else:
                print("Unrecognized command", commandType)


def printUsage():
    print("Usage: ./vm-translator.py <dir|file>")


def getFiles(fpath):
    if fpath.endswith('.vm'):
        return [fpath], '.asm'.join(fpath.rsplit('.vm', 1))
    elif os.path.isdir(fpath):
        vmfiles = []
        for file in os.listdir(fpath):
            if file.endswith('.vm'):
                vmfiles.append(fpath + file)
        filename = os.path.basename(os.path.normpath(fpath))
        outfile = fpath + '/' + filename + '.asm'
        return vmfiles, outfile
    else:
        print("Invalid input given")
        printUsage()
        sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(2)

    vmfiles, outfile = getFiles(sys.argv[1])
    vmtranslator = VMTranslator()
    vmtranslator.translate(vmfiles, outfile)
