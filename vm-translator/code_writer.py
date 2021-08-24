#!/usr/bin/python3

from constants import *


class CodeWriter:
    def __init__(self, outfile):
        self._f = open(outfile, 'w')
        self._output = ''
        self._labelCount = 0
        self._returnAddressCount = 0
        self._currentClassName = ''
        self._memorySegments = {
            S_LCL:  R_LCL,
            S_ARG:  R_ARG,
            S_THIS: R_THIS,
            S_THAT: R_THAT,
        }
        self._registrySegments = {
            S_REG:  R_REG,
            S_PTR:  R_PTR,
            S_TEMP: R_TEMP
        }

    # Public methods

    def writeInit(self):
        # SP = 256
        self._aCommand(256)
        self._cCommand('D', 'A')
        self._setReg(R_SP)

        # Sys.init()
        self.writeCall('Sys.init', 0)

    def writeArithmetic(self, cmd):
        if cmd == 'add':
            self._binary('D+A')
        elif cmd == 'sub':
            self._binary('A-D')
        elif cmd == 'neg':
            self._unary('-D')
        elif cmd == 'eq':
            self._compare('JEQ')
        elif cmd == 'gt':
            self._compare('JGT')
        elif cmd == 'lt':
            self._compare('JLT')
        elif cmd == 'and':
            self._binary('D&A')
        elif cmd == 'or':
            self._binary('D|A')
        elif cmd == 'not':
            self._unary('!D')

    def writePushPop(self, cmd, seg, idx):
        if cmd == C_PUSH:
            self._push(seg, idx)
        elif cmd == C_POP:
            self._pop(seg, idx)

    def close(self):
        self._f.write(self._output)
        self._f.close()

    def writeLabel(self, label):
        self._lCommand(label)

    def writeGoto(self, label):
        self._aCommand(label)
        self._cCommand(None, '0', 'JMP')

    def writeIf(self, label):
        self._spDec()
        self._spRead('D')
        self._aCommand(label)
        self._cCommand(None, 'D', 'JNE')

    def writeCall(self, functionName, numArgs):
        # push return address
        returnAddress = self._newReturnAddress()
        self._push(S_CONST, returnAddress)

        # push LCL, ARG, THIS, THAT
        self._push(S_REG, R_LCL)
        self._push(S_REG, R_ARG)
        self._push(S_REG, R_THIS)
        self._push(S_REG, R_THAT)

        # ARG = SP - (numArgs + 5)
        self._aCommand(5)
        self._cCommand('D', 'A')
        if numArgs > 0:
            self._aCommand(numArgs)
            self._cCommand('D', 'D+A')
        self._aCommand(R_SP)
        self._cCommand('D', 'M-D')
        self._setReg(R_ARG)

        # LCL = SP
        self._aCommand(R_SP)
        self._cCommand('D', 'M')
        self._setReg(R_LCL)

        # goto functionName
        self._aCommand(functionName)
        self._cCommand(None, '0', 'JMP')

        # (return address)
        self._lCommand(returnAddress)

    def _setFrame(self):
        self._aCommand(R_LCL)
        self._cCommand('D', 'M')
        self._aCommand(R_FRAME)
        self._cCommand('M', 'D')

    def _frameToReg(self, reg, offset):
        self._aCommand(offset)
        self._cCommand('D', 'A')
        self._aCommand(R_FRAME)
        self._cCommand('A', 'M-D')
        self._cCommand('D', 'M')
        self._aCommand(reg)
        self._cCommand('M', 'D')

    def writeReturn(self):
        self._setFrame()            # FRAME = LCL
        self._frameToReg(R_RET, 5)  # RET = *(FRAME-5)

        # *ARG = pop()
        self._spDec()
        self._spRead('D')
        self._aCommand(R_ARG)
        self._cCommand('A', 'M')
        self._cCommand('M', 'D')

        # SP = ARG + 1
        self._aCommand(R_ARG)
        self._cCommand('D', 'M+1')
        self._aCommand(R_SP)
        self._cCommand('M', 'D')

        self._frameToReg(R_THAT, 1)  # THAT = *(FRAME-1)
        self._frameToReg(R_THIS, 2)  # THIS = *(FRAME-2)
        self._frameToReg(R_ARG, 3)  # ARG = *(FRAME-3)
        self._frameToReg(R_LCL, 4)  # LCL = *(FRAME-4)

        # goto RET
        self._aCommand(R_RET)
        self._cCommand('A', 'M')
        self._cCommand(None, '0', 'JMP')

    def writeFunction(self, functionName, numLocals):
        self._currentClassName = functionName[:functionName.find('.')]
        self._lCommand(functionName)
        for i in range(numLocals):
            self._pushConst(0)

    # Push/Pop

    def _push(self, seg, idx=0):
        if self._isConstSeg(seg):
            self._pushConst(idx)
        elif self._isMemSeg(seg):
            self._pushMem(seg, idx)
        elif self._isRegSeg(seg):
            self._pushReg(seg, idx)
        elif self._isStaticSeg(seg):
            self._pushStatic(idx)

    def _pop(self, seg, idx=0):
        if self._isMemSeg(seg):
            self._popMem(seg, idx)
        elif self._isRegSeg(seg):
            self._popReg(seg, idx)
        elif self._isStaticSeg(seg):
            self._popStatic(idx)

    def _isConstSeg(self, seg):
        return seg == S_CONST

    def _isMemSeg(self, seg):
        return seg in self._memorySegments.keys()

    def _isRegSeg(self, seg):
        return seg in self._registrySegments.keys()

    def _isStaticSeg(self, seg):
        return seg == S_STATIC

    def _segAddr(self, seg):
        return self._memorySegments[seg]

    def _segReg(self, seg, idx):
        return self._registrySegments[seg] + idx

    # Write to output

    def _write(self, *args):
        for arg in args:
            self._output += str(arg)
        self._output += "\n"

    def _aCommand(self, addr):
        self._write('@', addr)

    def _cCommand(self, dest, comp, jump=None):
        args = []
        if dest:
            args.append(dest)
            args.append('=')
        args.append(comp)
        if jump:
            args.append(';')
            args.append(jump)
        self._write(*args)

    def _lCommand(self, label):
        self._write('(', label, ')')

    # Labels and jumps

    def _newLabel(self):
        label = "LABEL" + str(self._labelCount)
        self._labelCount += 1
        return label

    def _newJump(self, comp, jump):
        label = self._newLabel()
        self._aCommand(label)
        self._cCommand(None, comp, jump)
        return label

    def _newReturnAddress(self):
        label = "RETURN" + str(self._labelCount)
        self._labelCount += 1
        return label

    # SP operations

    def _spLoad(self):
        self._aCommand(R_SP)
        self._cCommand('A', 'M')

    def _spRead(self, to):
        self._spLoad()
        self._cCommand(to, 'M')

    def _spWrite(self):
        self._spLoad()
        self._cCommand('M', 'D')

    def _spInc(self):
        self._aCommand(R_SP)
        self._cCommand('M', 'M+1')

    def _spDec(self):
        self._aCommand(R_SP)
        self._cCommand('M', 'M-1')

    # Arithmetic and logical operations

    def _binary(self, comp):
        self._spDec()
        self._spRead('D')
        self._spDec()
        self._spRead('A')
        self._cCommand('D', comp)
        self._spWrite()
        self._spInc()

    def _unary(self, comp):
        self._spDec()
        self._spRead('D')
        self._cCommand('D', comp)
        self._spWrite()
        self._spInc()

    def _compare(self, jump):
        self._spDec()
        self._spRead('D')
        self._spDec()
        self._spRead('A')
        self._cCommand('D', 'A-D')
        labelTrue = self._newJump('D', jump)
        self._cCommand('D', '0')
        self._spWrite()
        labelFalse = self._newJump('0', 'JMP')
        self._lCommand(labelTrue)
        self._cCommand('D', '-1')
        self._spWrite()
        self._lCommand(labelFalse)
        self._spInc()

    # Memory access operations

    def _staticSymbol(self, idx):
        return self._currentClassName + '.' + str(idx)

    def _setReg(self, reg, comp='D'):
        self._aCommand(reg)
        self._cCommand('M', comp)

    def _getReg(self, reg, dest):
        self._aCommand(reg)
        self._cCommand(dest, 'M')

    def _loadSeg(self, addr, idx, dest='D', indirect=False):
        if idx > 0:
            self._aCommand(idx)
            self._cCommand('D', 'A')
        self._aCommand(addr)
        if indirect:
            if idx > 0:
                self._cCommand('A', 'D+M')
            else:
                self._cCommand('A', 'M')
            self._cCommand(dest, 'M')
        else:
            if idx > 0:
                self._cCommand(dest, 'D+M')
            else:
                self._cCommand(dest, 'M')

    def _pushConst(self, value):
        self._aCommand(value)
        self._cCommand('D', 'A')
        self._spWrite()
        self._spInc()

    def _pushMem(self, seg, idx):
        addr = self._segAddr(seg)
        self._loadSeg(addr, idx, indirect=True)
        self._spWrite()
        self._spInc()

    def _popMem(self, seg, idx):
        addr = self._segAddr(seg)
        self._spDec()
        self._loadSeg(addr, idx)
        self._setReg(R_13)
        self._spRead('D')
        self._getReg(R_13, 'A')
        self._cCommand('M', 'D')

    def _pushReg(self, seg, idx):
        reg = self._segReg(seg, idx)
        self._getReg(reg, 'D')
        self._spWrite()
        self._spInc()

    def _popReg(self, seg, idx):
        reg = self._segReg(seg, idx)
        self._spDec()
        self._spRead('D')
        self._setReg(reg)

    def _pushStatic(self, idx):
        symbol = self._staticSymbol(idx)
        self._aCommand(symbol)
        self._cCommand('D', 'M')
        self._spWrite()
        self._spInc()

    def _popStatic(self, idx):
        symbol = self._staticSymbol(idx)
        self._spDec()
        self._spRead('D')
        self._aCommand(symbol)
        self._cCommand('M', 'D')
