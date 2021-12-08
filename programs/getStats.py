from music21 import *
import bigScore
import getProgs
import pprint
import operator
import csvOperations
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
randn = np.random.randn
import progs
import showMeasures
from tabulate import tabulate
from string import digits

# NOTE: the methods here were designed for my personal use, and I make no
# guarantee that they will work for you.

# GetStats.py is a library which allows statistical data to be collected
# from the voice-leading data collected in getProgs.py.

# Takes as parameters a progs dict, and a mode ("maj" or "min").
# Prints a list of progressions and the percent of all progressions
# that they make up. Also returns the data as a list.

def rnStats(progs, mode = "maj"):
	rnStats = []
	totalNumberOfProgressions = 0
	if mode == "maj":
		for rnProg in progs["maj"]:
			rnProgCount = len(progs["maj"][rnProg])
			totalNumberOfProgressions += rnProgCount
			frequency = float(rnProgCount)
			rnStats.append([frequency, rnProg])
	else:
		for rnProg in progs["min"]:
			rnProgCount = len(progs["min"][rnProg])
			totalNumberOfProgressions += rnProgCount
			frequency = float(rnProgCount)
			rnStats.append([frequency, rnProg])
	for i in range(0, len(progs[mode])):
		try:
			rnStats[i][0] = rnStats[i][0]/totalNumberOfProgressions * 100
		except:
			print(rnStats[i])
	rnStats.sort(reverse = False)

	pprint.pprint(rnStats)
	# print(totalNumberOfProgressions)
	# print(statsCheckList0(rnStats))

	return rnStats


def countRnProgs(progs):
	rnStatsMaj = rnStatsNoInversions(progs, mode = "maj", counts = True)
	rnStatsMin = rnStatsNoInversions(progs, mode = "min", counts = True)

	total = 0
	for item in rnStatsMaj:
		total += item[1]
	for item in rnStatsMin:
		total += item[1]
	return total


def searchRnStats(rnStatsList, rnProg):
	results = []
	total = 0
	for item in rnStatsList:
		print(item)
		print(rnProg)
		if getRnNoInv(item[0][0]) == getRnNoInv(rnProg[0]) and getRnNoInv(item[0][1]) == getRnNoInv(rnProg[1]):
			results.append(item)
			total += item[1]
	pprint.pprint(results)
	return total

# These methods help to count the number of progressions.
def statsCheckList0(rnStats):
	total = 0
	for item in rnStats:
		total += item[0]
	return total

def statsCheckList1(rnStats):
	total = 0
	for item in rnStats:
		total += item[1]
	return total

# takes two rn strings (roman numerals) as parameters, and returns
# them in root position.
def getRnProgNoInv(rnProg, sevenths = True):
	
	cleanRN1 = rnProg[0]
	cleanRN2 = rnProg[1]

	if sevenths:
		cleanRN1 = cleanRN1.replace('6/5', '7')
		cleanRN1 = cleanRN1.replace('4/3', '7')
		cleanRN1 = cleanRN1.replace('2', '7')

		cleanRN2 = cleanRN2.replace('6/5', '7')
		cleanRN2 = cleanRN2.replace('4/3', '7')
		cleanRN2 = cleanRN2.replace('2', '7')
		remove_digits = str.maketrans('', '', '012345689') # no 7

	else:
		remove_digits = str.maketrans('', '', '0123456789') # no 7

	cleanRN1 = cleanRN1.translate(remove_digits).replace('//', '/')
	if cleanRN1.endswith('/'):
		cleanRN1 = cleanRN1[0:-1]
	cleanRN2 = cleanRN2.translate(remove_digits).replace('//', '/')
	if cleanRN2.endswith('/'):
		cleanRN2 = cleanRN2[0:-1]
	res = (cleanRN1, cleanRN2)

	return res

# takes a rn string (roman numeral) as a parameter, and returns
# the root position roman numeral.
def getRnNoInv(rn, sevenths = True):

	cleanRN1 = rn

	if sevenths:
		cleanRN1 = cleanRN1.replace('6/5', '7')
		cleanRN1 = cleanRN1.replace('4/3', '7')
		cleanRN1 = cleanRN1.replace('2', '7')

		remove_digits = str.maketrans('', '', '012345689') # no 7

	else:
		remove_digits = str.maketrans('', '', '0123456789') # no 7

	cleanRN1 = cleanRN1.translate(remove_digits).replace('//', '/')
	if cleanRN1.endswith('/'):
		cleanRN1 = cleanRN1[0:-1]

	return cleanRN1

