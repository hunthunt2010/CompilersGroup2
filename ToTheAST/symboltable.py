
from collections import namedtuple
SymEntry = namedtuple('SymEntry', ['name', 'symtype', 'scope', 'depth'])

# Exists as a built-in for Python2, but was put in sys for python 3
from sys import intern, stderr, stdout

from namespace import Namespace

class SymbolTable:
    def __init__(self, file=stderr):
        # Contains scope-depth. this is different from scope level, because
        # the scopes are uniquely defined, while depths are often the same
        self._depth = 0

        # the SymbolTable is a hash of type: {SymbolName :String -> {ScopeLevel :int -> (Name, Type, Var, Depth) }}
        self._symbolHash = {}

        # Current depth is stored as _scopelevelstack[-1]
        self._scopelevelstack=[0]
        self._allscopes=[0]

        self.errors = False
        self.output = file

        # Namespace instance for symbol table
        self.namespace = Namespace()

    def prettyprint(self, file=stdout):
        for name in self._symbolHash:
            print("%s:" % name, end='', file=file)
            for scope in self._symbolHash[name]:
                print("\t\t%i: %s" % (scope, str(self._symbolHash[name][scope])), file=file)

    def getCurrentScopeStack(self):
        return self._scopelevelstack

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

    def retrieveScope(self, symbol, level=-1, stack=None):
        '''Returns the symbol-table entry for the symbol at the specified level.
           If no level is specified, then the inner-most level is used'''
        if stack is None:
            stack = self._scopelevelstack

        if symbol not in self._symbolHash:
            return None

        if level >= 0:
            if level not in self._symbolHash[symbol]:
                return None
            else:
                return self._symbolHash[symbol][level]
        else:
            # level == -1. Return the inner-most entry
            for scope in stack:
                # print("Checking for %s in scope %i" % (symbol, scope))
                if scope in self._symbolHash[symbol]:
                    # print("Returning", self._symbolHash[symbol][scope])
                    return self._symbolHash[symbol][scope]
            # print("Could not find %s" % symbol)
            return None

    # TODO: Type??
    def enterSymbol(self, name, symtype):
        if symtype is None:
            print("Trying to enter %s with a NONE symtype" % name, file=stderr)

        if name not in self._symbolHash:
            self._symbolHash[name] = {}

        if name in self._symbolHash:
            if self._scopelevelstack[0] in self._symbolHash[name]:
                # This variable was previously defined for the scope
                print("Variable %s was already defined in scope %i" % (name, self._scopelevelstack[0]) , file=self.output)
                self.errors = True

        # print("Making %s at scope=%i, depth=%i" % (name, self._scopelevelstack[-1], self._depth))
        # Use python's global intern to compress string-names into an intern (Same thing as our NameSpace)
        newSym = SymEntry(name=self.namespace.addName(name), symtype=symtype, scope=self._scopelevelstack[0], depth=self._depth)

        self._symbolHash[name][newSym.scope] = newSym

    def createMemoryMap(self):
        # Makes a default memory map that has globals allocated
        return MemoryMap(self)

class MemoryMap:
    def __init__(self, symbolTable):
        self.symtable = symbolTable

        # SymEntry -> memlocation
        self._mmap = {}

        # Starting location of memory after instructions and data
        self.memptr = 20000

        # Allocate globals
        for var in self.symtable._symbolHash:
            #for scope in self._symbolHash[var]:
            if 0 in self.symtable._symbolHash[var]:
                self._mmap[self.symtable._symbolHash[var][0]] = self.memptr
                self.incrementMemptr()

    def incrementMemptr(self, n=1):
        # Hardcoded memory location size: 8 bytes
        self.memptr += (8*n)

	def decrementMemptr(self, n=1):
		self.memptr -= (8*n)

	def allocateScope(self, listSymEnt):
		"Allocates local variables for a scope"
		for var in listSymEnt:
			self._mmap[var] = self.memptr
			self.incrementMemptr()

	def lookUpVar(self, nameVar, scopeVar):
		'''Given the name and scope of a variable, return the mem location that it resides in or none if mem location is not allocated '''	
			symEntry = self.symtable._symbolHash[nameVar][scopeVar]

			if symEntry in  self._mmap:
				return self._mmap[symEntry]			
			else
				return None

	def deallocateScope(self, scopeVar):
		"Frees scope from local variables"
		for mappedVar in self._mmap:
			if mappedVar.scope == scopeVar:
				del self._mmap[mappedVar] 
				self.decrementMemptr()
