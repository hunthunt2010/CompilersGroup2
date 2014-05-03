from symboltable import SymbolTable
from sys import stderr,stdout
from register import *

class Visitor:
    def visit(self, node):
        return node.accept(self)

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
        self.output = file

    @staticmethod
    def toTypeList(node):
        types = []
        if node.name == 'TYPE':
            # could have a modifier AND a type
            if len(node.children) > 0:
                for child in node.children:
                    if child.data is not None:
                        types.append(child.data)
            else:
                types.append(node.data)
        return tuple(types)

    def visit(self, node):
        node.scopestack = tuple(self.table.getCurrentScopeStack())

        if node.name == 'DECL':
            # DECL is the important one for processing variable instantion
            typelist = self.toTypeList(node.children[0])
            self.table.enterSymbol(node.children[1].data, typelist)
            node.typelist = typelist
            super().visit(node)

        elif node.name == 'MULTI_ASSIGN' or node.name == 'MULTI':
            typelist = node.parent.typelist
            # typelist = self.toTypeList(node.children[0])
            self.table.enterSymbol(node.children[0].data, typelist)
            node.typelist = typelist
            super().visit(node)

        elif node.name == 'CODEBLOCK':
            self.table.openScope()
            node.accept(self)
            self.table.closeScope()

        elif node.name == 'ASSIGN':
            # Check for const correctness
            # is node.data writable?
            syme = self.table.retrieveScope(node.children[0].data)
            if syme is None:
                # This error will be caught when the recursion to VALUE is found
                pass
            else:
                if 'const' in syme.symtype:
                    # You cannot change that!!!
                    print("Symbol %s cannot be assigned in scope %i" % (node.children[0].data, self.table.getCurrentScope()), file=self.output)
                    self.table.errors = True
            node.accept(self)


        elif node.name == "VALUE" or node.name == "IDENTIFIER":
            # Check that the symbol is accessible in this scope, including const correctness
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
            super().visit(node)

            node.name = node.children[1].name
            node.data = node.children[1].data
            node.children.pop(1)

        elif node.name == 'EXPR':
            super().visit(node)

            node.name = node.children[0].name
            node.data = node.children[0].data
            node.children = node.children[0].children

        else:
            super().visit(node)

