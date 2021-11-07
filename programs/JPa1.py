from music21 import *
import sys
import re
import pickle
import os
import pprint
import pathlib
import voicing
import progs
import bigScore
import bigVoicing
import bigVL
import bigVLprogs
import getStats
import tabulate
from fractions import Fraction
import copy


def getProgs(filename, load = True):

#~~VARIABLES_AND_DICTIONARIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	mxlFile = filename + '.mxl'
	print(mxlFile)

	progDict = progs.Progs()
	progsStorage = filename + "_progs"

	giantProgDict = progs.Progs()
	giantProgDictStorageMay13a = "/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay13a"
	# try:
	# 	giantProgDict.loadProgs(giantProgDictStorageMay13a)
	# 	print("giantProgDict loaded")
	# except:
	# 	print("couldn't load gpdsMay13a")

	# bvlProgsStorage = filename + "_bigVLprogs"
	# bvlDict = bigVLprogs.BigVLprogs()

	rnFrequencies = {"major" : {}, "minor" : {}}

#~~OPEN_FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Extracting the analysis information
	with open(filename + '.txt', 'r') as rnFile:
		for i in range(4):
			rnFile.readline()
		timeSignatureLine = rnFile.readline().split()
		print(timeSignatureLine)
		timeSignature = meter.TimeSignature(timeSignatureLine[2]) #FIX: what happens when there's a time signature change within the movement?
		rnFile.readline()
		# Extracting the string parts
		try:
			movement = converter.parse(mxlFile)
		except:
			print(filename + " could not be opened")
			return
		mvt = bigScore.BigScore(movement, timeSignature, mxlFile = mxlFile)
		print(mvt.mvtString)



#~~LOAD_TOGGLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		if load: # Toggle: 1 if you wish to load Progs rather than run the program.
			progDict.loadProgs(progsStorage)
			#bvlDict.loadProgs(bvlProgsStorage)
#~~GATHER_VL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# Gathers the voice-leadings.
		else: 			
			prevVoicing = None
			prevPrevVoicing = None
			prevBigVoicing = None

#~~PARSE_BY_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			for line in rnFile:
				#print(line[0:])
				if line[0] == 'N': # i.e. "Note: ..."
					continue
				if line[0] == '\n' or line[0] == ' ':
					continue
				beatsChordsKeys = line.split()
				if beatsChordsKeys[0][0] == 'T': #i.e. "Time Signature: 4/4"
					timeSignature = meter.TimeSignature(beatsChordsKeys[-1])
					continue
				mmStr = beatsChordsKeys[0]
				mNumb = int(mmStr[1:])
				print(mNumb)
				# in case a measure doesn't actually exist.
				if mvt.violin1.measure(mNumb) is None:
					continue
				currentBeat = None

#~~PARSE_THROUGH_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				for i in range(1, len(beatsChordsKeys)):
#~~CHECK_KEY~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
					keyRE = re.compile('[a-g](b|#)?:', re.IGNORECASE)
					isKey = keyRE.match(beatsChordsKeys[i])
					if isKey:
						keyStr = isKey.group()
						currentKey = keyStr[0:-1]
						mvt.globalKey = key.Key(currentKey)
						print("~~~~~~~~~~~~~~~~~~~~~~~", mvt.globalKey)
						continue
#~~CHECK_BEAT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
					# Checks if BEAT
					beatRE = re.compile('b\\d.?\\d*')
					isBeat = beatRE.match(beatsChordsKeys[i])
					if isBeat:
						beatFlag = 0
						beatStr = isBeat.group()
						currentBeat = float(beatStr[1:len(beatStr)])
						currentBeat = Fraction(currentBeat).limit_denominator(20)
						continue
