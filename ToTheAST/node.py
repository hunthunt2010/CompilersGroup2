
class Node:
    count = 0

    def __init__(self, name, data):
        self.name = Node.count
        Node.count += 1
        self.data = data
        #index 0 in child list = left most child
        self.children = []

    def addChild(self, newChild):
        self.children.append(newChild)

    def adoptChildren(self, otherNode):
        if otherNode is not None:
            for child in otherNode.children:
                self.children.append(child)

    def isLeaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False

    def getName(self):
        return self.name

    def getData(self):
        return self.data

    def showSelf(self):
        temp = "%s %s :" % (self.name, self.data)
        for child in self.children:
            if child is not None:
                temp += " (%s,%s)" % (child.name, child.data)

        return temp

    def getNames(self):
        temp = "%s %s\n" % (self.name, self.data)
        for child in self.children:
            if child is not None:
                temp += child.getNames()

        return temp

    def getChildren(self):
        if len(self.children) == 0:
            return ""


        temp = str(self.name) + " "
        for child in self.children:
            if child is not None:
                temp += str(child.getName()) + " "

        temp += "\n"
        for child in self.children:
            if child is not None:
                temp += child.getChildren()

        return temp

    # Revision 1: NOT PERFECT
    # TODO: Put more thought into this data-structure
    # the SymbolTable is a hash of type: {SymbolName :String -> {ScopeLevel :int -> Node }}
    # Note: the stack is initialzied with level 0 (Global scope)
    def processSymbolTable(self, symbolTable={}, scopelevelstack=[0], allscopes=[0]):
        print("Processing node %s" % self.showSelf())
        # Depending on what type I am, we may process self and children differently
        if self.data == 'DECL':
            # DECL is the important one for processing variable instantion
            if self.children[1].data not in symbolTable: symbolTable[self.children[1].data] = {}

            symbolTable[self.children[1].data][scopelevelstack[-1]] = self.children[1]
            self.children[2].processSymbolTable(symbolTable, scopelevelstack, allscopes)

        elif self.data == 'MULTI_ASSIGN':
            if self.children[0].data not in symbolTable: symbolTable[self.children[0].data] = {}

            symbolTable[self.children[0].data][scopelevelstack[-1]] = self.children[0]
            for child in self.children:
                if child is not None:
                    child.processSymbolTable(symbolTable, scopelevelstack, allscopes)

        elif self.data == 'IF_ELSE':
            # Descend on the if-statements
            nextscope = max(allscopes)+1
            scopelevelstack.append(nextscope)
            allscopes.append(nextscope)
            self.children[1].processSymbolTable(symbolTable, scopelevelstack, allscopes)
            scopelevelstack.pop()

            # Descend on the else-statements
            nextscope = max(allscopes)+1
            scopelevelstack.append(nextscope)
            allscopes.append(nextscope)
            self.children[2].processSymbolTable(symbolTable, scopelevelstack, allscopes)
            scopelevelstack.pop()

        else:
            for child in self.children:
                if child is not None:
                    child.processSymbolTable(symbolTable, scopelevelstack, allscopes)
        return symbolTable
