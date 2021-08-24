# nand2tetris

Contains projects from [nand2tetris](https://www.nand2tetris.org).

## Assembler

Converts an assembly language into instruction sets for the cpu.
Assembler takes as input 1 asm file and outputs 1 hack file with the same name.

```
./assembler.py <asm file>
```

## VM Translator

Translates the intermediate vm language into assembly.
VM translator takes as input either 1 vm file or a directory containing multiple vm files.
Outputs 1 asm file.

```
./vm_translator.py <vm file|vm directory>
```

## Compiler

Compiles the high level jack language into the vm language.

## TODOs

* Build compiler
* Update README.md with compiler usage information
