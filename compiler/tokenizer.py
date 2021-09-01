#!/usr/bin/python3

import re
from constants import *

class Tokenizer:
    def __init__(self, infile):
        self._keywords = Keyword.list()
        self._symbols = Symbol.list()

        self._reComments = re.compile(r'//[^\n]*\n|/\*(.*?)\*/', re.MULTILINE|re.DOTALL)
        self._reWhitespace = re.compile(r'\s+')
        self._reKeywords = re.compile('|'.join([k for k in self._keywords]))
        self._reSymbols = re.compile('|'.join([re.escape(s) for s in self._symbols]))
        self._reIdentifier = re.compile("\w+")
        self._reIntConst = re.compile("\d+")
        self._reStringConst = re.compile(r'"[^"\n]*"')
        self._reTokens = re.compile('|'.join([
            self._reIdentifier.pattern,
            self._reKeywords.pattern,
            self._reSymbols.pattern,
            self._reIntConst.pattern,
            self._reStringConst.pattern]))

        self._tokens = self._readFile(infile)
        self._cursor = 0
        self._clear()

    # Initializing methods

    def _readFile(self, infile):
        f = open(infile, 'r')
        lines = f.read()
        f.close()

        lines = self._reComments.sub('', lines)
        lines = self._reWhitespace.sub(' ', lines)
        lines = lines.strip(' ')
        return self._reTokens.findall(lines)

    def _clear(self):
        self._tokenType = ''
        self._keyword = ''
        self._symbol = ''
        self._identifier = ''
        self._intVal = ''
        self._stringVal = ''

    # Public methods

    def hasMoreTokens(self):
        return len(self._tokens) > self._cursor

    def advance(self):
        token = self._tokens[self._cursor]

        if self._isKeyword(token):
            self._tokenType = TokenType.KEYWORD
            self._keyword = token.strip()
        elif self._isSymbol(token):
            self._tokenType = TokenType.SYMBOL
            self._symbol = token
        elif self._isIntConst(token):
            self._tokenType = TokenType.INT_CONST
            self._intVal = token
        elif self._isStringConst(token):
            self._tokenType = TokenType.STRING_CONST
            self._stringVal = token[1:-1]
        elif self._isIdentifier(token):
            self._tokenType = TokenType.IDENTIFIER
            self._identifier = token
        else:
            print("Unrecognized token:", token)

        self._cursor += 1

    def back(self):
        self._cursor -= 1

    def tokenType(self):
        return self._tokenType

    def keyword(self):
        return self._keyword
    
    def symbol(self):
        return self._symbol

    def identifier(self):
        return self._identifier

    def intVal(self):
        return self._intVal

    def stringVal(self):
        return self._stringVal

    # Conditional methods

    def _isKeyword(self, token):
        return token in Keyword.list()

    def _isSymbol(self, token):
        return self._reSymbols.match(token)

    def _isIdentifier(self, token):
        return self._reIdentifier.match(token)

    def _isIntConst(self, token):
        return self._reIntConst.match(token)

    def _isStringConst(self, token):
        return self._reStringConst.match(token)
