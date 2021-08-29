#!/usr/bin/python3

from enum import Enum

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Keyword(ExtendedEnum):
    CLASS = 'class'
    METHOD = 'method'
    FUNCTION = 'function'
    CONSTRUCTOR = 'constructor'
    INT = 'int'
    BOOLEAN = 'boolean'
    CHAR = 'char'
    VOID = 'void'
    VAR = 'var'
    STATIC = 'static'
    FIELD = 'field'
    LET = 'let'
    DO = 'do'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    RETURN = 'return'
    TRUE = 'true'
    FALSE = 'false'
    NULL = 'null'
    THIS = 'this'

class Symbol(ExtendedEnum):
    OPEN_BRACE = '{'
    CLOSE_BRACE = '}'
    OPEN_PARENTHESIS = '('
    CLOSE_PARENTHESIS = ')'
    OPEN_BRACKET = '['
    CLOSE_BRACKET = ']'
    DOT = '.'
    COMMA = ','
    SEMICOLON = ';'
    PLUS = '+'
    HYPHEN = '-'
    ASTERISK = '*'
    SLASH = '/'
    AMPERSAND = '&'
    VERTICAL_BAR = '|'
    LESS_THAN = '<'
    GREATER_THAN = '>'
    EQUALS = '='
    TILDE = '~'

class TokenType(ExtendedEnum):
    KEYWORD = 'keyword'
    SYMBOL = 'symbol'
    IDENTIFIER = 'identifier'
    INT_CONST = 'integerConstant'
    STRING_CONST = 'stringConstant'
