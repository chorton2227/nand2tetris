#!/usr/bin/python3

import os
import sys
import argparse
from constants import *
from tokenizer import Tokenizer
from compilation_engine import CompilationEngine
from xml.sax.saxutils import escape

class Compiler:
    def run(self, infiles):
        for infile in infiles:
            print("Compiling...", infile)
            outfile = self._outfile(infile)
            compilationEngine = CompilationEngine(infile, outfile)
            compilationEngine.compile()

    def _outfile(self, infile, s=''):
        dirname = os.path.dirname(infile)
        filename = os.path.splitext(os.path.basename(infile))[0]
        return "{0}/out/{1}{2}.xml".format(dirname, filename, s)

def printUsage():
    print("Usage: ./compiler.py <dir|file>")

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
    compiler = Compiler()
    compiler.run(infiles)
