#!/usr/bin/python3

import os
import sys
import argparse
from constants import *
from tokenizer import Tokenizer

class Analyzer:
    def run(self, infile):
        outfile = self._outfile(infile, 'T')
        self._generateTokens(infile, outfile)

    def _outfile(self, infile, s=''):
        dirname = os.path.dirname(infile)
        filename = os.path.splitext(os.path.basename(infile))[0]
        return "{0}/out/{1}{2}.xml".format(dirname, filename, s)

    def _generateTokens(self, infile, outfile):
        out = open(outfile, 'w')
        out.write("<tokens>\n")

        tokenizer = Tokenizer(infile)
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            tokenType = tokenizer.tokenType()
            token = ''

            if tokenType == TokenType.KEYWORD:
                token = tokenizer.keyword()
            elif tokenType == TokenType.SYMBOL:
                token = tokenizer.symbol()
            elif tokenType == TokenType.IDENTIFIER:
                token = tokenizer.identifier()
            elif tokenType == TokenType.INT_CONST:
                token = tokenizer.intVal()
            elif tokenType == TokenType.STRING_CONST:
                token = tokenizer.stringVal()

            out.write("<{0}> {1} </{0}>\n".format(tokenType.value, token))

        out.write("</tokens>\n")
        out.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./analyzer.py <file>")
        sys.exit(2)

    analyzer = Analyzer()
    analyzer.run(sys.argv[1])