class IntermediateRepresentation(Visitor):
    def __init__(self, symboltable, mmap, file=stdout):
        self.output = file
        self.mmap = mmap
        self.symboltable = symboltable
        self.prgrmCounter = 0
        self.registerTracker = RegisterTracker()

    def visit(self, node):

        instructionList = []


        if node.name == 'RETURN':
                    #print("return", file=self.output)
            instructionList.append('jump +0')

            # elif node.name == 'VALUE':
            #       print("immld RX,",node.data)

            # elif node.name == 'IDENTIFIER':
            #       print("memld RX,",node.data)

            # elif node.name == 'VARIABLE':
            #       print("memld RX,",node.data)

            # elif node.name == 'BINARYOPERATOR':
            #       print("calc RX,", node, file=self.output)

        elif node.name == 'IF_ELSE':
            blockA = self.visit(node.children[1])
            blockB = self.visit(node.children[2])
            ifjumpNum = len(blockA)
            elsejumpNum = len(blockB)

            if node.children[0].name == 'BINARYOPERATOR':
                # instructionList.append("calc RX, %s" % node.children[0])

                instructionList.extend(self.internalVisit(node.children[0]))

                # If the calc register is virtual, we need to load it into a work register
                calcReg = node.children[0].register
                if calcReg.memory is not None:
                    calcReg = self.registerTracker.getWorkReg()
                    instructionList.append("memld %s, %i" % (calcReg.name, node.children[0].register.memory))

                instructionList.append("relbfalse %i, %s" % (ifjumpNum + 2, calcReg.name))

                # Free calculation register
                self.registerTracker.freeOneRegister(calcReg)
                if node.children[0].register.memory is not None:
                    self.registerTracker.freeOneRegister(node.children[0].register)

            elif node.children[0].name == 'VALUE':
                # Load that into a register for comparison
                valReg = self.registerTracker.getWorkReg()
                if node.children[0].data.isdigit():
                    # use immediate
                    instructionList.append("immld %s, %i" % (valReg.name, int(node.children[0].data)))
                else:
                    instructionList.append("memld %s, %i" % (valReg.name, self.mmap.lookUpVar(node.children[0].data, node.children[0].scopestack)))

                instructionList.append("relbfalse %i, %s" % (ifjumpNum + 2, valReg.name))
                self.registerTracker.freeOneRegister(valReg)

            instructionList.extend(blockA)
            instructionList.append("reljump %i" % (elsejumpNum + 1))
            instructionList.extend(blockB)

        elif node.name == 'IF':
            block = self.visit(node.children[1])
            jumpNum = len(block)

            if node.children[0].name == 'BINARYOPERATOR':
                # instructionList.append("calc RX, %s" % node.children[0])

                instructionList.extend(self.internalVisit(node.children[0]))

                # If the calc register is virtual, we need to load it into a work register
                calcReg = node.children[0].register
                if calcReg.memory is not None:
                    calcReg = self.registerTracker.getWorkReg()
                    instructionList.append("memld %s, %i" % (calcReg.name, node.children[0].memory))

                instructionList.append("relbfalse %i, %s" % (jumpNum + 1, calcReg.name))

                # Free calculation register
                self.registerTracker.freeOneRegister(calcReg)
                if node.children[0].register.memory is not None:
                    self.registerTracker.freeOneRegister(node.children[0].register)

                for instr in block:
                    instructionList.append(instr)

            elif node.children[0].name == 'VALUE':
                # Load that into a register for comparison
                valReg = self.registerTracker.getWorkReg()
                if node.children[0].data.isdigit():
                    # use immediate
                    instructionList.append("immld %s, %i" % (valReg.name, int(node.children[0].data)))
                else:
                    instructionList.append("memld %s, %i" % (valReg.name, self.mmap.lookUpVar(node.children[0].data, node.children[0].scopestack)))

                instructionList.append("relbfalse %i, %s" % (jumpNum + 2, valReg.name))
                self.registerTracker.freeOneRegister(valReg)

                for instr in block:
                    instructionList.append(instr)

        elif node.name == 'WHILE':
            block = self.visit(node.children[1])
            jumpNum = len(block)
            if node.children[0].name == 'BINARYOPERATOR':
                # instructionList.append("calc RX %s" % node.children[0])

                instructionList.extend(self.internalVisit(node.children[0]))

                # If the calc register is virtual, we need to load it into a work register
                calcReg = node.children[0].register
                if calcReg.memory is not None:
                    calcReg = self.registerTracker.getWorkReg()
                    instructionList.append("memld %s, %i" % (calcReg.name, node.children[0].memory))

                instructionList.append("relbfalse %i, %s" % (jumpNum + 2, calcReg.name))

                # Free calculation register
                self.registerTracker.freeOneRegister(calcReg)
                if node.children[0].register.memory is not None:
                    self.registerTracker.freeOneRegister(node.children[0].register)

                for instr in block:
                    instructionList.append(instr)

                instructionList.append("reljump %s" % str(-1 * jumpNum))

        elif node.name == 'ASSIGN':
            #print("calc RX,",node.children[1], file=self.output)

            instructionList.extend(self.internalVisit(node.children[1]))

            destMemAddr = self.mmap.lookUpVar(node.children[0].data, node.children[0].scopestack)
            if node.children[1].register.memory is None:
                instructionList.append("memst %s, %i" % (node.children[1].register.name, destMemAddr))
            else:
                # The result register is in virtual memory. Copy from a memory location into the actual memory location
                wreg = self.registerTracker.getWorkReg()
                instructionList.append("memld %s, %i" % (wreg.name, node.children[1].register.memory))
                instructionList.append("memst %s, %i" % (wreg.name, destMemAddr))
                self.registerTracker.freeOneRegister(wreg)

            self.registerTracker.freeOneRegister(node.children[1].register)

            # instructionList.append("calc RX, %s" % str(node.children[1]))
            #i = node.children[0].data
            #j = self.symboltable.retrieveScope(i, stack=node.children[0].scopestack)
            #print("memst RX,",self.mmap[j], file=self.output)
            #instructionList.append("memst RX, %s" % str(self.mmap.lookUpVar(node.children[0].data, node.children[0].scopestack)))

        elif node.name == 'DECL':
            currVarScope = self.symboltable.retrieveScope(node.children[1].data, stack=node.children[1].scopestack)
            self.mmap.allocateScope([currVarScope])

            if len(node.children) > 2:
                if node.children[2].name != 'MULTI_ASSIGN':
                    #print("calc RX,",node.children[2], file=self.output)
                    #instructionList.append("calc RX, %s" % str(node.children[2]))

                    instructionList.extend(self.internalVisit(node.children[2]))

                    destMemAddr = self.mmap.lookUpVar(node.children[1].data, node.children[1].scopestack)
                    if node.children[2].register.memory is None:
                        instructionList.append("memst %s, %i" % (node.children[2].register.name, destMemAddr))
                    else:
                        # The result register is in virtual memory. Copy from a memory location into the actual memory location
                        wreg = self.registerTracker.getWorkReg()
                        instructionList.append("memld %s, %i" % (wreg.name, node.children[2].register.memory))
                        instructionList.append("memst %s, %i" % (wreg.name, destMemAddr))
                        self.registerTracker.freeOneRegister(wreg)

                    self.registerTracker.freeOneRegister(node.children[2].register)

                    # i = node.children[1].data
                    # j = self.symboltable.retrieveScope(i, stack=node.children[1].scopestack)
                    #print("memst RX,",self.mmap[j], file=self.output)
                    # instructionList.append("memst RX, %s" % str(self.mmap.lookUpVar(node.children[1].data, node.children[1].scopestack)))
                else:
                    instructionList += self.visit(node.children[2])

        elif node.name == 'MULTI_ASSIGN':
            currVarScope = self.symboltable.retrieveScope(node.children[0].data, stack=node.children[0].scopestack)
            self.mmap.allocateScope([currVarScope])

            #print("calc RD,",node.children[1], file=self.output)
            instructionList.extend(self.internalVisit(node.children[1]))

            i = node.children[0].data
            j = self.symboltable.retrieveScope(i)
            #print("memst RX,",self.mmap[j], file=self.output)
            destMemAddr = self.mmap.lookUpVar(node.children[0].data, node.children[0].scopestack)
            if node.children[1].register.memory is None:
                instructionList.append("memst %s, %i" % (node.children[1].register.name, destMemAddr))
            else:
                # The result register is in virtual memory. Copy from a memory location into the actual memory location
                wreg = self.registerTracker.getWorkReg()
                instructionList.append("memld %s, %i" % (wreg.name, node.children[1].register.memory))
                instructionList.append("memst %s, %i" % (wreg.name, destMemAddr))
                self.registerTracker.freeOneRegister(wreg)

            # Free the calculation destination register
            self.registerTracker.freeOneRegister(node.children[1].register)

            if len(node.children) > 2 and node.children[2].name == 'MULTI_ASSIGN':
                instructionList.extend(self.visit(node.children[2]))

        elif node.name == 'MULTI':
            currVarScope = self.symboltable.retrieveScope(node.children[0].data, stack=node.children[0].scopestack)
            symboltable.allocateScope([currVarScope])
            instructionList = []
            for child in node.children:
                instructionList += self.visit(child)

        elif node.name == 'CODEBLOCK':
            instructionList = []
            for child in node.children:
                instructionList += self.visit(child)

            codeBlockScope = node.children[0].scopestack[0]
            self.mmap.deallocateScope(codeBlockScope);

        elif node.name == 'START':
            instructionList = []
            for child in node.children:
                instructionList += self.visit(child)
            for instr in instructionList:
                print(instr, file=self.output)

        else:
            instructionList = []
            for child in node.children:
                instructionList += self.visit(child)

        return instructionList

    def internalVisit(self, node):
        instructionList = []

        if node.name == 'BINARYOPERATOR':
            # Recurse upon the child with the LARGEST register requirements first
            # If the requirements are equal, the right side is traversed
            instructionList.extend(self.internalVisit(node.children[0]
                               if node.children[0].regCount > node.children[1].regCount
                               else node.children[1]))
            instructionList.extend(self.internalVisit(node.children[0]
                               if node.children[0].regCount <= node.children[1].regCount
                               else node.children[1]))

            # Choose the best destination. Note that the parent register (node.register) COULD be virtual
            if (node.children[0].register.isMoreOptimal(node.children[1].register)):
                node.register = node.children[0].register
            else:
                node.register = node.children[1].register
            
            # Convert the child registers into work registers if they are virtual
            # Remember what the original virtual registers are, so that we can deallocate them later

            oldVirtualRegisters = []
            for childIndex in range(0, len(node.children)):
                if node.children[childIndex].register.memory is not None:
                    oldVirtualRegisters.append((node.children[childIndex].register, childIndex))
                    node.children[childIndex].register = self.registerTracker.getWorkReg()
 
                   # When we convert the register into a work register, we need to load it into the work register for use
                    # in the calculation
                    instructionList.append("memld " + node.children[childIndex].register.name + ", " + oldVirtualRegisters[-1][0].name)

            # Find which child register is optimal, so that we can place the result appropriately
            # Since the children cannot be virtual anymore, the operand and result location WILL
            # be real registers (not virtual)
            optimalChild = (0 if node.children[0].register.isMoreOptimal(node.children[1].register) 
                              else 1)

            # Make the instruction
            instructionList.append(node.data + " " + 
                                       node.children[optimalChild].register.name
                                       + " ," + node.children[0].register.name + ", " + node.children[1].register.name)

            # if the result is supposed to be in a virtual register, we need to copy it from the
            # real register into the virtual register.
            if node.register.memory is not None:
                instructionList.append("memst %s, %i" % (node.children[optimalChild].name, node.register.memory))

            # Deallocate ALL registers, so long as they do NOT contain the result (used by the parent)
            for child in node.children:
                if child.register is not node.register:
                    self.registerTracker.freeOneRegister(child.register)

            for oldReg, childIndex in oldVirtualRegisters:
                if oldReg is not node.register:
                    self.registerTracker.freeOneRegister(oldReg)

        elif node.name == 'VALUE':
            node.register = self.registerTracker.getReg()
            if isinstance(node.data, int):
                if node.register.memory is None:
                    instructionList.append("immld %s, %i" % (node.register.name, node.data))
                else:
                    instructionList.append("immpush %i" % (node.data))
                    instructionList.append("mempop %i" % (node.register.memory))
            else:
                srcMemAddr = self.mmap.lookUpVar(node.data, node.scopestack)
                if node.register.memory is None:
                    instructionList.append("memld %s, %i" % (node.register.name, srcMemAddr))
                else:
                    tempReg = self.registerTracker.getWorkReg()
                    instructionList.append("memld %s, %i" % (tempReg.name, srcMemAddr))
                    instructionList.append("memst %s, %i" % (tempReg.name, node.register.memory))
                    self.registerTracker.freeOneRegister(tempReg)

        return instructionList

