from sly import Lexer, Parser
from dataclasses import dataclass, field
from typing import List
from pprint import pprint
from pathlib import Path

import re


class Lex(Lexer):
    tokens = {
        LB,
        RB,
        LINK_LB,
        LINK_RB,
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
        PRINT,
        PRINTLN,
        BUTTON,
        GOTO,
        END,
        INPUT,
        ANYKEY,
        PROC,
        FORGET_PROC,
        INV,
        INVKILL,
        QUIT,
        SAVE,
        CLS,
        RANDOM,
        RANDOM_INT,
        TIME,
        PAUSE,
        PLAY,
        MUSIC,
        IMAGE,
        LINK_SEP,
        NUMBER,
        ID,
        # LOCATION,
        LABEL,
        STRING,
    }

    ignore = ' \t'
    # ignore_newline = r'\n+'
    #ignore_comment = r'(?s)/\*.*?\*/'
    # ignore_old_comment = r'\;.*?\n'

    # Define a rule so we can track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    @_(r'(?s)/\*.*?\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\;.*?\n')
    def ignore_old_comment(self, t):
        self.lineno += 1

    @_(r'//.*?\n')
    def ignore_c_comment(self, t):
        self.lineno += 1

    @_(r'--.*?\n')
    def ignore_minmin_comment(self, t):
        self.lineno += 1

    @_(r'(?i)instr .*?\n')
    def ignore_instr(self, t):
        self.lineno += 1

    literals = {
        ',',
    }

    LB = r'\('
    RB = r'\)'
    LINK_LB = r'\[\['
    LINK_RB = r'\]\]'
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
    PRINT = r'(?i)(\bprint\b|\bp\b)([^&\n]*?\[\[.*?\]\][^&\n]*?)*[^&\n]*'
    PRINTLN = r'(?i)(\bprintln\b|\bpln\b)([^&\n]*?\[\[.*?\]\][^&\n]*?)*[^&\n]*'
    BUTTON = r'(?i)\bbtn\b[^&\n]+'
    GOTO = r'(?i)\bgoto\b' + r'[^&\n]+'
    END = r'(?i)\bend\b'
    INPUT = r'(?i)\binput\b'
    ANYKEY = r'(?i)\banykey\b'
    PROC = r'(?i)\bproc\b' + r'[^&\n]+'
    FORGET_PROC = r'(?i)\bforget_procs?\b'
    INV = r'(?i)\binv[+-]'
    INVKILL = r'(?i)\binvkill\b'
    QUIT = r'(?i)\bquit\b'
    SAVE = r'(?i)\bsave\b [\w#%$]*'
    CLS = r'(?i)\bcls\b'
    RANDOM = r'(?i)\brnd\b'
    RANDOM_INT = r'(?i)\brnd\d+\b'
    TIME = r'(?i)\btime\b'
    PAUSE = r'(?i)\bpause\b'
    PLAY = r'(?i)\bplay\b'
    MUSIC = r'(?i)\bmusic\b'
    IMAGE = r'(?i)\bimage\b'
    LINK_SEP = r'\|'
    NUMBER = r'\b[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?\b'
    ID = r'(\b[\w.]+\b)|(#[\w.]+?\$)'
    #LOCATION = r'\b[a-zA-Z][a-zA-Z0-9_-]+\b'
    LABEL = r':[^&\n,]+'
    STRING = r'"[^"]*"'


