#!/usr/bin/python3

from constants import *
from identifier import Identifier

class IdentifierTable:
    def __init__(self):
        self._classScope = {} 
        self._subroutineScope = {}
        self._indexes = {
            VariableKind.STATIC: 0,
            VariableKind.FIELD: 0,
            VariableKind.ARG: 0,
            VariableKind.VAR: 0
        }

    def startSubroutine(self):
        self._subroutineScope = {} 
        self._indexes[VariableKind.ARG] = 0
        self._indexes[VariableKind.VAR] = 0

    def define(self, name, type_, kind):
        index = self._indexes[kind]
        self._indexes[kind] += 1
        identifier = Identifier(type_, kind, index)

        if kind in (VariableKind.STATIC, VariableKind.FIELD):
            self._classScope[name] = identifier
        elif kind in (VariableKind.ARG, VariableKind.VAR):
            self._subroutineScope[name] = identifier
        else:
            raise Exception("Invalid kind: {0}".format(kind))

    def varCount(self, kind):
        return self._indexes[kind]

    def kindOf(self, name):
        identifier = self.getIdentifier(name)
        if identifier is not None:
            return identifier.getKind()
        else:
            return None

    def typeOf(self, name):
        identifier = self.getIdentifier(name)
        if identifier is not None:
            return identifier.getType()
        else:
            return None

    def indexOf(self, name):
        identifier = self.getIdentifier(name)
        if identifier is not None:
            return identifier.getIndex()
        else:
            return None

    def getIdentifier(self, name):
        if name in self._subroutineScope:
            return self._subroutineScope[name]
        elif name in self._classScope:
            return self._classScope[name]
        else:
            return None
