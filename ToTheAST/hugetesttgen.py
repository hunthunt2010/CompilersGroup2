#!/usr/bin/env python3

import sys

if len(sys.argv) < 2:
    print("Usage %s <NumberofRegisters>" % sys.argv[0])
    exit(-1)

def expressiongen(num):
    if num == 1:
        return "(1+1)"
    else:
        return "(" + expressiongen(num-1) + "+" + expressiongen(num-1) + ")"

print("int z = " + expressiongen(int(sys.argv[1])) + ";")
