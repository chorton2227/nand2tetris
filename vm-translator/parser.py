#!/usr/bin/python3

import re
from constants import *


class Parser:
    def __init__(self, infile):
        self._reComments = re.compile("//.*$")
        self._reWhitespace = re.compile(r"\s+")
        self._lines = self._readAndCleanLines(infile)
        self._cursor = 0
        self._clearParsedValues()

    def _readAndCleanLines(self, infile):
        cleanedLines = []

        f = open(infile, 'r')
        lines = f.readlines()

        for line in lines:
            line = self._reComments.sub('', line)
            line = self._reWhitespace.sub(' ', line)
            line = line.strip(" ")
            if line:
                cleanedLines.append(line)

        return cleanedLines

    def _clearParsedValues(self):
        self._commandType = ''
        self._arg1 = ''
        self._arg2 = ''

    def _currentLine(self):
        return self._lines[self._cursor]

    def _parseCurrentLine(self):
        self._clearParsedValues()
        line = self._currentLine()

        if line[:4] == 'push':
            self._commandType = C_PUSH
        elif line[:3] == 'pop':
            self._commandType = C_POP
        elif line[:5] == 'label':
            self._commandType = C_LABEL
        elif line[:4] == 'goto':
            self._commandType = C_GOTO
        elif line[:7] == 'if-goto':
            self._commandType = C_IF
        elif line[:8] == 'function':
            self._commandType = C_FUNCTION
        elif line[:6] == 'return':
            self._commandType = C_RETURN
        elif line[:4] == 'call':
            self._commandType = C_CALL
        else:
            self._commandType = C_ARITHMETIC

        if self._commandType == C_ARITHMETIC:
            self._arg1 = line
        else:
            chunks = line.split(' ')
            chunklen = len(chunks)
            if chunklen > 1:
                self._arg1 = chunks[1]
            if chunklen > 2:
                self._arg2 = int(chunks[2])

    def hasMoreCommands(self):
        return len(self._lines) > self._cursor

    def advance(self):
        self._parseCurrentLine()
        self._cursor += 1

    def reset(self):
        self._cursor = 0

    def commandType(self):
        return self._commandType

    def arg1(self):
        return self._arg1

    def arg2(self):
        return self._arg2