# Creates a list of progressions, abstracted away from inversion, and also
# prints that list.
def rnStatsNoInversions(progs, mode = "maj", sevenths = True, counts = False):
	rnStats = []
	rnStatsDict = {}
	totalNumberOfProgressions = 0
	if mode == "maj":
		for rnProg in progs["maj"]:
			if rnProg[0] == rnProg[1]:
				continue
			if sevenths == False:
				rnProgNoInv = getRnProgNoInv(rnProg, sevenths = False)
			else:
				rnProgNoInv = getRnProgNoInv(rnProg, sevenths = True)
			rnProgCount = len(progs["maj"][rnProg])
			if rnProgNoInv not in rnStatsDict:
				rnStatsDict[rnProgNoInv] = rnProgCount
				totalNumberOfProgressions += rnProgCount
			else:
				rnStatsDict[rnProgNoInv] += rnProgCount
				totalNumberOfProgressions += rnProgCount
		for key in rnStatsDict:
			if counts:
				rnStats.append((key, rnStatsDict[key]))
			else:
				rnStats.append((key, ((rnStatsDict[key]/totalNumberOfProgressions) * 100)))
	else:
		for rnProg in progs["min"]:
			if rnProg[0] == rnProg[1]:
				continue
			if sevenths == False:
				rnProgNoInv = getRnProgNoInv(rnProg, sevenths = False)
			else:
				rnProgNoInv = getRnProgNoInv(rnProg, sevenths = True)
			rnProgCount = len(progs["min"][rnProg])
			if rnProgNoInv not in rnStatsDict:
				rnStatsDict[rnProgNoInv] = rnProgCount
				totalNumberOfProgressions = len(progs["min"])
			else:
				rnStatsDict[rnProgNoInv] += rnProgCount
				totalNumberOfProgressions = len(progs["min"])
		for key in rnStatsDict:
			if counts:
				rnStats.append((key, rnStatsDict[key]))
			else:
				rnStats.append((key, ((rnStatsDict[key]/totalNumberOfProgressions) * 100)))
	rnStats.sort(reverse = False, key = operator.itemgetter(1))

	pprint.pprint(rnStats)
	print(totalNumberOfProgressions)
	print(statsCheckList1(rnStats))


	return rnStats

def sortSecond(val): 
    return val[1] 




# e.g. 50% I, 25% V
# if rn is specified, gives only the inversions for that rn.
def rnPercentages(progs, mode = "maj", counts = False, rn = None):
	rnPercentDict = {}
	totalRnCount = 0
	if rn == None:
		for rnTuple in progs[mode]:
			if rnTuple[0] == rnTuple[1]:
				continue
			for i in range(0, 2):
				l = len(progs[mode][rnTuple])
				if rnTuple[i] not in rnPercentDict:
					rnPercentDict[rnTuple[i]] = l
					totalRnCount += l
				else:
					rnPercentDict[rnTuple[i]] += l
					totalRnCount += l
		
		if counts:	# i.e. the actual numbers of each rn
			sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
			pprint.pprint(sortedRnPercentDict)
		else:
			for key in rnPercentDict:
				rnPercentDict[key] = rnPercentDict[key] / totalRnCount * 100
			sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
			pprint.pprint(sortedRnPercentDict)
		print(totalRnCount)
		print(statsCheckList1(sortedRnPercentDict))

		return sortedRnPercentDict

	else:
		rn = getRnNoInv(rn)
		for rnTuple in progs[mode]:
			if rnTuple[0] == rnTuple[1]:
				continue
			for i in range(0, 2):
				if getRnNoInv(rnTuple[i]) != rn:
					continue
				l = len(progs[mode][rnTuple])
				if rnTuple[i] not in rnPercentDict:
					rnPercentDict[rnTuple[i]] = l
					totalRnCount += l
				else:
					rnPercentDict[rnTuple[i]] += l
					totalRnCount += l
		
		if counts:	# i.e. the actual numbers of each rn
			sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
			pprint.pprint(sortedRnPercentDict)
		else:
			for key in rnPercentDict:
				rnPercentDict[key] = rnPercentDict[key] / totalRnCount * 100
			sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
			pprint.pprint(sortedRnPercentDict)
		print(totalRnCount)
		print(statsCheckList1(sortedRnPercentDict))

		return sortedRnPercentDict




