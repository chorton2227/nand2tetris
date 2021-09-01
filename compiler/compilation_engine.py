#!/usr/bin/python3

from constants import *
from identifier import Identifier
from identifier_table import IdentifierTable
from tokenizer import Tokenizer
from vm_writer import VMWriter
from xml.sax.saxutils import escape

class CompilationEngine:

    # Intializing methods

    def __init__(self, infile, outfile):
        self._infile = infile
        self._outfile = outfile
        self._out = None
        self._tokenizer = Tokenizer(infile)
        self._identifierTable = IdentifierTable()
        self._className = ''
        self._subroutineName = ''
        self._subroutineType = ''
        self._subroutineReturnType = ''
        self._numExpressions = 0
        self._numLabels = 0

    # Public methods
    
    def compile(self):
        self._vmWriter = VMWriter(self._outfile.replace('.xml', '.vm'))
        self._out =  open(self._outfile, 'w')
        self._compileClass()
        self._vmWriter.close()
        self._out.close()

    # Compile methods

    def _compileClass(self):
        self._outOpenNonTerminal(NonTerminal.CLASS)
        self._grammar(TokenType.KEYWORD, Keyword.CLASS)
        _, self._className = self._grammar(TokenType.IDENTIFIER)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        while self._isClassVarDec():
            self._compileClassVarDec()
        while self._isSubroutineDec():
            self._compileSubroutineDec()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.CLASS)

    def _compileClassVarDec(self):
        self._outOpenNonTerminal(NonTerminal.CLASS_VAR_DEC)

        # Class variable kind
        _, kindT = self._advance()
        kind = VariableKind(kindT)

        # Define class variables
        _, type_ = self._grammarType()
        _, name = self._grammar(TokenType.IDENTIFIER)
        self._identifierTable.define(name, type_, kind)
        while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
            _, type_ = self._advance()
            _, name = self._grammar(TokenType.IDENTIFIER)
            self._identifierTable.define(name, type_, kind)

        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.CLASS_VAR_DEC)

    def _compileSubroutineDec(self):
        self._identifierTable.startSubroutine()
        if self._isVmMethodOnly():
            self._identifierTable.define(Keyword.THIS.value, self._className, VariableKind.ARG)

        self._outOpenNonTerminal(NonTerminal.SUBROUTINE_DEC)
        _, self._subroutineType = self._advance()
        _, self._subroutineReturnType = self._grammarSubroutineReturnType()
        _, self._subroutineName = self._grammar(TokenType.IDENTIFIER)
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
            _, type_ = self._advance()
            _, name = self._grammar(TokenType.IDENTIFIER)
            self._identifierTable.define(name, type_, VariableKind.ARG)

    def _compileSubroutineBody(self):
        self._outOpenNonTerminal(NonTerminal.SUBROUTINE_BODY)
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        while self._isVarDec():
            self._compileVarDec()
        self._vmFunction()
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.SUBROUTINE_BODY)

    def _compileVarDec(self):
        self._outOpenNonTerminal(NonTerminal.VAR_DEC)

        # Define local variables
        self._grammar(TokenType.KEYWORD, Keyword.VAR)
        _, type_ = self._grammarType()
        _, name = self._grammar(TokenType.IDENTIFIER)
        self._identifierTable.define(name, type_, VariableKind.VAR)
        while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
            self._advance()
            _, name = self._grammar(TokenType.IDENTIFIER)
            self._identifierTable.define(name, type_, VariableKind.VAR)

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

        # Resolve identifier
        _, name = self._grammar(TokenType.IDENTIFIER)
        kind = self._identifierTable.kindOf(name)
        segment = self._kindToSegment(kind)
        index = self._identifierTable.indexOf(name)

        # Handle array
        isArray = self._isToken(TokenType.SYMBOL, Symbol.OPEN_BRACKET)
        if isArray:
            self._advance()
            self._compileExpression()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACKET)
            self._vmWriter.writePush(segment, index)
            self._vmWriter.writeArithmetic(VMOp.ADD)

        self._grammar(TokenType.SYMBOL, Symbol.EQUALS)
        self._compileExpression()

        # Assign variable
        if isArray:
            self._vmWriter.writePop(Segment.TEMP, 0)
            self._vmWriter.writePop(Segment.PTR, 1)
            self._vmWriter.writePush(Segment.TEMP, 0)
            self._vmWriter.writePop(Segment.THAT, 0)
        else:
            self._vmWriter.writePop(segment, index)

        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.LET_STATEMENT)

    def _compileIfStatement(self):
        # Goto labels
        ifGoto = self._newLabel()
        elseGoto = self._newLabel()
        endGoto = self._newLabel()

        self._outOpenNonTerminal(NonTerminal.IF_STATEMENT)
        self._advance()
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)

        # Goto if or else
        self._vmWriter.writeIf(ifGoto)
        self._vmWriter.writeGoto(elseGoto)
        self._vmWriter.writeLabel(ifGoto)

        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)

        # Goto end or start else
        self._vmWriter.writeGoto(endGoto)
        self._vmWriter.writeLabel(elseGoto)

        if self._isToken(TokenType.KEYWORD, Keyword.ELSE):
            self._advance()
            self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
            self._compileStatements()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.IF_STATEMENT)

        # End
        self._vmWriter.writeLabel(endGoto)

    def _compileWhileStatement(self):
        self._outOpenNonTerminal(NonTerminal.WHILE_STATEMENT)

        # While labels
        whileExp = self._newLabel()
        whileEnd = self._newLabel()

        # Label while expression evaluation
        self._vmWriter.writeLabel(whileExp)
        self._advance()
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)

        # Evaluate expression
        self._vmWriter.writeArithmetic(VMOp.NOT)
        self._vmWriter.writeIf(whileEnd)

        # While body
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_BRACE)
        self._compileStatements()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACE)
        self._outCloseNonTerminal(NonTerminal.WHILE_STATEMENT)

        # Goto expression or end
        self._vmWriter.writeGoto(whileExp)
        self._vmWriter.writeLabel(whileEnd)

    def _compileDoStatement(self):
        self._outOpenNonTerminal(NonTerminal.DO_STATEMENT)
        self._advance()
        _, t = self._grammar(TokenType.IDENTIFIER)
        self._compileSubroutineCall(t)
        self._vmWriter.writePop(Segment.TEMP, 0)
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.DO_STATEMENT)

    def _compileReturnStatement(self):
        self._outOpenNonTerminal(NonTerminal.RETURN_STATEMENT)
        self._advance()
        if self._isExpression():
            self._compileExpression()
        self._grammar(TokenType.SYMBOL, Symbol.SEMICOLON)
        self._outCloseNonTerminal(NonTerminal.RETURN_STATEMENT)

        # Write return
        if self._subroutineReturnType == Keyword.VOID.value:
            self._vmWriter.writePush(Segment.CONST, 0)
        self._vmWriter.writeReturn()

    def _compileExpression(self):
        self._outOpenNonTerminal(NonTerminal.EXPRESSION)
        self._compileTerm()
        while self._isOp():
            _, op = self._advance()
            self._compileTerm()
            self._vmOp(op)
        self._outCloseNonTerminal(NonTerminal.EXPRESSION)

    def _compileTerm(self):
        self._outOpenNonTerminal(NonTerminal.TERM)
        if self._isTokenType(TokenType.INT_CONST):
            _, t = self._advance()
            self._vmWriter.writePush(Segment.CONST, t)
        elif self._isTokenType(TokenType.STRING_CONST):
            _, t = self._advance()
            l = len(t)
            self._vmWriter.writePush(Segment.CONST, l)
            self._vmWriter.writeCall('String.new', 1)
            for i in range(l):
                self._vmWriter.writePush(Segment.CONST, ord(t[i]))
                self._vmWriter.writeCall('String.appendChar', 2)
        elif self._isTokenType(TokenType.IDENTIFIER):
            _, t = self._advance()
            identifier = self._identifierTable.getIdentifier(t)
            if identifier is not None and not self._isToken(TokenType.SYMBOL, Symbol.DOT):
                segment = self._kindToSegment(identifier.getKind())
                index = identifier.getIndex()

                isArray = self._isToken(TokenType.SYMBOL, Symbol.OPEN_BRACKET)
                if isArray:
                    self._advance()
                    self._compileExpression()
                    self._grammar(TokenType.SYMBOL, Symbol.CLOSE_BRACKET)

                self._vmWriter.writePush(segment, index)
                if isArray:
                    self._vmWriter.writeArithmetic(VMOp.ADD)
                    self._vmWriter.writePop(Segment.PTR, 1)
                    self._vmWriter.writePush(Segment.THAT, 0)
            else:
                self._compileSubroutineCall(t)
        elif self._isKeywordConstant():
            _, t = self._advance()
            if t in (Keyword.NULL.value, Keyword.FALSE.value):
                self._vmWriter.writePush(Segment.CONST, 0)
            elif t == Keyword.TRUE.value:
                self._vmWriter.writePush(Segment.CONST, 0)
                self._vmWriter.writeArithmetic(VMOp.NOT)
            elif t == Keyword.THIS.value:
                self._vmWriter.writePush(Segment.PTR, 0)
        elif self._isUnaryOp():
            _, t = self._advance()
            self._compileTerm()
            self._vmUnaryOp(t)
        elif self._isToken(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS):
            self._advance()
            self._compileExpression()
            self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)
        self._outCloseNonTerminal(NonTerminal.TERM)

    def _compileSubroutineCall(self, subroutine):
        #TODO
        nArgs = 0

        # Swap identifier with type
        identifier = self._identifierTable.getIdentifier(subroutine)
        if identifier is not None:
            segment = self._kindToSegment(identifier.getKind())
            index = identifier.getIndex()
            subroutine = identifier.getType()
            self._vmWriter.writePush(segment, index)
            nArgs += 1

        # Subroutine to call
        if self._isToken(TokenType.SYMBOL, Symbol.DOT):
            self._advance()
            _, id1 = self._grammar(TokenType.IDENTIFIER)
            subroutine = "{0}.{1}".format(subroutine, id1)
        else:
            subroutine = "{0}.{1}".format(self._className, subroutine)

        # Pass this to arg0 for class methods
        if (self._isVmConstructor() or self._isVmMethodOnly()) and \
            subroutine.startswith(self._className):
                self._vmWriter.writePush(Segment.PTR, 0)
                nArgs += 1

        # Compile expressions
        self._numExpressions = 0
        self._grammar(TokenType.SYMBOL, Symbol.OPEN_PARENTHESIS)
        self._compileExpressionList()
        self._grammar(TokenType.SYMBOL, Symbol.CLOSE_PARENTHESIS)

        # Call subroutine
        nArgs += self._numExpressions
        self._vmWriter.writeCall(subroutine, nArgs)

    def _compileExpressionList(self):
        self._outOpenNonTerminal(NonTerminal.EXPRESSION_LIST)
        if self._isExpression():
            self._numExpressions += 1
            self._compileExpression()
            while self._isToken(TokenType.SYMBOL, Symbol.COMMA):
                self._numExpressions += 1
                self._advance()
                self._compileExpression()
        self._outCloseNonTerminal(NonTerminal.EXPRESSION_LIST)

    # VM Writer methods

    def _newLabel(self):
        label = "LABEL{0}".format(self._numLabels)
        self._numLabels += 1
        return label

    def _isVmConstructor(self):
        return self._subroutineType == Keyword.CONSTRUCTOR.value

    def _isVmMethodOnly(self):
        return self._subroutineType == Keyword.METHOD.value

    def _isVmMethod(self):
        if self._className == "Main":
            return False
        elif self._subroutineType == Keyword.FUNCTION.value:
            return False
        #elif self._subroutineReturnType == Keyword.VOID.value:
        #    return False
        else:
            return True

    def _vmSubroutineName(self):
        return "{0}.{1}".format(self._className, self._subroutineName)

    def _kindToSegment(self, kind):
        if kind == VariableKind.STATIC:
            return Segment.STATIC
        elif kind == VariableKind.FIELD:
            return Segment.THIS # todo?
        elif kind == VariableKind.ARG:
            return Segment.ARG
        elif kind == VariableKind.VAR:
            return Segment.LOCAL
        else:
            return None

    def _vmFunction(self):
        name = self._vmSubroutineName()
        nLocals = self._identifierTable.varCount(VariableKind.VAR)
        self._vmWriter.writeFunction(name, nLocals)

        if self._isVmConstructor():
            nFields = self._identifierTable.varCount(VariableKind.FIELD)
            if nFields > 0:
                self._vmWriter.writePush(Segment.CONST, nFields)
                self._vmWriter.writeCall('Memory.alloc', 1)
                self._vmWriter.writePop(Segment.PTR, 0)

        #nArgs = self._identifierTable.varCount(VariableKind.ARG)
        #if nArgs > 0:
        #    self._vmWriter.writePush(Segment.CONST, nArgs)
        #    self._vmWriter.writeCall('Memory.alloc', 1)
        #    self._vmWriter.writePop(Segment.PTR, 0)

        if self._isVmMethodOnly():
            self._vmWriter.writePush(Segment.ARG, 0)
            self._vmWriter.writePop(Segment.PTR, 0)

    def _vmOp(self, op):
        if op == Symbol.PLUS.value:
            self._vmWriter.writeArithmetic(VMOp.ADD)
        elif op == Symbol.LESS_THAN.value:
            self._vmWriter.writeArithmetic(VMOp.LT)
        elif op == Symbol.GREATER_THAN.value:
            self._vmWriter.writeArithmetic(VMOp.GT)
        elif op == Symbol.HYPHEN.value:
            self._vmWriter.writeArithmetic(VMOp.SUB)
        elif op == Symbol.AMPERSAND.value:
            self._vmWriter.writeArithmetic(VMOp.AND)
        elif op == Symbol.VERTICAL_BAR.value:
            self._vmWriter.writeArithmetic(VMOp.OR)
        elif op == Symbol.EQUALS.value:
            self._vmWriter.writeArithmetic(VMOp.EQ)
        elif op == Symbol.ASTERISK.value:
            self._vmWriter.writeCall('Math.multiply', 2)
        elif op == Symbol.SLASH.value:
            self._vmWriter.writeCall('Math.divide', 2)

    def _vmUnaryOp(self, unaryOp):
        if unaryOp == Symbol.HYPHEN.value:
            self._vmWriter.writeArithmetic(VMOp.NEG)
        elif unaryOp == Symbol.TILDE.value:
            self._vmWriter.writeArithmetic(VMOp.NOT)

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
        return tt, t

    def _grammarType(self):
        if self._isType():
            tt, t = self._advance()
            return tt, t
        else:
            raise Exception("Unexpected token: {0}".format(t))

    def _grammarSubroutineReturnType(self):
        if self._isToken(TokenType.KEYWORD, Keyword.VOID) or self._isType():
            tt, t = self._advance()
            return tt, t
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
