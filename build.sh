#!/usr/bin/env bash

# Compile .jack to .vm
./compiler/compiler.py ./tetris/

# Translate .vm to .asm
./vm-translator/vm_translator.py ./tetris/out/

# Assemble .asm to .hack
./assembler/assembler.py ./tetris/out/*.asm
