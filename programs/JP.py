from music21 import *
import sys
import re
import pickle
import os
import pprint
from fractions import Fraction

# Filepaths
mvtString = "op18_no1_mov2"
_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
_QUARTET = _MUSICPATH + mvtString

# list divides between major and minor modalities, dictionaries nest specific voicings within chord progressions
locations = {"maj" : {}, "min" : {}}
progs = {"maj" : {}, "min" : {}} # e.g.: progs["maj"][rnProgs][spec vls : freq]
progsDeluxe = {"maj" : {}, "min" : {}} #e.g.: progs["maj"][rnProgs][vl.toTupleTuple() : (freq, vl)]
rntxt = "" # holds the romanText file
progsStorage = mvtString + "_progs"
movement = stream.Score
timeSignature = meter.TimeSignature
globalKey = key.Key
violin1 = stream.Part
violin2 = stream.Part
viola = stream.Part
cello = stream.Part

class Voicing():
	""" Voicing object to contain a given chordal verticality """
	# This program I think mostly inputs as notes. Might possibly want to do pitches. ¡Also accepts chords!.
	def __init__(self, cello = None, viola = None, violin2 = None, violin1 = None, rn = None, mNumb = None, beat = None, celloClef = None):
		
		if celloClef is not None and celloClef.name is 'treble': #Probably won't work if clef changes in middle of the bar...
			cello.pitch.transpose('-P8')
		self.cello = cello
		self.viola = viola
		self.violin2 = violin2
		self.violin1 = violin1
		self.pitches = [cello, viola, violin2, violin1]

		self.rn = rn # this is the roman numeral associated with this voicing
		self.mNumb = mNumb
		self.beat = beat

	# transposes the voicing to C for the sake of VL's toString()
	def transposeToC(self):
		global globalKey
		root = globalKey.tonic
		pc = root.pitchClass
		i = 12 - pc #interval to transpose by to get to key of C
		transposedPitches = []
		for n in self.pitches:
			if isinstance(n, note.Note):
				transposedPitches.append(n.transpose(i))
			elif isinstance(n, chord.Chord):
				tempList = []
				for p in n.pitches:
					tempList.append(p.transpose(i))
				transposedChord = chord.Chord(tempList)
				transposedPitches.append(transposedChord)
			else: 
				transposedPitches.append(None)
		v = Voicing(transposedPitches[0], transposedPitches[1], transposedPitches[2], transposedPitches[3])
		return v

	# in original key
	def toString(self):
		pitchesForPrinting = []
		for n in self.pitches:
			if isinstance(n, note.Note):
				pitchesForPrinting.append(n.name)
			elif isinstance(n, chord.Chord):
				tempList = []
				for p in n.pitches:
					tempList.append(p.name)
				printTuple = tuple(tempList)
				pitchesForPrinting.append(printTuple)
			else:
				pitchesForPrinting.append('rest')
		return str(pitchesForPrinting)

	def toTuple(self):
		pitchesForPrinting = []
		for n in self.pitches:
			if isinstance(n, note.Note):
				pitchesForPrinting.append(n.name)
			elif isinstance(n, chord.Chord):
				tempList = []
				for p in n.pitches:
					tempList.append(p.name)
				printTuple = tuple(tempList)
				pitchesForPrinting.append(printTuple)
			else:
				pitchesForPrinting.append('rest')
		return tuple(pitchesForPrinting)

	def location(self):
		return (mNumb, beat)

