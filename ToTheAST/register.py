#!/usr/bin/env python3

class Register:
	def __init__(self, name, memory=None):
		self.name = name
		self.memory = memory 
		self.assigned = False

	def __str__(self):
		return "name: " + self.name + " Memory: " + str(self.memory) + " allocated: " + str(self.assigned)

	def isMoreOptimal(self, reg):
		if (reg is None):
			return False
		if (self.memory is None) and (reg.memory is not None):
			return True
		elif (self.memory is not None) and (reg.memory is None):
			return False
		elif self.name < reg.name:
			return True
		else:
			return False

class RegisterTracker:
	baseSp = 34768

	def __init__(self):
		self.allocRegNum = 9 
		self.workRegNum = 3

		self.allocRegList = []
		#register representation
		for i in range(0, self.allocRegNum):
			self.allocRegList.append(Register('R%d' % i))

		self.workRegList = []
		#register representation
		for i in range(0, self.workRegNum):
			self.workRegList.append(Register('R%d' % (i + self.allocRegNum)))

		#stack pointer
		self.sp = self.baseSp

	def getWorkReg(self):
		for i in range(0, self.workRegNum):
			if self.workRegList[i].assigned == False:
				self.workRegList[i].assigned = True
				return self.workRegList[i]
		raise Exception('NO MORE WORKING REGISTERS TO ALLOCATE!!!!!')

	def getReg(self):
		for i in range(0, self.allocRegNum):
			if self.allocRegList[i].assigned == False:
				self.allocRegList[i].assigned = True
				return self.allocRegList[i]

		#if Virtual
		vReg = Register('Virtual', self.sp)
		self.sp -= 8
		return vReg

	def freeAllocReg(self, regName):
		for reg in self.allocRegList:
			
			if reg.name == regName:
				if reg.assigned == False:
					raise Exception('Allocatable register ' + reg.name + ' is already free')
				else:
					reg.assigned = False

	def freeWorkReg(self, regName):
		for reg in self.workRegList:
			if reg.name == regName:
				if reg.assigned == False:
					raise Exception('Working register ' + reg.name + ' is already free')
				else:
					reg.assigned = False

	#Passes in number of registers to free NOT amount of memory to free
	def freeVirtualReg(self, numToFree):
		if (self.sp + (numToFree * 8)) > self.baseSp:
			raise Exception('NOTHING VIRTUAL LEFT TO DEALLOCATE!!!!')
		else:
			self.sp += (numToFree * 8)

	def freeOneRegister(self, reg):
		if (reg.memory is None):
			for i in range(0, len(self.allocRegList)):
				if reg.name == self.allocRegList[i].name:
					self.freeAllocReg(reg.name)
					return
			for i in range(0, len(self.workRegList)):
				if reg.name == self.workRegList[i].name:
					self.freeWorkReg(reg.name)
					return
		else:
			self.freeVirtualReg(1)