def rnPercentagesNoInversions(progs, mode = "maj", counts = False, sevenths = True):
	rnPercentDict = {}
	totalRnCount = 0
	
	for rnTuple in progs[mode]:
		if rnTuple[0] == rnTuple[1]:
			continue
		for i in range(0, 2):
			l = len(progs[mode][rnTuple])
			if sevenths:
				rnNoInv = getRnNoInv(rnTuple[i])
			else:
				rnNoInv = getRnNoInv(rnTuple[i], sevenths = False)
			if rnNoInv not in rnPercentDict:
				rnPercentDict[rnNoInv] = l
				totalRnCount += l
			else:
				rnPercentDict[rnNoInv] += l
				totalRnCount += l
		if getRnNoInv(rnTuple[0]) == 'V7':
			for tup in progs[mode][rnTuple]:
				print(tup[0][0])
				print(tup[1])
				print(tup[6])
	if counts:	# i.e. the actual numbers of each rn
		sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
		pprint.pprint(sortedRnPercentDict)
	else:
		for key in rnPercentDict:
			rnPercentDict[key] = rnPercentDict[key] / totalRnCount * 100
		sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))
		pprint.pprint(sortedRnPercentDict)
	print(totalRnCount)
	print(statsCheckList1(sortedRnPercentDict))
	return sortedRnPercentDict


def whereWillMyChordGo(rn, progs, mode = "maj", counts = False, excludeInversions = False):
	rnPercentDict = {}
	totalRnCount = 0

	if excludeInversions:
		rn = getRnNoInv(rn)

	for rnTuple in progs[mode]:
		if excludeInversions:
			testingRn = getRnNoInv(rnTuple[0])
		else:
			testingRn = rnTuple[0]
		if rnTuple[0] == rn:
			if rnTuple[1] == rn:
				continue
			l = len(progs[mode][rnTuple])
			rnPercentDict[rnTuple[1]] = l
			totalRnCount += l

	if not counts:
		for key in rnPercentDict:
			rnPercentDict[key] = rnPercentDict[key] / totalRnCount * 100
	sortedRnPercentDict = sorted(rnPercentDict.items(), key = operator.itemgetter(1))

	rnString = rn.replace('/', '-') + "_" + str(random.randint(1, 999))
	print(rnString)
	if excludeInversions:
		filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/whereWillMyChordGo_excludeInversions_" + mode + "_" + rnString + ".csv"
	else:
		filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/whereWillMyChordGo_" + mode + "_" +  rnString + ".csv"
	csvOperations.exportList(sortedRnPercentDict, filename, headers = ['rn', 'frequency'])
	print("totalRnCount for " + rn + ":", totalRnCount)
	return(sortedRnPercentDict)

def whereWillMyChordGoForAllChords(progs):
	rnList = []
	
	rnPmaj = rnPercentages(progs, "maj")
	rnPmin = rnPercentages(progs, "min")

	for tup in rnPmaj:
		whereWillMyChordGo(tup[0], progs, mode = "maj", excludeInversions = False)
		whereWillMyChordGo(tup[0], progs, mode = "maj", excludeInversions = True)
	for tup in rnPmin:
		whereWillMyChordGo(tup[0], progs, mode = "min", excludeInversions = False)
		whereWillMyChordGo(tup[0], progs, mode = "min", excludeInversions = True)

	print("we are finished.")
	return

def countVLdegree(progs):
	degreeAndFreqDict = {}
	vl1degrees = []
	vl2degrees = []
	frequencies = []
	for mode in ["maj", "min"]:
		for key in progs[mode]:
			for tup in progs[mode][key]:
				try:
					degree = tup[4]
				except:
					continue
				if degree not in degreeAndFreqDict:
					degreeAndFreqDict[degree] = 1
				else:
					degreeAndFreqDict[degree] += 1
	for key in degreeAndFreqDict:
		vl1degrees.append(key[0])
		vl2degrees.append(key[1])
		frequencies.append(degreeAndFreqDict[key])

	cell_text = []
	max1 = max(vl1degrees)
	row = []
	max2 = max(vl2degrees)
	col = []
	for i in range(0, max1 + 1):
		row.append(i)
		cell_text.append([])
		for j in range(0, max2 + 1):
			cell_text[i].append(0)
	for j in range(0, max2 + 1):
		col.append(j)
	for key in degreeAndFreqDict:
		cell_text[key[0]][key[1]] = degreeAndFreqDict[key]
	print(cell_text)


	dataF = pd.DataFrame(cell_text, index = row, columns = col)
	print(dataF)
	dataF.to_csv("/Users/truszala/Documents/1JuniorSpring/JP/CSVs/countDegrees/countVLdegree.csv")