class VL():
	""" Voice-Leading object to contain motion between two Voicings """
	def __init__(self, voicing1, voicing2):
		self.v1 = voicing1
		self.v2 = voicing2
		self.intervals = []

		v1Instruments = [voicing1.cello, voicing1.viola, voicing1.violin2, voicing1.violin1]
		v2Instruments = [voicing2.cello, voicing2.viola, voicing2.violin2, voicing2.violin1]

		#Ok, so this whole segment definitely has 1000 bugs. Test.
		for i in v1Instruments:
			for j in v2Instruments:
				if isinstance(i, note.Note) and isinstance(j, note.Note):
					self.intervals.append(interval.notesToChromatic(i, j).semitones)
				elif isinstance(i, chord.Chord) and isinstance(j, chord.Chord):
					pitchIntList = []
					if len(i.pitches) is len(j.pitches):
						for q in range(0, len(i.pitches)):
							pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]))
						self.intervals.append(tuple(pitchIntList))
					else: # In the case of chords of different pitches, simply ignores some notes.
						lo = max(len(i.pitches), len(j.pitches))
						pitchIntList = []
						for q in range(0, lo):
							pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]))
						self.intervals.append(tuple(pitchIntList))
				elif isinstance(i, note.Note) and isinstance(j, chord.Chord):
					pitchIntList = []
					for q in range(0, len(j.pitches)):
						pitchIntList.append(interval.notesToChromatic(i, j.pitches[q]))
					self.intervals.append(tuple(pitchIntList))
				elif isinstance(i, chord.Chord) and isinstance(j, note.Note):
					pitchIntList = []
					for q in range(0, len(i.pitches)):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j))
					self.intervals.append(tuple(pitchIntList))
				else:
					self.intervals.append(999)
		#self.intervals.sort() 				FOR NOW THERE IS NO SORTING. THIS WILL NEED TO BE FIXED.
		self.intervals = tuple(self.intervals)

	def rnTuple(self):
		return (self.v1.rn, self.v2.rn)

	def toString(self):
		return self.v1.toString() + " -> " + self.v2.toString()

	def toStringTransposed(self):
		return self.v1.transposeToC().toString() + " -> " + self.v2.transposeToC().toString() #+ "intervals: " + intervals

	def intervalTuple(self):
		return self.intervals

	def toTupleTuple(self):
		return (self.v1.toTuple(), self.v2.toTuple())

	def toTransposedTupleTuple(self):
		return (self.v1.transposeToC().toTuple(), self.v2.transposeToC().toTuple())

# I will definitely have problems here with .67 divisions of the beat, which are greater than 2/3
def getNoteOrRestAtBeat(part, measure, beat, rn = None):
	global globalKey

	excerpt = part.measure(measure)
	beatCap = beat
	noteOrRest = None
	prevElement = None
	romanN = roman.RomanNumeral()
	if rn is None:
		for n in excerpt.notesAndRests:
			if n.beat > beatCap:
					break
			prevElement = n
	else:
		romanN = roman.RomanNumeral(rn, globalKey)
		for n in excerpt.notesAndRests:
			#print("n=", n, n.beat)
			if n.beat > beatCap:
				if isinstance(n, note.Rest):
					break
				elif isinstance(n, note.Note) and (n.pitch.pitchClass in romanN.pitchClasses):
					break
				elif isinstance(n, chord.Chord) and (n.pitchClasses in romanN.pitchClasses):
					break
			prevElement = n
	#print ("beatCap =", beatCap, "beat =", prevElement.beat, "note =", prevElement)
	return prevElement # this gives us the element not greater than beatCap, i.e. the element at or before beatCap

# extracts all the parts of the movement into its individual instruments
def extractParts():
	global movement, violin1, violin2, viola, cello

	violin1  = movement.parts[0]
	violin2  = movement.parts[1]
	viola    = movement.parts[2]
	cello    = movement.parts[3]

# finds the first voicing
def firstVoicing():
	global violin1, violin2, viola, cello

	v1Note = violin1.getElementsByClass(stream.Measure)[0].notesAndRests[0]
	v2Note = violin2.getElementsByClass(stream.Measure)[0].notesAndRests[0]
	violNote = viola.getElementsByClass(stream.Measure)[0].notesAndRests[0]
	cNote    = cello.getElementsByClass(stream.Measure)[0].notesAndRests[0]
	firstVoicing = Voicing(cNote, violNote, v2Note, v1Note)
	#print(firstVoicing.toString())
	return firstVoicing

# doesn't quite work yet, but might come in handy
def resetPrevVoicing(measure, beat): 
	global violin1, violin2, viola, cello

	if beat == 1:
		measure = measure - 1
		beat = timeSignature.beatCount + .99 # FIND WHAT THIS ACTUALLY IS. +.99 is so that we have the last possible offest in the measure.
		print(beat)
		v1Note = getNoteOrRestAt(violin1, measure, beat)
		v2Note = getNoteOrRestAt(violin2, measure, beat) 
		violNote = getNoteOrRestAt(viola, measure, beat)
		celNote  = getNoteOrRestAt(cello, measure, beat)
		newVoicing = Voicing(celNote, violNote, v2Note, v1Note)

	# -.01 ensures we get the previous note/rest.	
	else:
		v1Note = getNoteOrRestAt(violin1, measure, beat - 0.01)
		v2Note = getNoteOrRestAt(violin2, measure, beat - 0.01) 
		violNote = getNoteOrRestAt(viola, measure, beat - 0.01)
		celNote  = getNoteOrRestAt(cello, measure, beat - 0.01)
		newVoicing = Voicing(celNote, violNote, v2Note, v1Note)

	return newVoicing

