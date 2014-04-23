from symboltable import SymbolTable

class Visitor:
    def visit(self, node):
        node.accept(self)

class PrintVisitor(Visitor):
    def __init__(self):
        self.idcount = 0

    def prettyChildren(self, node):
        return "%s" % (id(node))

    def visit(self, node):
        # print("%s\t%s" % (id(node), node.name if node.kind is not None else node.data))
        print("%s\t%s%s" % (id(node), node.name,
            ( "" if node.name is node.data else ("="+str(node.data)))
            ))

        if len(node.children) > 0:
            print(id(node), end=" ")
            for child in node.children:
                print(id(child), end=" ")
            print()

        self.idcount+=1
        # print(type(super()))

        super().visit(node)

class SymbolVisitor(Visitor):
    def __init__(self):
        self.table = SymbolTable()

    def visit(self, node):

        if node.data == 'DECL':
            # DECL is the important one for processing variable instantion
            self.table.enterSymbol(node.children[1].data, None)
            super().visit(node)

        elif node.data == 'MULTI_ASSIGN':
            self.table.enterSymbol(node.children[0].data, None)

            super().visit(node)

        elif node.data == 'IF_ELSE':
            self.table.openScope()
            node.children[1].accept(self)
            self.table.closeScope()

            # Descend on the else-statements
            self.table.openScope()
            node.children[2].accept(self)
            self.table.closeScope()

        elif node.data == 'IF':
            self.table.openScope()
            node.children[1].accept(self)
            self.table.closeScope()

        else:
            node.accept(self)

        return self.table