def countBigVLdegree(progs):
	degreeAndFreqDict = {}
	vl1degrees = []
	vl2degrees = []
	frequencies = []
	for mode in ["maj", "min"]:
		for key in progs[mode]:
			for tup in progs[mode][key]:
				try:
					degree = tup[5]
				except:
					continue
				if degree not in degreeAndFreqDict:
					degreeAndFreqDict[degree] = 1
				else:
					degreeAndFreqDict[degree] += 1
	for key in degreeAndFreqDict:
		vl1degrees.append(key[0])
		vl2degrees.append(key[1])
		frequencies.append(degreeAndFreqDict[key])

	cell_text = []
	max1 = max(vl1degrees)
	row = []
	max2 = max(vl2degrees)
	col = []
	for i in range(0, max1 + 1):
		row.append(i)
		cell_text.append([])
		for j in range(0, max2 + 1):
			cell_text[i].append(0)
	for j in range(0, max2 + 1):
		col.append(j)
	for key in degreeAndFreqDict:
		cell_text[key[0]][key[1]] = degreeAndFreqDict[key]


	df = pd.DataFrame(cell_text, index = row, columns = col)
	print(df)
	df.to_csv("/Users/truszala/Documents/1JuniorSpring/JP/CSVs/countDegrees/countBigVLdegree.csv")


# sets up a movement
def load(fullFilename):

	with open(fullFilename + '.txt', 'r') as rnFile:
		for i in range(4):
			rnFile.readline()
		timeSignatureLine = rnFile.readline().split()
		timeSignature = meter.TimeSignature(timeSignatureLine[2])
		# Extracting the string parts
		movement = converter.parse(fullFilename + '.mxl')
		mvt = bigScore.BigScore(movement, timeSignature)

	return mvt

def getCleanVLs(progs):
	cleanVLlist = []
	for mode in ["maj", "min"]:
		for key in progs[mode]:
			for tup in progs[mode][key]:
				try:
					throwaway = (tup[3] and tup[4] == tup[5]) # this means: if VL.isSimple() and VL.degree == BVL.degree
				except:
					continue
				if tup[3] and tup[4] == tup[5]:
					cleanVLlist.append((key, tup))

	print("cleanVLlist got!")
	return cleanVLlist

def getCleanVLDict(progs):
	cleanVLDict = {"maj" : {}, "min" : {}}
	for mode in ["maj", "min"]:
		for rnProg in progs[mode]:
			for tup in progs[mode][rnProg]:
				try:
					throwaway = (tup[3] and tup[4] == tup[5]) # this means: if VL.isSimple() and VL.degree == BVL.degree
				except:
					continue
				if tup[3] and tup[4] == tup[5]:
					if rnProg not in cleanVLDict[mode]:
						cleanVLDict[mode][rnProg] = []
					cleanVLDict[mode][rnProg].append(tup)
	return cleanVLDict

# list entry example: ('V', range, generalIntervals)
def searchForIntervalStructure(pitchClasses, progs, rn1 = None, rn2 = None, inversions = False, mode = ["maj", "min"]):
	vlList = []
	if mode == "maj":
		mode = ["maj"]
	elif mode == "min":
		mode = ["min"]
	for m in mode:
		for key in progs[m]:
			if rn1:
				if not inversions:
					rn1 = getRnNoInv(rn1)
					keyCheck = getRnNoInv(key[0])
				else:
					keyCheck = key[0]
				if keyCheck != rn1:
					continue
			if rn2:
				if not inversions:
					rn2 = getRnNoInv(rn2)
					keyCheck = getRnNoInv(key[1])
				else:
					keyCheck = key[1]
				if keyCheck != rn2:
					continue
			for tup in progs[m][key]:
				try:
					genericIntervalDict = tup[6]
				except:
					#print("no genericIntervalDict")
					continue
				containsAllPitchClasses = True
				for pc in pitchClasses:
					if pc not in genericIntervalDict:
						containsAllPitchClasses = False
				if containsAllPitchClasses:
					vlList.append((key, tup[1], tup[6]))
	print("we have the vlList in searchForIntervalStructure()!")
	return vlList

