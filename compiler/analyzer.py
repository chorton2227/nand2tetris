#!/usr/bin/python3

import os
import sys
import argparse
from constants import *
from tokenizer import Tokenizer
from compilation_engine import CompilationEngine
from xml.sax.saxutils import escape

class Analyzer:
    def run(self, infiles):
        for infile in infiles:
            print("Processing ", infile)
            tokenOut = self._outfile(infile, 'T')
            compileOut = self._outfile(infile)
            self._generateTokens(infile, tokenOut)
            self._compile(infile, compileOut)

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
                token = escape(tokenizer.symbol())
            elif tokenType == TokenType.IDENTIFIER:
                token = tokenizer.identifier()
            elif tokenType == TokenType.INT_CONST:
                token = tokenizer.intVal()
            elif tokenType == TokenType.STRING_CONST:
                token = tokenizer.stringVal()

            out.write("<{0}> {1} </{0}>\n".format(tokenType.value, token))

        out.write("</tokens>\n")
        out.close()

    def _compile(self, infile, outfile):
        compilationEngine = CompilationEngine(infile, outfile)
        compilationEngine.compile()

def printUsage():
    print("Usage: ./analyzer.py <dir|file>")

def getFiles(fpath):
    if fpath.endswith('.jack'):
        return [fpath]
    elif os.path.isdir(fpath):
        infiles = []
        for file in os.listdir(fpath):
            if file.endswith('.jack'):
                infiles.append(fpath + file)
        filename = os.path.basename(os.path.normpath(fpath))
        return infiles
    else:
        print("Invalid input given")
        printUsage()
        sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        printUsage()
        sys.exit(2)

    infiles = getFiles(sys.argv[1])
    analyzer = Analyzer()
    analyzer.run(infiles)
