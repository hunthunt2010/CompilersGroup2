#!/usr/bin/env python

class Register:
	def __init__(self, name, memory=None):
		self.name = name
		self.memoryloc = memory 
		self.assigned = False


class RegisterTracker:
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
		self.sp = 34767

	def getWorkReg(self):
		for i in range(0, self.workRegNum):
			if self.workRegList[i].assigned == False:
				self.workRegList[i].assigned = True
				return workRegList[i]

	def getReg(self):
		for i in range(0, self.allocRegNum):
			if self.regList[i].assigned == False:
				self.regList[i].assigned = True
				return self.regList[i]

		#if Virtual
		vReg = Register('Virtual', self.sp)
		self.sp -= 8
		return vReg

	def freeAllocReg(self, regName):
		for reg in self.allocRegList:
			if reg.name == regName:
				reg.assigned == False

	def freeWorkReg(self, regName):
		for reg in self.WorkRegList:
			if reg.name == regName:
				reg.assigned == False

	#Passes in number of registers to free NOT amount of memory to free
	def freeVirtualReg(self, numToFree):
		self.sp += (numToFree * 8)







