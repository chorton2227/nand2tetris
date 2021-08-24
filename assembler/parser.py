#!/usr/bin/python3

import re
from command_type import CommandType


class Parser:
    def __init__(self, infile):
        self._reComments = re.compile("//.*$")
        self._reWhitespace = re.compile("\\s")
        self._lines = self._cleanFile(infile)
        self._cursor = 0
        self._clearParsedValues()

    def _cleanFile(self, infile):
        inf = open(infile, 'r')
        lines = inf.readlines()
        inf.close()

        cleanedLines = []
        for line in lines:
            cleanedLine = self._cleanLine(line)
            if cleanedLine is not None:
                cleanedLines.append(cleanedLine)
        return cleanedLines

    def _cleanLine(self, line):
        line = self._reComments.sub("", line)
        line = self._reWhitespace.sub("", line)
        return None if not line else line

    def _clearParsedValues(self):
        self._commandType = ""
        self._symbol = ""
        self._dest = ""
        self._comp = ""
        self._jump = ""

    def _currentLine(self):
        return self._lines[self._cursor]

    def _parseACommand(self):
        self._commandType = CommandType.A_COMMAND
        self._symbol = self._currentLine()

    def _parseLCommand(self):
        self._commandType = CommandType.L_COMMAND
        self._symbol = self._currentLine()

    def _parseCCommand(self):
        self._commandType = CommandType.C_COMMAND
        self._dest = self._parseDest()
        self._comp = self._parseComp()
        self._jump = self._parseJump()

    def _parseDest(self):
        line = self._currentLine()
        destEnd = line.find('=')
        return line[:destEnd] if destEnd > -1 else ""

    def _parseComp(self):
        line = self._currentLine()
        destEnd = line.find('=') + 1
        jumpStart = line.find(';')
        if jumpStart == -1:
            jumpStart = len(line)
        return line[destEnd:jumpStart]

    def _parseJump(self):
        line = self._currentLine()
        jumpStart = line.find(';') + 1
        return line[jumpStart:] if jumpStart > 0 else ""

    def _parseCurrentLine(self):
        self._clearParsedValues()

        line = self._currentLine()
        if line[0] == '@':
            self._parseACommand()
        elif line[0] == '(':
            self._parseLCommand()
        else:
            self._parseCCommand()

    def hasMoreCommands(self):
        return len(self._lines) > self._cursor

    def advance(self):
        self._parseCurrentLine()
        self._cursor += 1

    def reset(self):
        self._cursor = 0
        self._parseCurrentLine()

    def commandType(self):
        return self._commandType

    def symbol(self):
        return self._symbol

    def dest(self):
        return self._dest

    def comp(self):
        return self._comp

    def jump(self):
        return self._jump