class Pax(Parser):
    debugfile = 'parser.out'

    tokens = Lex.tokens

    precedence = (
        ('left', IF),
        ('nonassoc', EQ),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, INTDIVIDE, MOD),
        ('left', OR, XOR),
        ('left', AND),
    )

    static_self = None

    @staticmethod
    def get_static_self():
        if not Pax.static_self:
            Pax.static_self = Pax()
        return Pax.static_self

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
    @_('label_statement')
    @_('print_statement')
    @_('goto_statement')
    @_('button_statement')
    @_('end_statement')
    @_('input_statement')
    @_('any_key_statement')
    @_('procedure_statement')
    @_('forget_procedure_statement')
    @_('inventory_statement')
    @_('clear_inventory_statement')
    @_('quit_statement')
    @_('save_statement')
    @_('clear_screen_statement')
    @_('pause_statement')
    @_('multimedia_statement')
    def statement(self, p):
        return p[0]

    @_('LABEL')
    def label_statement(self, p):
        label = p.LABEL[1:].strip(' ')
        return ('label', label)

    @_('PRINT')
    @_('PRINTLN')
    def print_statement(self, p):
        return ('print', self._parse_text_block(p[0][3:]))

    @_('GOTO')
    def goto_statement(self, p):
        location_name = p.GOTO[5:]
        return ('goto', location_name)

    @_('END')
    def end_statement(self, p):
        return ('end', )

    @_('INPUT ID')
    def input_statement(self, p):
        return ('input', p.ID)

    @_('ANYKEY')
    def any_key_statement(self, p):
        return ('anykey', None)

    @_('ANYKEY ID')
    def any_key_statement(self, p):
        return ('anykey', p.ID)

    @_('PROC')
    def procedure_statement(self, p):
        location_name = p.PROC[5:]
        return ('call', location_name)

    @_('FORGET_PROC')
    def forget_procedure_statement(self, p):
        return ('drop-call-stack', )

    @_('INV ID')
    def inventory_statement(self, p):
        return ('inventory', p.INV[3], 1, p.ID)

    @_('INV number_expression "," ID')
    def inventory_statement(self, p):
        return ('inventory', p.INV[3], p.number_expression, p.ID)

    @_('INVKILL ID')
    def clear_inventory_statement(self, p):
        return ('inventory', '=', 0, p.ID)

    @_('INVKILL')
    def clear_inventory_statement(self, p):
        return ('inventory', '=', 0, None)

    @_('BUTTON')
    def button_statement(self, p):
        return self._parse_button(p.BUTTON[3:])

    @_('QUIT')
    def quit_statement(self, p):
        return ('quit', )

    @_('SAVE')
    def save_statement(self, p):
        return ('save', )

    @_('CLS')
    def clear_screen_statement(self, p):
        return ('clear-screen',)

    @_('PAUSE number_expression')
    def pause_statement(self, p):
        return ('pause', p.number_expression)

    @_('PLAY string_term')
    @_('MUSIC string_term')
    @_('IMAGE string_term')
    def multimedia_statement(self, p):
        return (p[0], p.string_term)

    @_('ID EQ expression')
    def assignment_statement(self, p):
        return ('assign', p.ID, p[2])

    @_('boolean_expression')
    @_('number_expression')
    @_('string_term')
    def expression(self, p):
        return p[0]

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

    @_('compare_expression')
    def boolean_term(self, p):
        return p.compare_expression

    @_('ID')
    def boolean_term(self, p):
        return ('boolean-variable', p.ID)

    @_('TRUE')
    @_('FALSE')
    def boolean_constant(self, p):
        return ('constant', p[0])

    @_('expression compare_operator expression')
    def compare_expression(self, p):
        return (p.compare_operator, [p.expression0, p.expression1])

    @_('NE')
    @_('LE')
    @_('GE')
    @_('LT')
    @_('GT')
    @_('EQ')
    @_('MASK_EQ')
    def compare_operator(self, p):
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

    @_('number_function')
    def number_term(self, p):
        return p.number_function

    @_('RANDOM')
    @_('RANDOM_INT')
    @_('TIME')
    def number_function(self, p):
        return ('function', p[0])

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
            line = p.lineno
            column = self._find_column(quest_file, p)
            print(f'Error at token {p.type}, {p.value} at line {line} col {column}')
            self.errok()
        else:
            print('Syntax error at EOF')

    def _find_column(self, text, token):
        last_cr = text.rfind('\n', 0, token.index)
        if last_cr < 0:
            last_cr = 0
        column = (token.index - last_cr) + 1
        return column

    def _parse_text_block(self, text_block):
        rex = r'(?P<link>\[\[.+?\]\])|(?P<substitution>#.*?\$)'
        res = re.search(rex, text_block)
        begin = 0
        end = len(text_block)

        res = []

        for match in re.finditer(rex, text_block):
            group = match.lastgroup
            span_begin, span_end = match.span(group)

            text = text_block[begin:span_begin]
            if text:
                res.append(('text', text))
            if group == 'link':
                res.append(self._parse_link(match.group(group)))
            elif group == 'substitution':
                res.append(self._parse_substitution(match.group(group)))

            begin = span_end

        text = text_block[begin:end]
        if text:
            res.append(('text', text))

        return res

    def _parse_substitution(self, substitution_text: str):
        substitution_text = substitution_text[1:-1]
        if substitution_text.startswith('%'):
            substitution_text = substitution_text[1:]
        if substitution_text.startswith('#'):
            code = substitution_text[1:]
            try:
                return ('text', chr(int(code)))
            except Exception:
                raise Exception(f'Cannot parse {code} as char code')
        elif substitution_text == '':
            return ('text', ' ')
        elif substitution_text == '/':
            return ('text', '\n')
        else:
            return ('variable', substitution_text)

    def _parse_link(self, link_text: str):
        link_text = link_text[2:-2]
        splits = link_text.split('|')
        if len(splits) == 1:
            link_text = link_text.strip(' ')
            return ('link', link_text, [('goto', link_text)])
        elif len(splits) == 2:
            link_text = splits[0].strip(' ')
            operators = splits[1].strip(' ')
            if re.match(r'^[a-zA-Z-0-9_]+$', operators):
                return ('link', link_text, [('goto', operators)])
            else:
                return ('link', link_text, self._parse_operators(operators))
        else:
            raise Exception('Incorrect character | somewhere')

    def _parse_operators(self, operators_text):
        res = Pax().parse(Lex().tokenize(operators_text))
        return res

    def _parse_button(self, button_text: str):
        split = button_text.split(',', 2)
        if len(split) == 1:
            location_name = split[0].strip(' ')
            return ('button', location_name, [('goto', location_name)])
        else:
            text = split[1].strip(' ')
            operators = split[0].strip(' ')
            if re.match(r'^[\w.]+$', operators):
                return ('button', text, [('goto', operators)])
            else:
                return ('button', text, self._parse_operators(operators))




# quest_file = "/home/su0/git/kirillsulim/sly-test/quests/Cursed City/cursed_city.qst"
# quest_file = "/home/su0/git/kirillsulim/sly-test/quests/Alice's Adventures in Urqland/quest.qst"
# quest_file = "/home/su0/git/kirillsulim/sly-test/quests/Grunk and cheese/quest.qst"
# quest_file = "/home/su0/git/kirillsulim/sly-test/quests/support/quest.qst"
# quest_file = "/home/su0/git/kirillsulim/sly-test/quests/zolushka/quest.qst"
quest_file = "/home/su0/git/kirillsulim/sly-test/quests/Адская суббота/quest.qst"

quest_source = Path(quest_file).read_text('utf-8')
# quest_source = 'Mhealp2=(Mhealp1*#Weaponhealb$)/100'

def tokens():
    for t in Lex().tokenize(quest_source):
        print(t)
        yield t

res = Pax().parse(tokens())
print()

for statement in res:
    pprint(statement, indent=4, width=1)
