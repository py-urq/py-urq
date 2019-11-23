from sly import Lexer, Parser
from dataclasses import dataclass, field
from typing import List
from pprint import pprint

import re


class Lex(Lexer):
    tokens = {
        LB,
        RB,
        PLUS,
        MINUS,
        TIMES,
        INTDIVIDE,
        DIVIDE,
        MOD,
        AND,
        OR,
        XOR,
        NOT,
        TRUE,
        FALSE,
        NUMBER,
        ID,
    }

    ignore = ' \t'
    ignore_newline = r'\n+'

    LB = r'\('
    RB = r'\)'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    INTDIVIDE = r'\/\/'
    DIVIDE = r'\/'
    MOD = r'%'
    AND = r'(?i)\&\&|\band\b'
    OR = r'(?i)\|\||\bor\b'
    XOR = r'(?i)\^\^|\bxor\b'
    NOT = r'(?i)\bnot\b'
    TRUE = r'(?i)\btrue\b'
    FALSE = r'(?i)\bfalse\b'
    NUMBER = r'\b[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'
    ID = r'[a-zA-Z][a-zA-Z0-9_]*'


class Pax(Parser):
    debugfile = 'parser.out'

    tokens = Lex.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, INTDIVIDE, MOD),
        ('left', OR, XOR),
        ('left', AND),
    )

    @_('empty')
    def expression(self, p):
        return []

    @_('boolean_expression')
    @_('number_expression')
    def expression(self, p):
        return p[0]

    @_('boolean_or_expression')
    def boolean_expression(self, p):
        return p.boolean_or_expression

    @_('boolean_or_expression OR boolean_and_expression')
    @_('boolean_or_expression XOR boolean_and_expression')
    def boolean_or_expression(self, p):
        return (p[1], [p.boolean_or_expression, p.boolean_and_expression])

    @_('boolean_and_expression')
    def boolean_or_expression(self, p):
        return p.boolean_and_expression

    @_('boolean_and_expression AND boolean_term')
    def boolean_and_expression(self, p):
        return ('and', [p.boolean_and_expression, p.boolean_term])

    @_('boolean_term')
    def boolean_and_expression(self, p):
        return p.boolean_term

    @_('boolean_term')
    def boolean_expression(self, p):
        return [p.boolean_term]

    @_('LB boolean_expression RB')
    def boolean_term(self, p):
        return p.boolean_expression

    @_('NOT boolean_term')
    def boolean_term(self, p):
        return ('not', [p.boolean_term])

    @_('boolean_constant')
    def boolean_term(self, p):
        return p.boolean_constant

    @_('ID')
    def boolean_term(self, p):
        return ('boolean-variable', p.ID)

    @_('TRUE')
    @_('FALSE')
    def boolean_constant(self, p):
        return ('constant', p[0])

    @_('number_expression number_operator number_expression')
    def number_expression(self, p):
        return (p.number_operator, [p.number_expression0, p.number_expression1])

    @_('number_term')
    def number_expression(self, p):
        return [p.number_term]

    @_('LB number_expression RB')
    def number_term(self, p):
        return p.number_expression

    @_('number_constant')
    def number_term(self, p):
        return p.number_constant

    @_('ID')
    def number_term(self, p):
        return ('number-variable', p.ID)

    @_('PLUS number_term')
    @_('MINUS number_term')
    def number_term(self, p):
        return (p[0], p.number_term)

    @_('NUMBER')
    def number_constant(self, p):
        return p.NUMBER

    @_('PLUS')
    @_('MINUS')
    @_('TIMES')
    @_('INTDIVIDE')
    @_('DIVIDE')
    @_('MOD')
    def number_operator(self, p):
        return p[0]

    @_('')
    def empty(self, p):
        pass

    def error(self, p):
        if p:
            print(f'Error at token {p.type}, {p.value} at line {p.lineno} col {p.index}')
            self.errok()
        else:
            print('Syntax error at EOF')


TEXT = """
a && b || c and TrUe AND False Xor True
"""

def tokens():
    for t in Lex().tokenize(TEXT):
        print(t)
        yield t

res = Pax().parse(tokens())
print()
pprint(res, indent=4, width=1)
