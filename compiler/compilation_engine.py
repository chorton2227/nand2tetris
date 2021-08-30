#!/usr/bin/python3

from constants import *
from tokenizer import Tokenizer
from xml.sax.saxutils import escape

class CompilationEngine:

    # Intializing methods

    def __init__(self, infile, outfile):
        self._infile = infile
        self._outfile = outfile
        self._out = None
        self._tokenizer = Tokenizer(infile)

    # Public methods
    
    def compile(self):
        self._out =  open(self._outfile, 'w')
        self._compileClass()
        self._out.close()

    # Compile methods

    def _compileClass(self):
        self._outOpenNonTerminal(NonTerminal.CLASS)
        self._grammar(TokenType.KEYWORD, Keyword.CLASS)
        self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        while self._isClassVarDec():
            self._compileClassVarDec()
        while self._isSubroutineDec():
            self._compileSubroutineDec()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.CLASS)

    def _compileClassVarDec(self):
        self._outOpenNonTerminal(NonTerminal.CLASS_VAR_DEC)
        self._advance()
        self._grammarType()
        self._grammar(TokenType.IDENTIFIER)
        while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
            self._advance()
            self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.CLASS_VAR_DEC)

    def _compileSubroutineDec(self):
        self._outOpenNonTerminal(NonTerminal.SUBROUTINE_DEC)
        self._advance()
        self._grammarSubroutineReturnType()
        self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileParameterList()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)
        self._compileSubroutineBody()
        self._outCloseNonTerminal(NonTerminal.SUBROUTINE_DEC)

    def _compileParameterList(self):
        self._outOpenNonTerminal(NonTerminal.PARAMETER_LIST)
        self._compileParameter()
        while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
            self._advance()
            self._compileParameter()
        self._outCloseNonTerminal(NonTerminal.PARAMETER_LIST)

    def _compileParameter(self):
        if self._isType():
            self._advance()
            self._grammar(TokenType.IDENTIFIER)

    def _compileSubroutineBody(self):
        self._outOpenNonTerminal(NonTerminal.SUBROUTINE_BODY)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        while self._isVarDec():
            self._compileVarDec()
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.SUBROUTINE_BODY)

    def _compileVarDec(self):
        self._outOpenNonTerminal(NonTerminal.VAR_DEC)
        self._grammar(TokenType.KEYWORD, Keyword.VAR)
        self._grammarType()
        self._grammar(TokenType.IDENTIFIER)
        while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
            self._advance()
            self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.VAR_DEC)

    def _compileStatements(self):
        self._outOpenNonTerminal(NonTerminal.STATEMENTS)
        while self._isStatement():
            self._compileStatement()
        self._outCloseNonTerminal(NonTerminal.STATEMENTS)

    def _compileStatement(self):
        if self._isToken(TokenType.KEYWORD, Keyword.LET):
            self._compileLetStatement()
        elif self._isToken(TokenType.KEYWORD, Keyword.IF):
            self._compileIfStatement()
        elif self._isToken(TokenType.KEYWORD, Keyword.WHILE):
            self._compileWhileStatement()
        elif self._isToken(TokenType.KEYWORD, Keyword.DO):
            self._compileDoStatement()
        elif self._isToken(TokenType.KEYWORD, Keyword.RETURN):
            self._compileReturnStatement()

    def _compileLetStatement(self):
        self._outOpenNonTerminal(NonTerminal.LET_STATEMENT)
        self._advance()
        self._grammar(TokenType.IDENTIFIER)
        if self._isToken(TokenType.SYMBOL, Symbol.OPEN_BRACKET):
            self._advance()
            self._compileExpression()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACKET)
        self._grammar(TokenType.SYMBOL, Symbol.EQUALS)
        self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.LET_STATEMENT)

    def _compileIfStatement(self):
        self._outOpenNonTerminal(NonTerminal.IF_STATEMENT)
        self._advance()
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        if self._isToken(TokenType.KEYWORD, Keyword.ELSE):
            self._advance()
            self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
            self._compileStatements()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.IF_STATEMENT)

    def _compileWhileStatement(self):
        self._outOpenNonTerminal(NonTerminal.WHILE_STATEMENT)
        self._advance()
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.WHILE_STATEMENT)

    def _compileDoStatement(self):
        self._outOpenNonTerminal(NonTerminal.DO_STATEMENT)
        self._advance()
        self._grammar(TokenType.IDENTIFIER)
        self._compileSubroutineCall()
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.DO_STATEMENT)

    def _compileReturnStatement(self):
        self._outOpenNonTerminal(NonTerminal.RETURN_STATEMENT)
        self._advance()
        if self._isExpression():
            self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.RETURN_STATEMENT)

    def _compileExpression(self):
        self._outOpenNonTerminal(NonTerminal.EXPRESSION)
        self._compileTerm()
        while self._isOp():
            self._advance()
            self._compileTerm()
        self._outCloseNonTerminal(NonTerminal.EXPRESSION)

    def _compileTerm(self):
        self._outOpenNonTerminal(NonTerminal.TERM)
        if self._isTokenType(TokenType.INT_CONST):
            self._advance()
        elif self._isTokenType(TokenType.STRING_CONST):
            self._advance()
        elif self._isTokenType(TokenType.IDENTIFIER):
            self._advance()
            if self._isToken(TokenType.SYMBOL, Symbol.OPEN_BRACKET):
                self._advance()
                self._compileExpression()
                self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACKET)
            elif self._isToken(TokenType.SYMBOL, Symbol.DOT):
                self._compileSubroutineCall()
        elif self._isKeywordConstant():
            self._advance()
        elif self._isUnaryOp():
            self._advance()
            self._compileTerm()
        elif self._isToken(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS):
            self._advance()
            self._compileExpression()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)
        self._outCloseNonTerminal(NonTerminal.TERM)

    def _compileSubroutineCall(self):
        if self._isToken(TokenType.SYMBOL, Symbol.DOT):
            self._advance()
            self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpressionList()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)

    def _compileExpressionList(self):
        self._outOpenNonTerminal(NonTerminal.EXPRESSION_LIST)
        if self._isExpression():
            self._compileExpression()
            while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
                self._advance()
                self._compileExpression()
        self._outCloseNonTerminal(NonTerminal.EXPRESSION_LIST)

    # Out methods

    def _outTerminal(self, tokenType, token):
        if tokenType == TokenType.SYMBOL:
            token = escape(token)
        self._out.write("<{0}> {1} </{0}>\n".format(tokenType.value, token))

    def _outOpenNonTerminal(self, nonTerminal):
        self._out.write("<{0}>\n".format(nonTerminal.value))

    def _outCloseNonTerminal(self, nonTerminal):
        self._out.write("</{0}>\n".format(nonTerminal.value))

    # Tokenizer methods

    def _advance(self, out=True):
        if not self._tokenizer.hasMoreTokens():
            return None, None

        self._tokenizer.advance()
        tokenType = self._tokenizer.tokenType()
        token = ''

        if tokenType == TokenType.KEYWORD:
            token = self._tokenizer.keyword()
        elif tokenType == TokenType.SYMBOL:
            token = self._tokenizer.symbol()
        elif tokenType == TokenType.INT_CONST:
            token = self._tokenizer.intVal()
        elif tokenType == TokenType.STRING_CONST:
            token = self._tokenizer.stringVal()
        elif tokenType == TokenType.IDENTIFIER:
            token = self._tokenizer.identifier()

        if out: self._outTerminal(tokenType, token)
        return tokenType, token

    def _grammar(self, tokenType, token=None):
        tt, t = self._advance()
        if tokenType != tt or (token is not None and token.value != t):
            raise Exception("Unexpected token: {0}".format(t))

    def _grammarType(self):
        if self._isType():
            self._advance()
        else:
            raise Exception("Unexpected token: {0}".format(t))

    def _grammarSubroutineReturnType(self):
        if self._isToken(TokenType.KEYWORD, Keyword.VOID) or self._isType():
            self._advance()
        else:
            raise Exception("Unexpected token: {0}".format(t))

    def _inTokens(self, t, tokens):
        arr = []
        if isinstance(tokens, list):
            for token in tokens:
                arr.append(token.value)
        else:
            arr.append(tokens.value)
        return t in arr

    def _isTokenType(self, tokenType):
        tt, t = self._advance(False)
        self._tokenizer.back()
        return tt == tokenType

    def _isType(self):
        tokens = [Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN]
        tt, t = self._advance(False)
        self._tokenizer.back()
        return tt == TokenType.IDENTIFIER or (tt == TokenType.KEYWORD and self._inTokens(t, tokens))

    def _isStatement(self):
        tokens = [Keyword.LET, Keyword.IF, Keyword.WHILE, Keyword.DO, Keyword.RETURN]
        tt, t = self._advance(False)
        self._tokenizer.back()
        return tt == TokenType.KEYWORD and self._inTokens(t, tokens)

    def _isToken(self, tokenType, tokens): 
        tt, t = self._advance(False)
        self._tokenizer.back()
        return tt == tokenType and self._inTokens(t, tokens)

    def _isClassVarDec(self):
        tokens = [Keyword.STATIC, Keyword.FIELD]
        return self._isToken(TokenType.KEYWORD, tokens)

    def _isSubroutineDec(self):
        tokens = [Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD]
        return self._isToken(TokenType.KEYWORD, tokens)

    def _isVarDec(self):
        tokens = [Keyword.VAR]
        return self._isToken(TokenType.KEYWORD, tokens)

    def _isUnaryOp(self):
        symbolTokens = [
            Symbol.HYPHEN,
            Symbol.TILDE
        ]
        return self._isToken(TokenType.SYMBOL, symbolTokens)

    def _isOp(self):
        symbolTokens = [
            Symbol.PLUS,
            Symbol.HYPHEN,
            Symbol.ASTERISK,
            Symbol.SLASH,
            Symbol.AMPERSAND,
            Symbol.VERTICAL_BAR,
            Symbol.LESS_THAN,
            Symbol.GREATER_THAN,
            Symbol.EQUALS
        ]
        return self._isToken(TokenType.SYMBOL, symbolTokens)

    def _isKeywordConstant(self):
        keywordTokens = [
            Keyword.TRUE,
            Keyword.FALSE,
            Keyword.NULL,
            Keyword.THIS
        ]
        return self._isToken(TokenType.KEYWORD, keywordTokens)

    def _isTerm(self):
        return self._isUnaryOp() or \
            self._isKeywordConstant() or \
            self._isToken(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS) or \
            self._isTokenType(TokenType.INT_CONST) or \
            self._isTokenType(TokenType.STRING_CONST) or \
            self._isTokenType(TokenType.IDENTIFIER)

    def _isExpression(self):
        return self._isTerm()


























