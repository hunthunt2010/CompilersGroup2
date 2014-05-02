#!/usr/bin/env python

class RegisterTracker:
	def __init__(self):
		self.allocRegNum = 9 
		self.workRegNum = 3

		#register representation
		self.regList = [False] * self.allocRegNum
		self.workRegList = [False] * self.workRegNum

		#stack pointer
		self.sp = 34767

	def getWorkReg(self):
		for i in range(0, self.workRegNum - 1):
			if self.workRegList[i] == False:
				self.workRegList[i] = True
				return i + self.allocRegNum

	def getReg(self):
		for i in range(0, self.allocRegNum - 1):
			if self.regList[i] == False:
				self.regList[i] = True
				return i

	def freeReg(self, regNum):
		self.regList[regNum] == False







