from music21 import *
import sys
import re
import pickle
import os
import pprint
import voicing
import progs
import bigScore
from fractions import Fraction

# returns "true" if it is a key, otherwise returns 0
def isKey(chordsOrKey, c):
	keyFound = 0
	print("chordsOrKey =", chordsOrKey, "c =", c)
	reMatch = re.match('[a-g](b|#)?:', chordsOrKey[c], re.IGNORECASE)
	if reMatch:
		matchString = reMatch.group()
		length = len(matchString)
		keyFound = reMatch.group()[0:length-1]
		#print("keyFound", keyFound)
		
	return keyFound

def main2():

	# Filepaths
	mvtString = "op131_no14_mov2"
	progsStorage = mvtString + "_progs"
	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	_QUARTET = _MUSICPATH + mvtString

	progDict = progs.Progs()


	# Extracting the analysis information
	with open(_QUARTET + ".txt", 'r') as rnFile:

		for i in range(4):
			rnFile.readline()
		rnFile.read(16) # Gets us to the time-signature info, but this (probably doesn't) NEEDS DEBUGGING
		tsStr = rnFile.read(3)
		timeSignature = meter.TimeSignature(tsStr) #FIX: what happens when there's a time signature change within the movement?
		rnFile.readline()
		rnFile.readline()

		# Extracting the string parts
		movement = converter.parse(_QUARTET + ".mxl")
		mvt = bigScore.BigScore(movement, timeSignature)

		
		prevVoicing = None
		for line in rnFile:
			if line[0] == 'N': # i.e. "Note: ..."
				continue
			beatsChordsKeys = line.split()
			#print(beatsChordsKeys)
			mmStr = beatsChordsKeys[0]
			mNumb = mmStr[1:]
			#print("mNumb:", mNumb)
			# in case a measure doesn't actually exist.
			if mvt.violin1.measure(mNumb) is None:
				continue

			for i in range(1, len(beatsChordsKeys)):

				keyRE = re.compile('[a-g](b|#)?:', re.IGNORECASE)
				isKey = keyRE.match(beatsChordsKeys[i])
				if isKey:
					keyStr = isKey.group()
					currentKey = keyStr[0:-1]
					mvt.globalKey = key.Key(currentKey)

				beatRE = re.compile('b\\d.?\\d*')
				isBeat = beatRE.match(beatsChordsKeys[i])
				if isBeat:
					beatStr = isBeat.group()
					currentBeat = float(beatStr[1:len(beatStr)])
				testFlag = 1

				chordRE = re.compile("b?[(Ger)iIvV]+[bo\\+/(Ger)iIvV[0-9]*|  ", re.IGNORECASE)
				isChord = chordRE.match(beatsChordsKeys[i])
				if isChord:
					chordRN = isChord.group()
					if chordRN == "  ":
						chordRN = "No RN"
					currentVoicing = mvt.getVoicingAt(mNumb, currentBeat, chordRN)
					if prevVoicing == None: 
						prevVoicing = currentVoicing
						continue
					newVL = voicing.VL(prevVoicing, currentVoicing)
					progDict.addToProgs(newVL)
					print(mNumb, currentBeat, newVL.toString(), newVL.rnTuple())
					prevVoicing = currentVoicing


def main():
	genericIntervals = {3: [1], 9: [-1], 6: [-2], 11: [5]}
	c = chord.Chord()
	for pc in genericIntervals:
		c.add(pc)
	print(c.commonName)
	print(c.pitches)
	newPitches = pitch.simplifyMultipleEnharmonics(c.pitches)
	print(newPitches)
	newChord = chord.Chord(newPitches)
	print(newChord.commonName)

	chordRoot = c.root().pitchClass
	print(chordRoot)

	rn = roman.RomanNumeral('V7')
	rnRootInC = rn.root().pitchClass
	print(rnRootInC)
	transposeFactor = rnRootInC - chordRoot
	newGenericIntervals = {}
	for key in genericIntervals:
		newGenericIntervals[(key + transposeFactor) % 12] = genericIntervals[key]

	print(newGenericIntervals)







	print()
	print("simplifyingEnharmonics")
	test = chord.Chord(['C#', 'F', 'G#'])
	print(test.commonName)
	simpleTest = test.simplifyEnharmonics()
	print(simpleTest.pitches)
	print(simpleTest.commonName)

	cSharpMaj = chord.Chord(['C#', 'E#', 'G#'])
	print(cSharpMaj.commonName)


	progDict = progs.Progs()
	progDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op95_no11_mov4_progs")
	p = progDict.progs
	print("p loaded")
	pprint.pprint(p)









if __name__ == "__main__":
	main()
		


	