# just like addToProgs, but also stores the vl object itself
def addToProgsDeluxe(newVL):
 	if globalKey.mode is 'major':
 		rnProg = newVL.rnTuple() 
 		transposedTupleTuple = newVL.toTransposedTupleTuple()
 		if rnProg not in progs["maj"]:
 			progs["maj"][rnProg] = {transposedTupleTuple : [1, newVL]}
 		else:
 			if transposedTupleTuple not in progs["maj"][rnProg]:
 				progs["maj"][rnProg][transposedTupleTuple] = [1, newVL]
 			else:
 				progs["maj"][rnProg][transposedTupleTuple][0] += 1
 		
 	else:
 		rnProg = newVL.rnTuple()
 		transposedTupleTuple = newVL.toTransposedTupleTuple()
 		if rnProg not in progs["min"]:
 			progs["min"][rnProg] = {transposedTupleTuple : [1, [newVL]]}
 		else:
 			if transposedTupleTuple not in progs["min"][rnProg]:
 				progs["min"][rnProg][transposedTupleTuple] = [1, [newVL]]
 			else:
 				progs["min"][rnProg][transposedTupleTuple][0] += 1
 				progs["min"][rnProg][transposedTupleTuple][1].append(newVL)

def is_non_zero_file(fpath):
	return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

# extracts measure number from a line of rntext
def getMeasureNumber(line):
	mmRE = re.compile('[0-9]*')
	m = mmRE.match(line, 1) #Gets the measure number in form "mxxx"
	mNumb = int(m.group()) # measure number
	return mNumb

def extractBeatInfo(line):
	#This RE makes a list of relevant beats in the rntext. Fine for now.
	isBeat = re.compile('b\\d.?\\d*')
	beats = isBeat.findall(line)
	for i in range(0, len(beats)):
		beats[i] = float(beats[i][1:len(beats[i])]) # removes 'b' from e.g. 'b1.33'
		beats[i] = Fraction(beats[i]).limit_denominator(20)
	beats.insert(0, 1) #inserts beat 1
	return beats

# returns "true" if it is a key, otherwise returns 0
def isKey(chordsOrKey, c):
	keyVerdict = 0
	if re.match('[a-g]:', chordsOrKey[c], re.IGNORECASE):
		keyVerdict = "true"
	return keyVerdict

def getVoicingAt(mNumb, beat, rn):
	global cello

	cel  = getNoteOrRestAtBeat(cello, mNumb, beat)
	viol = getNoteOrRestAtBeat(viola, mNumb, beat)
	v2   = getNoteOrRestAtBeat(violin2, mNumb, beat)
	v1   = getNoteOrRestAtBeat(violin1, mNumb, beat)
	celloClef = cello.measure(mNumb).clef
	voi = Voicing(cel, viol, v2, v1, rn, celloClef)
	return voi

# rnProg is a two-element tuple. E.g.: ('i', 'V')
# if inversions is any value, will also return all inversion of these chords
# returns a dictionary
def searchForRnProg(rnProg, inversions = None):
	
	romanNumeral0 = roman.RomanNumeral(rnProg[0])
	rn0 = romanNumeral0.romanNumeral
	romanNumeral1 = roman.RomanNumeral(rnProg[1])
	rn1 = romanNumeral1.romanNumeral

	inversionListTriads = ('', '6', '6/4') 
	inversionListSevenths = ('7', '6/5', '4/3', '4/2')
	allRelevantProgs = []
	if inversions is None:
		if rnProg in progs["maj"]:
			allRelevantProgs.append(progs["maj"][rnProg])
			#print(allRelevantProgs)
		if rnProg in progs["min"]:
			allRelevantProgs.append(progs["min"][rnProg])
			#print(allRelevantProgs)

	else: # counting inversions. Needs to take into account 9th chords, since they're there.
		if romanNumeral0.isTriad():
			for i in inversionListTriads:
				if romanNumeral1.isTriad():
					for j in inversionListTriads:
						rnCheck = (rn0 + i, rn1 + j)
						if rnCheck in progs["maj"]:
							allRelevantProgs.append(progs["maj"][rnCheck])
						if rnCheck in progs["min"]:
							allRelevantProgs.append(progs["min"][rnCheck])
				elif romanNumeral1.isSeventh():
					for j in inversionListSevenths:
						rnCheck = (rn0 + i, rn1 + j)
						if rnCheck in progs["maj"]:
							allRelevantProgs.append(progs["maj"][rnCheck])
						if rnCheck in progs["min"]:
							allRelevantProgs.append(progs["min"][rnCheck])

		elif romanNumeral0.isSeventh():
			for i in inversionListSevenths:
				if romanNumeral1.isTriad():
					for j in inversionListTriads:
						rnCheck = (rn0 + i, rn1 + j)
						if rnCheck in progs["maj"]:
							allRelevantProgs.append(progs["maj"][rnCheck])
						if rnCheck in progs["min"]:
							allRelevantProgs.append(progs["min"][rnCheck])
				elif romanNumeral1.isSeventh():
					for j in inversionListSevenths:
						rnCheck = (rn0 + i, rn1 + j)
						if rnCheck in progs["maj"]:
							allRelevantProgs.append(progs["maj"][rnCheck])
						if rnCheck in progs["min"]:
							allRelevantProgs.append(progs["min"][rnCheck])
	return allRelevantProgs

