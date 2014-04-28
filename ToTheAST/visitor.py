from symboltable import SymbolTable
from sys import stderr,stdout

class Visitor:
    def visit(self, node):
        node.accept(self)

class PrintVisitor(Visitor):
    def __init__(self, file=stdout):
        self.idcount = 0
        self.output = file

    def prettyChildren(self, node):
        return "%s" % (id(node))

    def visit(self, node):
        # print("%s\t%s" % (id(node), node.name if node.kind is not None else node.data), file=self.output)
        print("%s\t%s%s" % (id(node), node.name,
            ( "" if node.name is node.data else ("="+str(node.data)))
            ), file=self.output)

        if len(node.children) > 0:
            print(id(node), end=" ", file=self.output)
            for child in node.children:
                print(id(child), end=" ", file=self.output)
            print(file=self.output)

        self.idcount+=1
        # print(type(super()))

        super().visit(node)

class SymbolVisitor(Visitor):
    def __init__(self, file=stderr):
        self.table = SymbolTable(file=file)
        print("Outputting symbol errors to ", file)
        self.output = file

    def visit(self, node):
        node.scope = self.table.getCurrentScope()

        if node.name == 'DECL':
            # DECL is the important one for processing variable instantion
            self.table.enterSymbol(node.children[1].data, None)
            super().visit(node)

        elif node.name == 'MULTI_ASSIGN' or node.name == 'MULTI':
            self.table.enterSymbol(node.children[0].data, None)

            super().visit(node)

        elif node.name == 'CODEBLOCK':
            self.table.openScope()
            node.accept(self)
            self.table.closeScope()

        elif node.name == "VALUE" or node.name == "IDENTIFIER":
            # Check that the symbol is accessible in this scope
            if type(node.data) is str and self.table.retrieveScope(node.data) is None:
                print("The symbol %s is not accessible in scope %i" % (node.data, self.table.getCurrentScope()), file=self.output)
                self.table.errors = True

        else:
            node.accept(self)

        return self.table

class ArithmeticTransformer(Visitor):

    def visit(self, node):
        # print("Visiting node: %s" % node.showSelf())
        if node.name == 'EXPR_BINOP':
            node.name = node.children[1].name
            node.data = node.children[1].data

            node.children.pop(1)
            super().visit(node)

        elif node.name == 'EXPR':
            node.name = node.children[0].name
            node.data = node.children[0].data

            node.children = []
            super().visit(node)

        else:
            super().visit(node)

class IntermediateRepresentation(Visitor):
        def __init__(self, symboltable, mmap, file=stdout):
                self.table = SymbolTable()
                self.output = file
                self.mmap = mmap
                self.symboltable = symboltable

        def visit(self, node):
                if node.name == 'RETURN':
                        print("return", file=self.output)
                
                # elif node.name == 'VALUE':
                #       print("immld RX,",node.data)

                # elif node.name == 'IDENTIFIER':
                #       print("memld RX,",node.data)

                # elif node.name == 'VARIABLE':
                #       print("memld RX,",node.data)

                # elif node.name == 'BINARYOPERATOR':
                #       print("calc RX,", node, file=self.output)

                elif node.name == 'IF_ELSE':
                        if len(node.children) > 2:
                                if node.children[0].name == 'BINARYOPERATOR':
                                        print("calc RX,",node.children[0], file=self.output)

                elif node.name == 'IF':
                        if len(node.children) > 2:
                                if node.children[0].name == 'BINARYOPERATOR':
                                        print("calc RX,",node.children[0], file=self.output)

                elif node.name == 'WHILE':
                    if len(node.children) > 2:
                        if node.children[0].name == 'BINARYOPERATOR':
                            print("calc RX,",node.children[0], file=self.output)

                elif node.name == 'ASSIGN':
                        print("calc RX,",node.children[1], file=self.output)
                        i = node.children[0].data
                        j = self.symboltable.retrieveScope(i)
                        print("memst RX,",self.mmap[j], file=self.output)

                elif node.name == 'DECL':
                        if len(node.children) > 2:
                                if node.children[2].name != 'MULTI_ASSIGN':
                                        print("calc RX,",node.children[2], file=self.output)
                                        i = node.children[1].data
                                        j = self.symboltable.retrieveScope(i, node.children[1].scope)
                                        print("memst RX,",self.mmap[j], file=self.output)

                elif node.name == 'MULTI_ASSIGN':
                        print("calc RD,",node.children[1], file=self.output)
                        i = node.children[0].data
                        j = self.symboltable.retrieveScope(i)
                        print("memst RX,",self.mmap[j], file=self.output)

                if len(node.children) > 0:
                        node.accept(self)

                return self.table

