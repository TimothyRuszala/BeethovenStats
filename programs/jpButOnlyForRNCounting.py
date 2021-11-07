from music21 import *
import sys
import re
import pickle
import os
import pprint
import voicing
import progs
import bigScore
import bigVoicing
import bigVL
import bigVLprogs
import getStats
import operator
from fractions import Fraction
import copy


def getProgs(filename, load = True):

#~~VARIABLES_AND_DICTIONARIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	mxlFile = filename + '.mxl'

	rnFrequencies = {"major" : {}, "minor" : {}}

#~~OPEN_FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Extracting the analysis information
	with open(filename + '.txt', 'r') as rnFile:
		for i in range(4):
			rnFile.readline()
		timeSignatureLine = rnFile.readline().split()
		#print(timeSignatureLine)
		timeSignature = meter.TimeSignature(timeSignatureLine[2]) #FIX: what happens when there's a time signature change within the movement?
		rnFile.readline()
		# Extracting the string parts
		movement = converter.parse(mxlFile)
		mvt = bigScore.BigScore(movement, timeSignature)


#~~LOAD_TOGGLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		if load: # Toggle: 1 if you wish to load Progs rather than run the program.
			progDict.loadProgs(progsStorage)
			bvlDict.loadProgs(bvlProgsStorage)
#~~GATHER_VL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# Gathers the voice-leadings.
		else: 			
			prevVoicing = None
			prevPrevVoicing = None
			prevBigVoicing = None

#~~PARSE_BY_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			for line in rnFile:
				print(line[0:])
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
						continue
#~~CHECK_RN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
					chordRE = re.compile("((Ger|It|Fr|N|b?[iIvV]+o?[+]?)+(b?#?o?[0-9]?/?)*)+|  ")
					isChord = chordRE.match(beatsChordsKeys[i])
					if isChord:
						chordRN = isChord.group()
						if chordRN == "  ":
							chordRN = "No RN"
						addRNtoProg(mvt, rnFrequencies, chordRN)
		return rnFrequencies

						
#~~ADD_VL_TO_PROGS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						

#~~FURTHER_OPERATIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	return rnFrequencies

def addRNtoProg(mvt, rnFrequencies, chordRN):
	mode = mvt.globalKey.mode
	if mode == 'major':
		if chordRN in rnFrequencies[mode]:
			rnFrequencies[mode][chordRN] += 1
		else:
			rnFrequencies[mode][chordRN] = 1
	elif mode == "minor":
		if chordRN in rnFrequencies[mode]:
			rnFrequencies[mode][chordRN] = rnFrequencies[mode][chordRN] + 1
			print("hooot")
		else:
			rnFrequencies[mode][chordRN] = 1

def rnProgsSortedPercentages(rnFrequencies, mode = "major"):
	newRnFreq = []
	for key in rnFrequencies[mode]:
		newRnFreq.append((key, rnFrequencies[mode][key]))
	return sorted(newRnFreq, key=operator.itemgetter(1))


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

	for file in fileList:
		print(file)
		try:
			getProgs(file, load = False)
		except:
			print(file + "did not work for some reason.")
			continue

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
		mvt = bigScore.BigScore(movement, timeSignature)

	return mvt


# MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
def main():

	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	mvtString = "op18_no1_mov4"
	filename = _MUSICPATH + mvtString
	print (filename)

	mvt = load(filename)
	rnFrequencies = getProgs(filename, load = False)
	pprint.pprint(rnProgsSortedPercentages(rnFrequencies, mode = "major"))

	
	print('fin.')

		

if __name__ == "__main__":
	main()


	