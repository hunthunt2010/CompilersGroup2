#!/usr/bin/env python

#Taylor Schmidt
#ToTheAST group assignment
#namespace implementation

class Namespace:

	nameString = ''

	def __init__ (self):
		#Not much to initialize

	def addName (newName):
		"takes a new name string as an arg and returns a tuple with its index and length in the global string"
		
		nameLength = len(newName)

		#check if name already exists in namespace, if not add it
		if nameString.find(newName) != -1:
			nameIndex = nameString.find(newName)
			return (nameIndex, nameLength)
		else
			nameIndex = len(nameString)
			nameString = nameString + newName
			return (nameIndex, nameLength)

	def getName (nameTuple):
		"takes a name tuple as an arg (nameIndex, nameLength) and returns the string representation from the namespace"

		nameIndex = nameTuple[0]
		endIndex = nameIndex + (nameTuple[1] -1)

		return nameString[nameIndex:endIndex]

