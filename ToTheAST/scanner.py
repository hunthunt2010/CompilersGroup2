#!/usr/bin/env python

import fileinput
import sys

import ply.lex as lex
import ply.yacc as yacc

from node import Node
from io import StringIO

from visitor import *

# Collects errors into a string
errors = StringIO()

reserved = {'int' : 'int',
        'const' : 'const',
        'if' : 'if',
        'else' : 'else',
        'return' : 'return',
        'while' : 'while',
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
        'lessthan',
        'doubleequal',
        'greaterthan',
        'divide',
        'modulus',
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
t_doubleequal = r'=='
t_lessthan = r'<'
t_greaterthan = r'>'
t_plus = r'\+'
t_minus = r'-'
t_multiply = r'\*'
t_divide = r'/'
t_modulus = r'%'
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
    r'-?[0-9][0-9]*'
    t.value = int(t.value)
    return t

def t_ignore_comment(t):
    r'//.*\n'
    t.lexer.lineno += 1
    pass

def t_error(t):
    print("Illegal character (%d): %s\n" % (t.lineno, t), file=errors)

def p_START(p):
    '''START : STMTS'''
    p[0] = Node("START", "START")
    p[0].addChild(p[1])

def p_STMTS(p):
    'STMTS : STMT STMTS'
    p[0] = Node("STMTS",  "STMTS")
    p[0].addChild(p[1])
    p[0].adoptChildren(p[2])

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

def p_BLOCK(p):
    'STMT : CODEBLOCK'
    p[0] = Node("BLOCK", "BLOCK")
    p[0].addChild(p[1])

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

def p_WHILE_STMT(p):
    'STMT : while lp EXPR rp CODEBLOCK'
    p[0] = Node("WHILE", "WHILE")
    p[0].addChild(p[3])
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
                      | modulus
                      | lessthan
                      | greaterthan
                      | doubleequal
                      | lessequal'''
    p[0] = Node("BINARYOPERATOR", p[1])

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
    errors.write("Unknown Token(%d): %s\n" % (p.lineno, p.value))

lex.lex(debug=0)
parser = yacc.yacc(debug=0)

# use only file names that don't start with '-', since those are commandline arguments, and not files
files = []
for arg in sys.argv[1:]:
    if arg[0] != '-':
        files.append(arg)

s = ""
for line in fileinput.input(files):
    s += line

root = None
try:
    root = parser.parse(s)
except lex.LexError:
    print("Lex error")

# DEPRICATED. Use the SymbolVisitor instead
# if '-symtable' in sys.argv:
    # Show the symbol table
    # symTable = root.processSymbolTable()
    # print(symTable)
    # Node.symToNamespace(symTable)

if '-visit' in sys.argv:
    PrintVisitor().visit(root)

elif '-symvisit' in sys.argv:
    symtable = SymbolVisitor().visit(root)
    if symtable.errors:
        print("Symbol table had errors")
        sys.exit(-1)
    else:
        print(symtable)

elif '-arithmetic' in sys.argv:
    ArithmeticTransformer().visit(root)
    PrintVisitor().visit(root)

elif '-ir' in sys.argv:
	IntermediateRepresentation().visit(root)

else:
    # DEPRICATED Old way of disylaying the output for ToTheAST. Instead, use the SymbolVisitor
    # print(root.getNames())
    # print(root.getChildren())

    # Output requirements for ToTheIR:
    # OUTPUT.p:     raw parse tree like in ToTheAST
    ptfile = open("OUTPUT.p", "w")
    PrintVisitor(file=ptfile).visit(root)
    ptfile.close()

    # OUTPUT.a:     abstract syntax tree that uses arithmetic syntax trees instead
    astfile = open("OUTPUT.a", "w")
    # NOTE: The arithmetic transformer modifies the AST IN-PLACE
    ArithmeticTransformer().visit(root)
    PrintVisitor(file=astfile).visit(root)
    astfile.close()


    # OUTPUT.ir:    listing of the courses' IR instructions?
    # Generate the symbol table
    irfile = open("OUTPUT.ir", "w")
    symboltable = SymbolVisitor(file=errors).visit(root)

    symfile = open("OUTPUT.sym", "w")
    symboltable.prettyprint(file=symfile)
    symfile.close()

    # Generate a memory map. Goes from SymEntry -> memorylocation
    mmapfile = open("OUTPUT.mmap", "w")
    mmap = symboltable.createMemoryMap()
    for sym in mmap:
        print("%s (%i): %i" % (symboltable.namespace.getName(sym.name), sym.scope, mmap[sym]), file=mmapfile)
    mmapfile.close()
    IntermediateRepresentation(symboltable, mmap, file=irfile).visit(root)
    irfile.close()

    # OUTPUT.err:   list of errors during compilation
    errfile = open("OUTPUT.err", "w")
    print(errors.getvalue(), file=errfile)
    errfile.close()

    # If there are errors, there should be one per line. Counting the number of lines should cound the number of errors
    exit(len(errors.getvalue().split('\n')) - 1)
