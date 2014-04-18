#!/usr/bin/env python

# const int a = 1;
# int x = 1<<a;
# int y, z = 3;
# 
# y = z - x;
# if ( y <= 0 ) {
#    z = (x+2) + z*z ;
# } else {
#    z = z / y;
# }
# 
# return z;

import fileinput
import sys

import ply.lex as lex
import ply.yacc as yacc

from node import Node

reserved = {'int' : 'int',
        'const' : 'const',
        'if' : 'if',
        'else' : 'else',
        'return' : 'return',
        }

tokens = [
        'assign',
        'semi', 
        'comma',
        'lp', 'rp',
        'lb', 'rb',
        'leftshift',
        'plus',
        'minus',
        'multiply',
        'lessequal',
        'divide',
        'int_value',
        'identifier',
    ] + list(reserved.values())

t_assign = r'='
t_comma = r','
t_lp = r'\('
t_rp = r'\)'
t_lb = r'{'
t_rb = r'}'
t_leftshift = r'<<'
t_lessequal = r'<='
t_plus = r'\+'
t_minus = r'-'
t_multiply = r'\*'
t_divide = r'/'
t_semi = r';'
t_ignore = " \t"

def t_identifier(t):
    r'[a-zA-Z_]+[a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[ t.value ]
    return t

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1
    pass

def t_int_value(t):
    r'[0-9][0-9]*'
    t.value = int(t.value)
    return t

def t_ignore_comment(t):
    r'//.*\n'
    t.lexer.lineno += 1
    pass

def t_error(t):
    sys.stderr.write("Illegal character (%d): %s\n" % (t.lineno, t))
    sys.exit(1)

def p_START(p):
    '''START : STMTS'''
    p[0] = Node("START", "START")
    p[0].addChild(p[1])

def p_STMTS(p):
    'STMTS : STMT STMTS'
    p[0] = Node("STMTS",  "STMTS")
    p[0].addChild(p[1])
    p[0].adoptChildren(p[2])
    # print(p[0].showSelf())

def p_EMPTY_STMTS(p):
    'STMTS :'

def p_STMT_DECL(p):
    '''STMT : DECL semi'''
    p[0] = p[1]

def p_STMT_EXPR(p):
    'STMT : EXPR semi'
    p[0] = p[1]

def p_STMT_RETURN(p):
    'STMT : RETURN semi'
    p[0] = p[1]

def p_STMT_ASSIGN(p):
    'STMT : identifier assign EXPR semi'
    p[0] = Node("ASSIGN", "ASSIGN")
    p[0].addChild(Node("IDENTIFIER", p[1]))
    p[0].addChild(p[3])

def p_IF_STMT(p):
    'STMT : if lp EXPR rp CODEBLOCK'
    p[0] = Node("IF", "IF")
    p[0].addChild(p[3])
    p[0].addChild(p[5])


def p_IF_ELSE_STMT(p):
    'STMT : if lp EXPR rp CODEBLOCK else CODEBLOCK'
    p[0] = Node("IF_ELSE" ,"IF_ELSE")
    p[0].addChild(p[3])
    p[0].addChild(p[5])
    p[0].addChild(p[7])


def p_DECL(p):
    '''DECL : TYPE VARIABLE MULTI'''
    p[0] = Node("DECL", "DECL")
    p[0].addChild(p[1])
    p[0].addChild(p[2])
    p[0].addChild(p[3])

def p_DECL_ASSIGN(p):
    '''DECL : TYPE VARIABLE assign EXPR MULTI'''
    p[0] = Node("DECL", "DECL")
    p[0].addChild(p[1])
    p[0].addChild(p[2])
    p[0].addChild(p[4])
    p[0].addChild(p[5])

def p_MULTI(p):
    '''MULTI : comma VARIABLE MULTI'''
    p[0] = Node("MULTI" , "MULTI" )
    p[0].addChild(p[2])
    p[0].addChild(p[3])

def p_MULTI_ASSIGN(p):
    '''MULTI : comma VARIABLE assign EXPR MULTI'''
    p[0] = Node("MULTI_ASSIGN" , "MULTI_ASSIGN" )
    p[0].addChild(p[2])
    p[0].addChild(p[4])
    p[0].addChild(p[5])

def p_MULTI_LAMBDA(p):
    '''MULTI : '''

def p_VARIABLE(p):
    '''VARIABLE : identifier'''
    p[0] = Node("VARIABLE", p[1])

def p_EXPR_ORDER(p):
    'EXPR : lp EXPR rp'
    p[0] = Node("EXPR", "EXPR")
    p[0].addChild(p[2])

def p_EXPR_BINOP(p):
    'EXPR : EXPR BINARYOPERATOR EXPR'
    p[0] = Node("EXPR_BINOP", "EXPR_BINOP")
    p[0].addChild(p[1])
    p[0].addChild(p[2])
    p[0].addChild(p[3])

def p_EXPR_VALUE(p):
    'EXPR : VALUE'
    p[0] = Node("EXPR", "VALUE")
    p[0].addChild(p[1])

def p_BINARYOPERATOR(p):
    '''BINARYOPERATOR : leftshift
                      | plus
                      | minus
                      | multiply
                      | divide
                      | lessequal'''
    p[0] = Node("BINARYOPEAROR", p[1])

def p_RETURN(p):
    'RETURN : return'
    p[0] = Node("RETURN", "RETURN")

def p_RETURN_EXPR(p):
    'RETURN : return EXPR'
    p[0] = Node("RETURN", "RETURN")
    p[0].addChild(p[2])

def p_CODEBLOCK(p):
    'CODEBLOCK : lb STMTS rb'
    p[0] = Node("CODEBLOCK", "CODEBLOCK")
    p[0].addChild(p[2])

def p_VALUE(p):
    '''VALUE : int_value
             | identifier'''
    p[0] = Node("VALUE", p[1])

def p_TYPE(p):
    '''TYPE : MODIFIER TYPE'''
    p[0] = Node('TYPE',"TYPE")
    p[0].addChild(p[1])
    p[0].addChild(p[2])

def p_TYPE_INT(p):
    '''TYPE : int'''
    p[0] = Node('TYPE', p[1])
                          
def p_MODIFIER(p):
    'MODIFIER : const'
    p[0] = Node("MODIFIER","const")

def p_error(p):
    sys.stderr.write("Unknown Token(%d): %s\n" % (str(p.lineno), p.value))
    sys.exit(2)

lex.lex()
parser = yacc.yacc()


s = ""
for line in fileinput.input():
    s += line

root = parser.parse(s)

print(root.getNames())
print(root.getChildren())

# Show the symbol table
print(root.processSymbolTable())
