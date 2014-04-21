
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

