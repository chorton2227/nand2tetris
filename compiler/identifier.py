#!/usr/bin/python3

class Identifier:
    def __init__(self, type_, kind, index):
        self._type = type_
        self._kind = kind
        self._index = index

    def getType(self):
        return self._type

    def getKind(self):
        return self._kind

    def getIndex(self):
        return self._index
