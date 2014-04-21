
from sys import intern

from symboltable import SymbolTable

class Node:
    count = 0

    def __init__(self, name, data):
        # self.name = Node.count
        self.name = name
        Node.count += 1
        self.data = data
        #index 0 in child list = left most child
        self.children = []
        self.parent = None

    def addChild(self, newChild):
        if newChild is not None:
            self.children.append(newChild)
            newChild.parent = self

    def adoptChildren(self, otherNode):
        if otherNode is not None:
            for child in otherNode.children:
                self.children.append(child)
                child.parent = self

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

    # Revision 2; Very book-like
    def processSymbolTable(self, symbolTable=SymbolTable()):
        # Depending on what type I am, we may process self and children differently
        if self.data == 'DECL':
            # DECL is the important one for processing variable instantion
            symbolTable.enterSymbol(self.children[1].data, None)

            self.children[2].processSymbolTable(symbolTable)

        elif self.data == 'MULTI_ASSIGN':
            symbolTable.enterSymbol(self.children[0].data, None)

            for child in self.children:
                if child is not None:
                    child.processSymbolTable(symbolTable)

        elif self.data == 'IF_ELSE':
            symbolTable.openScope()
            self.children[1].processSymbolTable(symbolTable)
            symbolTable.closeScope()

            # Descend on the else-statements
            symbolTable.openScope()
            self.children[2].processSymbolTable(symbolTable)
            symbolTable.closeScope()

        elif self.data == 'IF':
            symbolTable.openScope()
            self.children[1].processSymbolTable(symbolTable)
            symbolTable.closeScope()
        else:
            for child in self.children:
                if child is not None:
                    child.processSymbolTable(symbolTable)
        return symbolTable

    def accept(self, visitor):
        # I've already been visited.. so, let's
        # visit all my children if I have any
        for child in self.children:
            visitor.visit(child)
