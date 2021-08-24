#!/usr/bin/python3

import sys
import getopt
import os
import re
from parser import Parser
from command_type import CommandType
from code import Code
from symbol_table import SymbolTable


class Assembler:
    def __init__(self):
        self._symbolTable = SymbolTable()
        self._symbolAddress = 16
        self._reIsDecimal = re.compile(r"^@\d+$")

    def _outfile(self, infile):
        dir = os.path.dirname(infile)
        filename = os.path.splitext(os.path.basename(infile))[0]
        return dir + "/" + filename + ".hack"

    def _assembleC(self):
        comp = self._parser.comp()
        dest = self._parser.dest()
        jump = self._parser.jump()

        code = Code()
        return [1, 1, 1] + code.comp(comp) + code.dest(dest) + code.jump(jump)

    def _resolveSymbol(self):
        symbol = self._parser.symbol()
        commandType = self._parser.commandType()

        if commandType == CommandType.L_COMMAND:
            return self._symbolTable.getAddress(symbol[1:-1])

        if self._reIsDecimal.match(symbol):
            return symbol[1:]

        if not self._symbolTable.contains(symbol[1:]):
            self._symbolTable.addEntry(symbol[1:], self._symbolAddress)
            self._symbolAddress += 1

        return self._symbolTable.getAddress(symbol[1:])

    def _assembleA(self):
        symbol = self._resolveSymbol()
        binary = [int(bit) for bit in format(int(symbol), "b")]
        padding = [0] * (16 - len(binary))
        return padding + binary

    def _assembleInstruction(self):
        commandType = self._parser.commandType()
        if commandType == CommandType.C_COMMAND:
            return self._assembleC()
        elif commandType == CommandType.A_COMMAND:
            return self._assembleA()
        return None

    def _instructionPass(self, outfile):
        out = open(outfile, 'w')
        while self._parser.hasMoreCommands():
            self._parser.advance()
            instruction = self._assembleInstruction()
            if instruction is not None:
                out.write("".join(str(bit) for bit in instruction) + "\n")
        out.close()

    def _symbolPass(self):
        instructionAddress = 0
        while self._parser.hasMoreCommands():
            self._parser.advance()
            commandType = self._parser.commandType()
            if commandType in(CommandType.A_COMMAND, CommandType.C_COMMAND):
                instructionAddress += 1
            elif commandType == CommandType.L_COMMAND:
                symbol = self._parser.symbol()
                self._symbolTable.addEntry(symbol[1:-1], instructionAddress)

    def assemble(self, infile):
        self._parser = Parser(infile)
        self._symbolPass()
        self._parser.reset()
        outfile = self._outfile(infile)
        self._instructionPass(outfile)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Assembler.py -i <infile>")
        sys.exit(2)

    assembler = Assembler()
    assembler.assemble(sys.argv[1])
