#!/usr/bin/python3


class Code:
    def dest(self, dest):
        binary = [0] * 3
        if dest.find("A") > -1:
            binary[0] = 1
        if dest.find("D") > -1:
            binary[1] = 1
        if dest.find("M") > -1:
            binary[2] = 1
        return binary

    def comp(self, comp):
        comp_codes = {
            "0": [0, 1, 0, 1, 0, 1, 0],
            "1": [0, 1, 1, 1, 1, 1, 1],
            "-1": [0, 1, 1, 1, 0, 1, 0],
            "D": [0, 0, 0, 1, 1, 0, 0],
            "A": [0, 1, 1, 0, 0, 0, 0],
            "!D": [0, 0, 0, 1, 1, 0, 1],
            "!A": [0, 1, 1, 0, 0, 0, 1],
            "-D": [0, 0, 0, 1, 1, 1, 1],
            "-A": [0, 1, 1, 0, 0, 0, 1],
            "D+1": [0, 0, 1, 1, 1, 1, 1],
            "A+1": [0, 1, 1, 0, 1, 1, 1],
            "D-1": [0, 0, 0, 1, 1, 1, 0],
            "A-1": [0, 1, 1, 0, 0, 1, 0],
            "D+A": [0, 0, 0, 0, 0, 1, 0],
            "D-A": [0, 0, 1, 0, 0, 1, 1],
            "A-D": [0, 0, 0, 0, 1, 1, 1],
            "D&A": [0, 0, 0, 0, 0, 0, 0],
            "D|A": [0, 0, 1, 0, 1, 0, 1],
            "M": [1, 1, 1, 0, 0, 0, 0],
            "!M": [1, 1, 1, 0, 0, 0, 1],
            "-M": [1, 1, 1, 0, 0, 1, 1],
            "M+1": [1, 1, 1, 0, 1, 1, 1],
            "M-1": [1, 1, 1, 0, 0, 1, 0],
            "D+M": [1, 0, 0, 0, 0, 1, 0],
            "D-M": [1, 0, 1, 0, 0, 1, 1],
            "M-D": [1, 0, 0, 0, 1, 1, 1],
            "D&M": [1, 0, 0, 0, 0, 0, 0],
            "D|M": [1, 0, 1, 0, 1, 0, 1]
        }
        return comp_codes[comp]

    def jump(self, jump):
        if jump == "JGT":
            return [0, 0, 1]
        elif jump == "JEQ":
            return [0, 1, 0]
        elif jump == "JGE":
            return [0, 1, 1]
        elif jump == "JLT":
            return [1, 0, 0]
        elif jump == "JNE":
            return [1, 0, 1]
        elif jump == "JLE":
            return [1, 1, 0]
        elif jump == "JMP":
            return [1, 1, 1]
        else:
            return [0, 0, 0]