class PrintWithStrahlerNumber(Visitor):
    def __init__(self, file=stdout):
        self.idcount = 0
        self.output = file

    def prettyChildren(self, node):
        return "%s" % (id(node))

    def visit(self, node):
        # print("%s\t%s" % (id(node), node.name if node.kind is not None else node.data), file=self.output)
        print("%s\t%s%s%s%s"
            % (
                  id(node)
                , node.name
                , ( "" if node.name is node.data else ("="+str(node.data)))
                , ( "" if node.name not in ["BINARYOPERATOR", "VALUE", "IDENTIFIER"] or node.regCount is None else "(%i)" % node.regCount )
                , ( "" if node.register is None else " <" + (node.register.name if node.register.memory is None else str(node.register.memory)) + ">")
            ), file=self.output)

        if len(node.children) > 0:
            print(id(node), end=" ", file=self.output)
            for child in node.children:
                print(id(child), end=" ", file=self.output)
            print(file=self.output)

        self.idcount+=1
        # print(type(super()))

        super().visit(node)


# Sethi Ullman register needs algorithm
class RegisterNeedsVisitor(Visitor):

    # Travels to all the arithmetic syntax parts, and decorates them with
    #   register needs
    def visit(self, node):
        if node.name == 'BINARYOPERATOR':
            if len(node.children) is 0:
                node.regCount = 0
            else:
                #print("%s -> %s(%s) : %s(%s)" % (node.name, node.children[0].name, node.children[0].regCount, node.children[1].name, node.children[1].regCount))
                self.visit(node.children[0])
                self.visit(node.children[1])
                #print("%s -> %s(%s) : %s(%s)" % (node.name, node.children[0].name, node.children[0].regCount, node.children[1].name, node.children[1].regCount))

                if node.children[0].regCount == node.children[1].regCount:
                    node.regCount = node.children[1].regCount + 1
                else:
                    node.regCount = max(node.children[0].regCount, node.children[1].regCount)
        elif (node.name == 'IDENTIFIER' or node.name == 'VALUE') and node.parent.name in ['BINARYOPERATOR', 'EXPR', 'EXPR_BINOP']:
            node.regCount = 1
        else:
            # Recurse down to all the binaryoperator nodes
            super().visit(node)









