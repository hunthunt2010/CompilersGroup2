#!/usr/bin/env python

#Taylor Schmidt
#ToTheAST group assignment
#namespace implementation

class Namespace:

	def __init__ (self):
		self.nameString = ''

	def addName(self, newName):
		"takes a new name string as an arg and returns a tuple with its index and length in the global string"
		
		nameLength = len(newName)

		#check if name already exists in namespace, if not add it
		if self.nameString.find(newName) != -1:
			nameIndex = self.nameString.find(newName)
			return (nameIndex, nameLength)
		else:
			nameIndex = len(self.nameString)
			self.nameString = self.nameString + newName
			return (nameIndex, nameLength)

	def getName(self, nameTuple):
		"takes a name tuple as an arg (nameIndex, nameLength) and returns the string representation from the namespace"

		nameIndex = nameTuple[0]
		endIndex = nameIndex + (nameTuple[1])

		return self.nameString[nameIndex:endIndex]