#~~CHECK_RN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
					chordRE = re.compile("((Ger|It|Fr|N|b?[iIvV]+o?[+]?)+(b?#?o?[0-9]?/?)*)+|  ")
					isChord = chordRE.match(beatsChordsKeys[i])
					if isChord:
						chordRN = isChord.group()
						addRNtoProg(mvt, rnFrequencies, chordRN)
						if chordRN == "  ":
							chordRN = "No RN"
						if currentBeat == None:
							currentBeat = 1.0
						currentVoicing = mvt.getVoicingAt(mNumb, currentBeat, chordRN)
						if currentVoicing == None: # i.e. we are at the last measure (so last measure not included)
							break
						if prevVoicing == None: 
							prevVoicing = currentVoicing
							continue
						if chordRN == prevVoicing.rn:
							continue
						else:
							mvt.update(prevVoicing, mNumb, currentBeat)
							currentBigVoicing = bigVoicing.BigVoicing(mvt, prevVoicing.rn, prevVoicing.mNumb, prevVoicing.beat, mNumb, currentBeat)
						if prevPrevVoicing == None:
							prevPrevVoicing = prevVoicing
							prevVoicing = currentVoicing
							prevBigVoicing = currentBigVoicing
							continue
#~~ADD_VL_TO_PROGS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						newVL = voicing.VL(prevPrevVoicing, prevVoicing, mvt)
						#print("Generic Intervals:", newVL.getGenericIntervals())
						newBVL = bigVL.BigVL(prevBigVoicing, currentBigVoicing)

						#print(newVL.v1.mNumb, newVL.v1.beat, "->", newVL.v2.mNumb, newVL.v2.beat, newVL.rnTuple(), newVL.toString(), newVL.toTransposedTupleTuple(), newVL.getGenericIntervals())
						#print()
						#print("^^^", newBVL.rnTuple(), newBVL.toString())
						progDict.addToProgs(newVL, newBVL)
						#giantProgDict.addToProgs(newVL, newBVL)


						prevPrevVoicing = prevVoicing
						prevVoicing = currentVoicing
						prevBigVoicing = currentBigVoicing


						# else:
						# 	bvlDict.addToProgs(newBVL)
						# 	prevBigVoicing = currentBigVoicing

#~~FURTHER_OPERATIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		
			giantProgDict.combineProgs(progDict.progs)
			progDict.dumpProgs(progsStorage)
			giantProgDict.dumpProgs(giantProgDictStorageMay13a)

	pprint.pprint(progDict.progs)
	return progDict.progs

def addRNtoProg(mvt, rnFrequencies, chordRN):
	mode = mvt.globalKey.mode
	if mode == 'major':
		if chordRN in rnFrequencies:
			rnFrequencies[mode][chordRN] += 1
		else:
			rnFrequencies[mode][chordRN] = 1
	elif mode == "minor":
		if chordRN in rnFrequencies:
			rnFrequencies[mode][chordRN] += 1
		else:
			rnFrequencies[mode][chordRN] = 1

def getListOfQuartetFilesWithoutExtensions():
	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'

	unfilteredFilelist = os.listdir(_MUSICPATH)
	fileList = []
	for file in unfilteredFilelist:
		if file[-1] == 't': #i.e. '.txt'
			fileList.append(_MUSICPATH + file[0:-4])

	return fileList

def getAllProgs():

	fileList = getListOfQuartetFilesWithoutExtensions()

	for file in reversed(fileList):
		print(file)
		# try:
		getProgs(file, load = False)
		# except:
		# 	print(file + "did not work for some reason.")
		# 	continue

# sets up a movement
def load(fullFilename):

	with open(fullFilename + '.txt', 'r') as rnFile:
		for i in range(4):
			rnFile.readline()
		timeSignatureLine = rnFile.readline().split()
		timeSignature = meter.TimeSignature(timeSignatureLine[2])
		rnFile.readline()
		# Extracting the string parts
		movement = converter.parse(fullFilename + '.mxl')
		mvt = bigScore.BigScore(movement, timeSignature, mxlFile = fullFilename)

	return mvt

def searchBigVLs(filename, mvt, degree = (4, 4), noNonChordTones = "Yes", oneVoiceForEachPart = "Yes"):
	bvlDict = bigVLprogs.BigVLprogs()
	bvlProgsStorage = filename + "_bigVLprogs"
	bvlDict.loadProgs(bvlProgsStorage)

	bvlsAndTups = bvlDict.searchForSimpleBigVLs(mvt)

	pprint.pprint(bvlsAndTups[1])
	bvlsAndTups[0].show()




# MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
def main():

	#getAllProgs()

	# _MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	# _MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	# mvtString = "op18_no3_mov1"
	# filename = _MUSICPATH + mvtString
	# print(filename)

	# testProgs = getProgs(filename, load = False)

	print('started')
	getProgs(str(pathlib.Path(__file__).parents[1]) + "/Music/Beethoven Quartets/op130_no13_mov1", load = False)




	# mvt = load(filename)
	# progDict = getProgs(filename, load = False)
	# progDict = getProgs(filename, load = True)
	# # pprint.pprint(progDict)
	# getStats.rnPercentages(progDict, "maj", counts = True)
	# getStats.rnPercentagesNoInversions(progDict, "maj", counts = False, sevenths = False)


	



	# giantProgDict = progs.Progs()
	# giantProgDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorage")
	# gp = giantProgDict.progs
	# print("gp loaded")


	# calculations

	# pprint.pprint(gp)
	# print("getStats.rnStats(gp)")
	# getStats.rnStats(gp)
	# for i in range(0, 20):
	# 	print()
	# print("getStats.rnStats(gp)")

	# print("getStats.rnStatsNoInversions(gp, sevenths = False)")
	# getStats.rnStatsNoInversions(gp, sevenths = False)
	# for i in range(0, 20):
	# 	print()
	# print("getStats.rnStatsNoInversions(gp, sevenths = False)")


	# print("getStats.rnPercentages(gp, 'maj', counts = True)")
	# rnPercentagesMaj = getStats.rnPercentages(gp, "maj", counts = True)
	# print("getStats.rnPercentages(gp, 'maj', counts = True)")

	# for i in range(0, 20):
	# 	print()

	# print("getStats.rnPercentagesNoInversions(gp, 'maj', counts = False, sevenths = True)")
	# getStats.rnPercentagesNoInversions(gp, "maj", counts = False, sevenths = False)
	# print("getStats.rnPercentagesNoInversions(gp, 'maj', counts = False, sevenths = True)")

	# for i in range(0, 20):
	# 	print()

	# print("getStats.whereWillMyChordGo('IV', gp, maj, counts = False):")
	# getStats.whereWillMyChordGo('IV', gp, 'maj', counts = False)
	# print("getStats.whereWillMyChordGo('IV', gp, maj, counts = False):")

	# print("getStats.whereWillMyChordGo('V', gp, maj, counts = False):")
	# getStats.whereWillMyChordGo('V', gp, 'maj', counts = False)
	# print("getStats.whereWillMyChordGo('V', gp, maj, counts = False):")

	# print("getStats.whereWillMyChordGo('bVI', gp, min, counts = False):")
	# getStats.whereWillMyChordGo('bVI', gp, 'min', counts = False)
	# print("getStats.whereWillMyChordGo('bVI', gp, min, counts = False):")

	# for tup in rnPercentagesMaj:
	# 	rn = tup[0]
	# 	getStats.whereWillMyChordGo(rn, gp, 'maj', counts = False)


	# MINOR calculations
	# print("getStats.rnStats(gp)")
	# getStats.rnStats(gp, mode = "min")
	# print("getStats.rnStats(gp)")

	# for i in range(0, 20):
	# 	print()
	
	# print("getStats.rnStatsNoInversions(gp, mode = 'min' sevenths = False)")
	# getStats.rnStatsNoInversions(gp, mode = "min", sevenths = False)
	# print("getStats.rnStatsNoInversions(gp, mode = 'min', sevenths = False)")

	# for i in range(0, 20):
	# 	print()

	# print("getStats.rnPercentages(gp, 'min', counts = True)")
	# getStats.rnPercentages(gp, "min", counts = True)
	# print("getStats.rnPercentages(gp, 'min', counts = True)")

	# for i in range(0, 20):
	# 	print()

	# print("getStats.rnPercentagesNoInversions(gp, 'min', counts = False, sevenths = True)")
	# getStats.rnPercentagesNoInversions(gp, "min", counts = False, sevenths = True)
	# print("getStats.rnPercentagesNoInversions(gp, 'min', counts = False, sevenths = True)")

	
	print('fin.')

		

if __name__ == "__main__":
	main()


	




