
# NOTES: When using this program, you have to make some slight alterations manually to the .txt file. First, add "--start of poem--" just before line 1.
# Also, since debugging every special case would be a big challenge, I included code to note where the program's internal representation of line number
# contrasts with what Luke's book says. Just go into the text file and fix it manually. Also make sure to manually check lines that look like 224a, or other weird ones
# 

import csv
import pickle
import re

class BigOvidIndex:
	def __init__(self, ovidIndexFilename, ovidBookFilenames):

		with open(ovidIndexFilename, 'rb') as handle:
			self.namesDict = pickle.load(handle)
		self.ovidIndexFilename = ovidIndexFilename
		self.ovidBookFilenames = ovidBookFilenames

	def update(self):
		
		with open(self.ovidIndexFilename, 'wb') as handle:
			pickle.dump(self.namesDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
		

	def findName(self, name):
		
		allInstancesOfName = {name:[]}
		romanNumerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
		rnCount = 0

		for filename in self.ovidBookFilenames:
			print("Book " + romanNumerals[rnCount] + ":")
			ovidBookIndex = OvidBookIndex(filename)
			ovidBookIndex.addName(name)
			bookIndex = ovidBookIndex.indexDictionary() #here I get the locations of the name for a specific book
			#print(filename.split('/')[-1] + ":")

			#append the correct roman numeral to the first index item
			if not bookIndex[name]:
				print(name + " not in", filename.split('/')[-1])
				print()
				print()
				rnCount +=1
				continue
			
			#print(romanNumerals[rnCount])
			bookIndex[name][0] = romanNumerals[rnCount] + '.' + str(bookIndex[name][0]) #note that all entries in the list except first and last are integers
			rnCount +=1
			#print(bookIndex[name])
			print()
			print()

			#get the semicolon at the end of the list
			if len(bookIndex[name]) > 0:
				bookIndex[name][-1] = str(bookIndex[name][-1]) + ';'

			allInstancesOfName[name].append(bookIndex[name])

			# print(allInstancesOfName)
		if allInstancesOfName[name]:
			self.namesDict.update({name: allInstancesOfName[name]})
			print()
			print("Instances of \'" + name + "\':")
			print(self.namesDict[name])
			# self.updateCSV(allInstancesOfName)

	def deleteName(self, name = 0):
		if name in self.namesDict:
			self.namesDict.pop(name)
			print()
			print("\'" + name + "\' deleted from Index.")

	def makeIndex(self):
		# with open("index.txt", "w") as index:
		index = open("/Users/truszala/Documents/python!/Metamorphoses/index.txt", "w")
		sortedDictTuple = sorted(self.namesDict.items())


		for item in sortedDictTuple:
			# print()
			# print(item)
			lineNumbers = str(item[1]).replace('\'', '').replace("],", '').replace("[", '').replace("]", '')
			index.write(str(item[0]) + ":" + '\n' + lineNumbers)
			index.write('\n' + '\n')
			# print(key)

		print()
		print("Index Updated.")


# Object to represent Luke's book
class OvidBookIndex:
	def __init__(self, fullFilename):
		self.file = fullFilename
		self.indexDict = {}
	

	def addName(self, name):
		
		listOfLineNumbersForThisName = []
		f = open(self.file, 'r')
		

		haveWeReachedThePoem = False #flag variable to help us find the first line of the poem, initially false
		while haveWeReachedThePoem == False:
			l = f.readline()
			if "--start of poem--" in l:
				haveWeReachedThePoem = True
		

		lineNumber = 1
		for eachLine in f:
			#print(eachLine, lineNumber)
			regEx = name + '\\W'
			if re.search(regEx, eachLine, re.IGNORECASE):
			#if name in eachLine:
				listOfLineNumbersForThisName.append(lineNumber)
				print(lineNumber, eachLine)
				#print(eachLine, lineNumber)
				#self.indexDict.update({name: lineNumber})
			if not eachLine.isspace(): #skipping blank lines, i.e. section breaks
				if eachLine[-3].isdigit(): #checking to see if the end of the line contains a number. Note that this won't work for numbers like 544a* in book 1. Not sure what do do about that. Maybe find those lines individually and index them.
					lineNumberInBook = int(eachLine.split()[-1]) #gets the line number
					if lineNumber != lineNumberInBook:
						print("lineNumber = ", lineNumber, "; lineNumberInBook = ", lineNumberInBook) #because this situation won't happen super often, and could be gnarly, we'll do this by hand, i.e.: Edit the .txt file.
						print(eachLine)
				lineNumber += 1
			if "TRANSLATION NOTES" in eachLine:
				break

		self.indexDict.update({name: listOfLineNumbersForThisName})

	def indexDictionary(self):
		return self.indexDict






def main():

	directory = "/Users/truszala/Documents/python!/Metamorphoses/"
	ovidIndexFilename = directory + "OvidIndex.txt"
	ovidBookFilenames = [directory + "LiberPrimus.txt", directory + "LiberSecundus.txt", directory + "LiberTertius.txt", directory + "LiberQuartus.txt", 
						 directory + "LiberQuintus.txt", directory + "LiberSextus.txt", directory + "LiberSeptimus.txt", directory + "LiberOctauus.txt",
						 directory + "LiberNonus.txt", directory + "LiberDecimus.txt", directory + "LiberUndecimus.txt", directory + "LiberDuodecimus.txt", 
						 directory + "LiberTertiusDecimus.txt", directory + "LiberQuartusDecimus.txt", directory + "LiberQuintusDecimus.txt"]
	bigOvidIndex = BigOvidIndex(ovidIndexFilename, ovidBookFilenames)
	
###########################################################################################################################################################################

#																			LUKE LOOK HERE!

# INSTRUCTIONS: Use the findName() command below to add names to the index, with information on every place that name appears. 
# -Make sure to put the name between single or double quotation marks.
# -If you need to search for something with an apostrophe, copy/paste this charater: ’    (Typing a single quotation mark won't do the trick.)
# -Also, if you try to findName() a name which has already been added, nothing bad will happen. :)

# example:
# 	bigOvidIndex.findName('Jove')
	bigOvidIndex.findName('Jove')

# Use deleteName() if you accidentally mispelled a name and need to remove it from the index.
# example:
#	bigOvidIndex.deleteName('duck')
	bigOvidIndex.deleteName()


###########################################################################################################################################################################



	bigOvidIndex.makeIndex()
	bigOvidIndex.update()
	
	# for key in bigOvidIndex.namesDict:
	# 	print()
	# 	print(key)
	# 	print(bigOvidIndex.namesDict[key])


if __name__ == "__main__":
	main()











