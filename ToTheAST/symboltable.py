
from collections import namedtuple
SymEntry = namedtuple('SymEntry', ['name', 'symtype', 'scope', 'depth'])

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

    def __str__(self):
        return str(self._symbolHash)

    def openScope(self):
        self._depth += 1

        nextScope = max(self._allscopes)+1
        # print("New scope: %i" % nextScope)
        self._scopelevelstack.append(nextScope)
        self._allscopes.append(nextScope)

    def closeScope(self):
        self._depth -= 1

        self._scopelevelstack.pop()

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
            return self._symbolHash[symbol][max(self._symbolHash[symbol])]

    # TODO: Type??
    def enterSymbol(self, name, symtype):
        if name not in self._symbolHash:
            self._symbolHash[name] = {}

        # print("Making %s at scope=%i, depth=%i" % (name, self._scopelevelstack[-1], self._depth))
        newSym = SymEntry(name=name, symtype=symtype, scope=self._scopelevelstack[-1], depth=self._depth)

        self._symbolHash[name][newSym.scope] = newSym
