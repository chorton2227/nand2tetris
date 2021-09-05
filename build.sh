#!/usr/bin/env bash

# Compile .jack to .vm
./compiler/compiler.py ./tetris/

# Compile os and copy files to tetris
./compiler/compiler.py ./os/
cp ./os/out/* ./tetris/out/ -r

# Translate .vm to .asm
./vm-translator/vm_translator.py ./tetris/out/

# Assemble .asm to .hack
./assembler/assembler.py ./tetris/out/*.asm