# just handles the first line of the program so we don't record rnProg (None, 'i').
# Slightly adjusted from the main loop, to avoid too many unecessary if statements.
# returns prevVoicing for the rest of the lines
# def handleFirstLine(line):
# 	beats = extractBeatInfo(line) # beats is a list of floats
# 	chordsOrKey = extractChordAndKeyInfo(line)
# 	prevVoicing = firstVoicing() # REMOVE (possibly)

# 	c = 0 # i is counter for beats[], c is counter for chordsOrKey[]
# 	for i in range(1, len(beats)):
# 		# Checks if we have key, and if so we set key to this.
# 		if isKey(chordsOrKey, c):
# 			globalKey = key.Key(chordsOrKey[c][0])
# 			c += 1
# 		chord = chordsOrKey[c]
		
# 		currentVoicing = getVoicingAt(1, beats[i], chord) # May need to fix re: pickup measures
# 		newVL = VL(prevVoicing, currentVoicing)
# 		addToProgsDeluxe(newVL)
# 		prevVoicing = currentVoicing # This will need to be adjusted
# 	return prevVoicing

def extractChordAndKeyInfo(line):
	# This RE finds makes a list of the chords in each line.
	# !!!! NOTE: I HAVE NO IDEA WHAT || IN THE CHORDS MEANS. NOT INCLUDED HERE.

	isChordOrKey = re.compile("[a-g]:|b?[(Ger)iIvV]+[o\\+/(Ger)iIvV[0-9]*", re.IGNORECASE)
	chordsOrKey = isChordOrKey.findall(line)

	return chordsOrKey




# MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



# Extracting the string parts
movement = converter.parse(_QUARTET + ".mxl")
extractParts()

# Extracting the analysis information
with open(_QUARTET + ".txt", 'r') as rnFile:
	for i in range(4):
		rnFile.readline()
	rnFile.read(16) # Gets us to the time-signature info, but this (probably doesn't) NEEDS DEBUGGING
	tsStr = rnFile.read(3)
	timeSignature = meter.TimeSignature(tsStr) #FIX: what happens when there's a time signature change within the movement?
	rnFile.readline()
	rnFile.readline()

	if is_non_zero_file(progsStorage) and 0:
		with open(progsStorage, 'rb') as infile:
			progs = pickle.load(infile)

	elif 1: # temporary on / off switch
		prevVoicing = firstVoicing()
		for line in rnFile:
			mNumb = getMeasureNumber(line)
			beats = extractBeatInfo(line) # beats is a list of floats
			chordsOrKey = extractChordAndKeyInfo(line)

			# Below I exctract the voicings and voice-leadings in the line.
			
			c = 0 # i is counter for beats[], c is counter for chordsOrKey[]
			for i in range(0, len(beats)):
				# Checks if we have key, and if so we set key to this.
				if isKey(chordsOrKey, c):
					globalKey = key.Key(chordsOrKey[c][0])
					c += 1
				rn = chordsOrKey[c]
				currentVoicing = getVoicingAt(mNumb, beats[i], rn) 
				newVL = VL(prevVoicing, currentVoicing)
				print(mNumb, beats[i], newVL.toString(), newVL.rnTuple())
				print(newVL.intervalTuple())
				getNoteOrRestAtBeat(violin1, mNumb, beats[i])
				if mNumb is not 1 and beats[i] is not 1: # maybe eventually restructure this, since it only deals with one time, to avoid first vl.
					addToProgsDeluxe(newVL)
				prevVoicing = currentVoicing # This will need to be adjusted
				c += 1

		# Dumps if not pickle.load()
		with open(progsStorage, 'wb') as outfile:
			pickle.dump(progs, outfile)


	

# print("maj =", len(progsInt["maj"]), "min =", len(progsInt["min"]))

# for x in progs["maj"].items():
# 	print(x, '\n')

# pprint.pprint(progs)


#TESTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# testDict = searchForRnProg(('i', 'V7'), "checkInversions")
# print("start")
# for x in testDict:
# 	pprint.pprint(x)
# print("done")