# should now be defunct.
def transposeGenericIntervals(genericIntervals, rnStr):

	c = chord.Chord()
	print("old:", genericIntervals)
	for pc in genericIntervals:
		c.add(pc)
	c.simplifyEnharmonics(inPlace=True)
	chordRoot = c.root().pitchClass
	rn = roman.RomanNumeral(rnStr)
	rnRootInC = rn.root().pitchClass
	transposeFactor = rnRootInC - chordRoot
	newGenericIntervals = {}
	for key in genericIntervals:
		newGenericIntervals[(key + transposeFactor) % 12] = genericIntervals[key]
	print("new:", newGenericIntervals)
	return newGenericIntervals

""" helper method for searchForIntervalStructure(). pcPathList of type: ((5, -1), (11, 1))
    When exclusion is true, returns a list of all VLs which DON't follow the behavior prescribed in pcPathList. 
    For the above example, means that it returns VLs which don't resolve the tritone normally.
    When rn is specified, only returns VLs where the first Voicing has that rn.
"""
def searchForSpecificPcPaths(pcPathList, vlList, rn1 = None, rn2 = None, inversions = False, exclusion = False):
	resultList = []
	if not inversions:
		rn1 = getRnNoInv(rn1)
		rn2 = getRnNoInv(rn2)
	for tup in  vlList:
		shouldAppendTupFlag = True
		if rn1:
			if getRnNoInv(tup[0][0]) != rn1:
				continue
		if rn2:
			if getRnNoInv(tup[0][1]) != rn2:
				continue
		exclusionFlagCounter = 0
		# pcPath e.g.: (5, -1)
		genericIntervals = tup[2]
		for pcPath in pcPathList:
			relevantInterval = pcPath[0]
			if exclusion:
				if pcPath[0] in genericIntervals:
					if pcPath[1] in genericIntervals[pcPath[0]]:
						exclusionFlagCounter += 1
						if exclusionFlagCounter == len(pcPathList):
							shouldAppendTupFlag = False
				else:
					exclusionFlagCounter +=1
			else: # not exclusion
				if pcPath[0] in genericIntervals:
					if pcPath[1] not in tup[2][pcPath[0]]:
						shouldAppendTupFlag = False
				else:
					shouldAppendTupFlag = False
		if shouldAppendTupFlag:
			resultList.append(tup)
	return resultList

def graphListOfKeyValTups(keyValTups, title = "No Title", numberOfVals = 1):
	listSubset = keyValTups[(numberOfVals*-1):len(keyValTups)]
	chords = []
	freqs = []
	for i in range(0, len(listSubset)):
		chords.append(str(listSubset[i][0]))
		freqs.append(listSubset[i][1])
	print("CHORDSCHORDSCHORDSCHORDSCHORDSCHORDSCHORDSCHORDSCHORDSCHORDS")
	print(chords)
	print("FREQSFREQSFREQSFREQSFREQSFREQSFREQSFREQSFREQSFREQSFREQSFREQS")
	print(freqs)
	bar1 = plt.bar(chords, freqs)
	plt.ylim(0, 100)
	for rect in bar1:
		height = rect.get_height()
		plt.text(rect.get_x() + rect.get_width()/2.0, height, '%5.2f' % height, ha='center', va='bottom')
	plt.title(title)
	plt.xlabel('RNs')
	plt.ylabel("% Frequency")
	plt.show()


	plt.show()

def getDoublingStats(progs, doublingDictStorage, mode = ["maj", "min"]):
	doublingDict = {}
	if mode == "maj":
		mode = ["maj"]
	elif mode == "min":
		mode = ["min"]
	for m in mode:
		print(m)
		for rn in progs[m]:
			try:
				romanN = roman.RomanNumeral(rn[0])
			except:
				print("ERROR", romanN)
			root = romanN.root().pitchClass
			third = romanN.third.pitchClass
			fifth = romanN.fifth.pitchClass
			if romanN.seventh:
				seventh = romanN.seventh.pitchClass
			else:
				seventh = None
			for tup in progs[m][rn]:
				doublingList = [0, 0, 0, 0] # where each member of the list, in the order [root, third, fifth, seventh] contains the number of occurrences
				numberOfVoices = 0
				for pc in tup[6]:
					if pc == root:
						doublingDegree = len(tup[6][pc])
						doublingList[0] += doublingDegree
						numberOfVoices += doublingDegree
						continue
					elif pc == third:
						doublingDegree = len(tup[6][pc])
						doublingList[1] += doublingDegree
						numberOfVoices += doublingDegree
						continue
					elif pc == fifth:
						doublingDegree = len(tup[6][pc])
						doublingList[2] += doublingDegree
						numberOfVoices += doublingDegree
						continue
					elif pc == seventh:
						doublingDegree = len(tup[6][pc])
						doublingList[3] += doublingDegree
						numberOfVoices += doublingDegree
						continue
					else:
						print("pc error", pc, rn[0])
				print(doublingList, tup[6], tup[1])
				if numberOfVoices not in doublingDict:
					doublingDict[numberOfVoices] = {}
				if rn[0] not in doublingDict[numberOfVoices]:
					doublingDict[numberOfVoices][rn[0]] = {}
				doublingTup = ""
				for x in doublingList:
					doublingTup = doublingTup + str(x)
				if doublingTup not in doublingDict[numberOfVoices][rn[0]]:
					doublingDict[numberOfVoices][rn[0]][doublingTup] = 0
				doublingDict[numberOfVoices][rn[0]][doublingTup] += 1

	with open(doublingDictStorage, 'wb') as outfile:
		pickle.dump(doublingDict, outfile)
	return doublingDict


