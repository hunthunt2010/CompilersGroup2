
from collections import namedtuple
SymEntry = namedtuple('SymEntry', ['name', 'symtype', 'scope', 'depth'])

# Exists as a built-in for Python2, but was put in sys for python 3
from sys import intern, stderr

import namespace 

class SymbolTable:
    def __init__(self):
        # Contains scope-depth. this is different from scope level, because
        # the scopes are uniquely defined, while depths are often the same
        self._depth = 0

        # the SymbolTable is a hash of type: {SymbolName :String -> {ScopeLevel :int -> (Name, Type, Var, Depth) }}
        self._symbolHash = {}

        # Current depth is stored as _scopelevelstack[-1]
        self._scopelevelstack=[0]
        self._allscopes=[0]
        self.errors = False

        # Namespace instance for symbol table
        self.namespace = Namespace()

    def getCurrentScope(self):
        return self._scopelevelstack[0]

    def __str__(self):
        return str(self._symbolHash)

    def openScope(self):
        self._depth += 1

        nextScope = max(self._allscopes)+1
        # print("New scope: %i" % nextScope)
        self._scopelevelstack.insert(0, nextScope)
        self._allscopes.append(nextScope)

    def closeScope(self):
        self._depth -= 1

        self._scopelevelstack.pop(0)

    def retrieveScope(self, symbol, level=-1):
        '''Returns the symbol-table entry for the symbol at the specified level.
           If no level is specified, then the inner-most level is used'''
        if symbol not in self._symbolHash:
            return None

        if level >= 0:
            if level not in self._symbolHash[symbol]:
                return None
            else:
                return self._symbolHash[symbol][level]
        else:
            # level == -1. Return the inner-most entry
            for scope in self._scopelevelstack:
                # print("Checking for %s in scope %i" % (symbol, scope))
                if scope in self._symbolHash[symbol]:
                    # print("Returning", self._symbolHash[symbol][scope])
                    return self._symbolHash[symbol][scope]
            # print("Could not find %s" % symbol)
            return None

    # TODO: Type??
    def enterSymbol(self, name, symtype):
        if name not in self._symbolHash:
            self._symbolHash[name] = {}

        if name in self._symbolHash:
            if self._scopelevelstack[0] in self._symbolHash[name]:
                # This variable was previously defined for the scope
                print("Variable %s was already defined in scope %i" % (name, self._scopelevelstack[0]) , file=stderr)
                self.errors = True

        # print("Making %s at scope=%i, depth=%i" % (name, self._scopelevelstack[-1], self._depth))
        # Use python's global intern to compress string-names into an intern (Same thing as our NameSpace)
        newSym = SymEntry(name=namespace.addName(name), symtype=symtype, scope=self._scopelevelstack[0], depth=self._depth)

        self._symbolHash[name][newSym.scope] = newSym
