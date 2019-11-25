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
        NE,
        LE,
        GE,
        LT,
        GT,
        MASK_EQ,
        EQ,
        ST_CONT,
        IF,
        THEN,
        ELSE,
        NUMBER,
        ID,
        STRING,
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
    NE = r'!=|<>'
    LE = r'<='
    GE = r'>='
    LT = r'<'
    GT = r'>'
    MASK_EQ = r'=='
    EQ = r'='
    ST_CONT = r'&'
    IF = r'(?i)\bif\b'
    THEN = r'(?i)\bthen\b'
    ELSE = r'(?i)\belse\b'
    NUMBER = r'\b[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'
    ID = r'[a-zA-Z][a-zA-Z0-9_]*'
    STRING = r'"[^"]*"'


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
    def program(self, p):
        pass

    @_('statement_group')
    def program(self, p):
        return [p.statement_group]

    @_('program statement_group')
    def program(self, p):
        prog = list(p.program)
        prog.append(p.statement_group)
        return prog

    @_('statement')
    def statement_group(self, p):
        return [p.statement]

    @_('statement_group ST_CONT statement')
    def statement_group(self, p):
        stg = list(p.statement_group)
        stg.append(p.statement)
        return stg

    @_('assignment_statement')
    @_('conditional_statement')
    def statement(self, p):
        return p[0]

    @_('ID EQ boolean_expression')
    @_('ID EQ number_expression')
    @_('ID EQ string_term')
    def assignment_statement(self, p):
        return ('assign', p.ID, p[2])

    @_('IF boolean_expression THEN statement_group')
    def conditional_statement(self, p):
        return ('if', p.boolean_expression, p.statement_group, None)

    @_('IF boolean_expression THEN statement_group ELSE statement_group')
    def conditional_statement(self, p):
        return ('if', p.boolean_expression, p.statement_group0, p.statement_group1)

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

    @_('number_compare_expression')
    def boolean_term(self, p):
        return p.number_compare_expression

    @_('boolean_compare_expression')
    def boolean_term(self, p):
        return p.boolean_compare_expression

    @_('string_compare_expression')
    def boolean_term(self, p):
        return p.string_compare_expression

    @_('ID')
    def boolean_term(self, p):
        return ('boolean-variable', p.ID)

    @_('TRUE')
    @_('FALSE')
    def boolean_constant(self, p):
        return ('constant', p[0])

    @_('boolean_term boolean_compare_operator boolean_term')
    def boolean_compare_expression(self, p):
        return (p.boolean_compare_operator, [p.boolean_term0, p.boolean_term1])

    @_('NE')
    @_('EQ')
    def boolean_compare_operator(self, p):
        return p[0]

    @_('number_expression number_compare_operator number_expression')
    def number_compare_expression(self, p):
        return (p.number_compare_operator, [p.number_expression0, p.number_expression1])

    @_('NE')
    @_('LE')
    @_('GE')
    @_('LT')
    @_('GT')
    @_('EQ')
    def number_compare_operator(self, p):
        return p[0]

    @_('number_add_expression')
    def number_expression(self, p):
        return p.number_add_expression

    @_('number_multiply_expression')
    def number_add_expression(self, p):
        return [p.number_multiply_expression]

    @_('number_add_expression number_add_operator number_multiply_expression')
    def number_add_expression(self, p):
        return (p.number_add_operator, [p.number_add_expression, p.number_multiply_expression])

    @_('number_term')
    def number_multiply_expression(self, p):
        return [p.number_term]

    @_('number_multiply_expression number_multiply_operator number_term')
    def number_multiply_expression(self, p):
        return (p.number_multiply_operator, [p.number_multiply_expression, p.number_term])

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
    def number_add_operator(self, p):
        return p[0]

    @_('TIMES')
    @_('INTDIVIDE')
    @_('DIVIDE')
    @_('MOD')
    def number_multiply_operator(self, p):
        return p[0]

    @_('string_term string_compare_operator string_term')
    def string_compare_expression(self, p):
        return (p.string_compare_operator, [p.string_term0, p.string_term1])

    @_('NE')
    @_('EQ')
    @_('MASK_EQ')
    def string_compare_operator(self, p):
        return p[0]

    @_('STRING')
    def string_term(self, p):
        return p.STRING

    @_('ID')
    def string_term(self, p):
        return ('string-variable', p.ID)

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
A = 1 & b = 2
if a == b 
  then a = b & a = d 
  else a = e 
    & if a = b 
      then a = c & e = 23 
      else sa = 42
"""

def tokens():
    for t in Lex().tokenize(TEXT):
        print(t)
        yield t

res = Pax().parse(tokens())
print()
pprint(res, indent=4, width=1)