def makeTableForAGivenRnWithGetDoublingStats(doublingDict, rn, numberOfVoices = 4, counts = False, inversions = False):

	dic = doublingDict[numberOfVoices][rn]
	total = 0
	for doubling in dic:
		total += dic[doubling]
	if not counts:
		for doubling in dic:
			dic[doubling] = dic[doubling] / total * 100
	dicSorted = sorted(dic.items(), key = operator.itemgetter(1))
	print(rn)
	pprint.pprint(dicSorted)
	print()
	csvOperations.exportList(dicSorted, "/Users/truszala/Documents/1JuniorSpring/JP/doublingStats/" + rn.replace('/', '') + '.csv', headers = ["Doubling Distribution", "Percent Frequency"])

def main():

	giantProgDict = progs.Progs()
	giantProgDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay13a")
	gp = giantProgDict.progs
	print("gp loaded")

	doublingDictStorage = "/Users/truszala/Documents/1JuniorSpring/JP/doublingDictStorage"
	doublingDict = {}
	with open(doublingDictStorage, 'rb') as infile:
		doublingDict = pickle.load(infile)
	pprint.pprint(doublingDict)
	makeTableForAGivenRnWithGetDoublingStats(doublingDict, 'IV6', numberOfVoices = 4)
	makeTableForAGivenRnWithGetDoublingStats(doublingDict, 'ii', numberOfVoices = 4)
	

	# NOTE: DO NOT DELETE ANY OF THESE COMMENTS! THEY CONTAIN MANY IMPORTANT TESTS THAT YOU'LL WANT TO REDO EVENTUALLY.

	# filename = "/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no6_mov1"
	# mvt = getProgs.load(filename)

	# p = progs.Progs()
	# p.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op131_no14_mov2_progs")
	# p = p.progs
	# pprint.pprint(p)

	# print("progs been Got")

	# pprint.pprint(progDict)
	# pprint.pprint(rnStats(progDict, mode = "min"))
	# rnStatsNoInversions(progDict, mode = "maj", sevenths = True)

	# print(getRnProgNoInv(('V6/5', 'IV7')))
	# s = "V6/5"
	# print(s.replace("6/5", '7'))


	

	# print(rnStatsNoInversions(gp, "maj", counts = True))
	# print(rnStatsNoInversions(gp, "min", counts = True))


	# print(rnPercentagesNoInversions(gp, "maj", counts = True))

	# rnProgStats = rnStatsNoInversions(gp, counts = True)
	# #csvOperations.exportList(rnProgStats, "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/RnProgStats/noInversions", headers = ["rnProg", "count"])
	# print("total:", searchRnStats(rnProgStats, ('V4/3', 'I')))

	# cleanGP = getCleanVLDict(gp)
	# print("cleanGP got")
	# print("total len = ", len(cleanGP["maj"]) + len(cleanGP["min"]))
	# print("len(cleanGP['maj']):", len(cleanGP["maj"]))
	# print("len(cleanGP['min']):", len(cleanGP["min"]))

	# print("total rnProgs = ", countRnProgs(gp))



	# #vlList5and11clean = searchForIntervalStructure((5, 11), cleanGP)
	# # # pprint.pprint(vlList5and11clean)
	# # vlList = searchForIntervalStructure([5, 11], gp, rn1 = 'V7', inversions = False)
	# # print("len(vlList):", len(vlList))
	# # pprint.pprint(vlList)
	# # print()

	# # #pprint.pprint([(tup[0], tup[2]) for tup in vlList])

	# # resultMaj = searchForSpecificPcPaths(((5, -1), (11, 1)), vlList, rn1 = 'V7', rn2 = 'I', inversions = True, exclusion = True)
	# # # pprint.pprint([item[2] for item in resultMaj])
	# # print("len(resultMaj):", len(resultMaj))
	# # print()
	# # print()
	# # print()


	# # resultMaj2 = searchForSpecificPcPaths(((5, -1), (11, 1)), vlList, rn1 = 'V7', rn2 = 'I', inversions = True, exclusion = False)
	# # # pprint.pprint([item[2] for item in resultMaj2])
	# # print("len(resultMaj2):", len(resultMaj2))

	# # # pprint.pprint(resultMaj)
	# # print()
	# # print()
	# # print()

	# # resultMin = searchForSpecificPcPaths(((5, -2), (11, 1)), vlList, rn1 = 'V7', rn2 = 'i', inversions = True, exclusion = True)
	# # # pprint.pprint([item[2] for item in resultMin])
	# # print("len(resultMin):", len(resultMin))
	
	# # print()
	# # print()
	# # print()

	# # resultMin2 = searchForSpecificPcPaths(((5, -2), (11, 1)), vlList, rn1 = 'V7', rn2 = 'i', inversions = True, exclusion = False)
	# # # pprint.pprint([item[2] for item in resultMin2])
	# # print("len(resultMin2):", len(resultMin2))
	# # pprint.pprint(resultMin)
	# #pprint.pprint(result)

	# vlListClean = searchForIntervalStructure([(5)], cleanGP, rn1 = 'V7')
	# unconventionalSeventhsClean = searchForSpecificPcPaths([(5, 2)], vlListClean, rn1 = 'V7', rn2 = 'I', inversions = True, exclusion = False)
	# # showMeasures.showProgList(unconventionalSeventhsClean)

	# vlList = searchForIntervalStructure([(5)], gp, rn1 = 'V7')
	# unconventionalSevenths = searchForSpecificPcPaths([(5, 2)], vlList, rn1 = 'V7', rn2 = 'I', inversions = True, exclusion = False)
	# # showMeasures.showProgList(unconventionalSevenths)


	# rnFourToFiveAndSevenToFiveCount = 0
	# rnFourToThreeAndSevenToFiveCount = 0
	# rnFourToFiveAndSevenToOneCount = 0
	# other = 0

	# rnFourToFiveAndSevenToFiveCountMin = 0
	# rnFourToThreeAndSevenToFiveCountMin = 0
	# rnFourToFiveAndSevenToOneCountMin = 0
	# otherMin = 0


	# for line in resultMaj:
	# 	d = line[2]
	# 	if 2 in d[5]:
	# 		if 1 in d[11]:
	# 			rnFourToFiveAndSevenToOneCount += 1
	# 		elif -4 in d[11]:
	# 			rnFourToFiveAndSevenToFiveCount += 1
	# 		else:
	# 			other += 1
	# 	elif -4 in d[11]:
	# 		if -1 in d[5]:
	# 			rnFourToThreeAndSevenToFiveCount += 1
	# 		elif 2 in d[5]:
	# 			rnFourToFiveAndSevenToFiveCount += 1
	# 		else:
	# 			other += 1
	# 	else:
	# 		other += 1



	# for line in resultMin:
	# 	d = line[2]
	# 	if 2 in d[5]:
	# 		if 1 in d[11]:
	# 			rnFourToFiveAndSevenToOneCountMin += 1
	# 		elif -4 in d[11]:
	# 			rnFourToFiveAndSevenToFiveCountMin += 1
	# 		else:
	# 			otherMin += 1
	# 	elif -4 in d[11]:
	# 		if -2 in d[5]:
	# 			rnFourToThreeAndSevenToFiveCountMin += 1
	# 		elif 2 in d[5]:
	# 			rnFourToFiveAndSevenToFiveCountMin += 1
	# 		else:
	# 			otherMin += 1
	# 	else:
	# 		otherMin += 1


	# print("for MAJOR:")
	# print("rnFourToFiveAndSevenToFiveCount:", rnFourToFiveAndSevenToFiveCount)
	# print("rnFourToThreeAndSevenToFiveCount:", rnFourToThreeAndSevenToFiveCount)
	# print("rnFourToFiveAndSevenToOneCount:", rnFourToFiveAndSevenToOneCount)
	# print("other:", other)

	# print("for MINOR:")
	# print("rnFourToFiveAndSevenToFiveCountMin:", rnFourToFiveAndSevenToFiveCountMin)
	# print("rnFourToThreeAndSevenToFiveCountMin:", rnFourToThreeAndSevenToFiveCountMin)
	# print("rnFourToFiveAndSevenToOneCountMin:", rnFourToFiveAndSevenToOneCountMin)
	# print("otherMin:", otherMin)


	


	# # BELOW FIND CHORD INVERSION STATS GETTERS!!!!
	# rnP1 = rnPercentages(gp, "min", counts = False, rn = 'iv')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/iv_InvPercentages.csv"
	# csvOperations.exportList(rnP1, filename, headers = ["RN", "% Frequency"])

	# for i in range(0, 5):
	# 	print()
	# rnP2 = rnPercentages(gp, "min", counts = False, rn = 'viio')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/viio_InvPercentages.csv"
	# csvOperations.exportList(rnP2, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP3 = rnPercentages(gp, "min", counts = False, rn = 'i')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/i_InvPercentages.csv"
	# csvOperations.exportList(rnP3, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP4 = rnPercentages(gp, "min", counts = False, rn = 'V')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/V_InvPercentages.csv"
	# csvOperations.exportList(rnP4, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP5 = rnPercentages(gp, "min", counts = False, rn = 'V7')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/V7_InvPercentages.csv"
	# csvOperations.exportList(rnP5, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP6 = rnPercentages(gp, "min", counts = False, rn = 'iio')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/iio_InvPercentages.csv"
	# csvOperations.exportList(rnP6, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP7 = rnPercentages(gp, "min", counts = False, rn = 'viio7')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/min/viio7_InvPercentages.csv"
	# csvOperations.exportList(rnP7, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()
	# rnP8 = rnPercentages(gp, "maj", counts = False, rn = 'ii')
	# filename = "/Users/truszala/Documents/1JuniorSpring/JP/CSVs/InvPercentages/maj/ii_InvPercentages.csv"
	# csvOperations.exportList(rnP8, filename, headers = ["RN", "% Frequency"])
	# for i in range(0, 5):
	# 	print()



	# whereWillMyChordGoForAllChords(gp)

	# rnP = rnPercentagesNoInversions(gp, mode = "maj")
	# graphListOfKeyValTups(rnP, title = 'RN Frequencies (Without Inversions) in the Beethoven String Quartets (Major Keys)', numberOfVals = 20)

	# rnP2 = rnPercentagesNoInversions(gp, mode = "min")
	# graphListOfKeyValTups(rnP2, title = 'RN Frequencies (Without Inversions) in the Beethoven String Quartets (Minor Keys)', numberOfVals = 20)

	# rnP3 = rnPercentages(gp, mode = "maj")
	# graphListOfKeyValTups(rnP3, title = 'RN Frequencies in the Beethoven String Quartets (Major Keys)', numberOfVals = 20)

	# rnP4 = rnPercentages(gp, mode = "min")
	# graphListOfKeyValTups(rnP4, title = 'RN Frequencies in the Beethoven String Quartets (Minor Keys)', numberOfVals = 20)

	# rnStats1 = rnStatsNoInversions(gp, mode = "maj", sevenths = True)
	# graphListOfKeyValTups(rnStats1, title = "RN Prog Frequencies (Without Inversions) in the Beethoven String Quartets (Major Keys)", numberOfVals = 10)

	# rnStats2 = rnStatsNoInversions(gp, mode = "min", sevenths = True)
	# graphListOfKeyValTups(rnStats2, title = "RN Prog Frequencies (Without Inversions) in the Beethoven String Quartets (Minor Keys)", numberOfVals = 10)


	# rnPercentSubset = rnP[-30:-1]
	# chords = []
	# freqs = []
	# for i in range(0, len(rnPercentSubset)):
	# 	chords.append(rnPercentSubset[i][0])
	# 	freqs.append(rnPercentSubset[i][1])
	# plt.bar(chords, freqs)
	# plt.show()



	# countBigVLdegree(gp)
	# countVLdegree(gp)
	# majorScaleTritoneProgs = searchForIntervalStructure([5, 11], gp, mode = "maj")
	# fourthScaleDegreeMovesUp = searchForSpecificPcPaths([(5, 2)], majorScaleTritoneProgs)
	# pprint.pprint(fourthScaleDegreeMovesUp)


	# cleanVLs = getCleanVLs(gp)
	# pprint.pprint(cleanVLs)
	# print("len(cleanVLs):", len(cleanVLs))
	# showMeasures.showProgList(cleanVLs)



if __name__ == "__main__":
	main()




