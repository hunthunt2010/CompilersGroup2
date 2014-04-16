
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

    def isLeaf(self):
        if len(self.children) == 0:
            return True
        else:
            return False

    def getName(self):
        return self.name

    def getData(self):
        return self.data

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
