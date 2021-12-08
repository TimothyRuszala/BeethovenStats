from music21 import *
import bigScore
import bigVL
import getProgs
import partVoiceCountList
from fractions import Fraction

# The BigVoicing object is like a regular voicing, but collects all chord
# tones within the space of a single harmony into one giant chord. Useful
# for looking at implied voice leadings.
class BigVoicing():
	def __init__(self, mvt, rn, mNumbStart, beatStart, mNumbEnd, beatEnd):
		excerpt = mvt.excerpt(mNumbStart, mNumbEnd)
		self.rn = rn
		self.bv = chord.Chord()
		self.bvListOfPitches = []

		self.globalKey = mvt.globalKey

		self.mNumbStart = mNumbStart
		self.beatStart = beatStart
		self.location = (mNumbStart, beatStart)
		self.nonChordTones = 0

		romanN = roman.RomanNumeral(self.rn, self.globalKey)
		for p in excerpt.parts:
			intermittentNoteFlag = 0 # used to help figure out if we're dealing with a held note
			possibleHeldNote = 0
			for n in p.recurse().notes:
				if n.beat >= beatStart or n.measureNumber > mNumbStart:
					if mvt.hasPickup():
						if (n.measureNumber == mNumbEnd - 1) and (n.beat >= beatEnd):
							break
					elif (n.measureNumber == mNumbEnd) and (n.beat >= beatEnd):
						break
					else:
						if isinstance(n, note.Note):
							intermittentNoteFlag = 1
							if n.pitch.pitchClass in romanN.pitchClasses:
								pitchNamesWithOctaves = [x.nameWithOctave for x in self.bv.pitches]
								pitchInQuestion = n.pitch.nameWithOctave
								if pitchInQuestion not in pitchNamesWithOctaves:
									n.pitch.groups.append(p.id)	
									self.bv.add(n.pitch)
								else:
									index = pitchNamesWithOctaves.index(pitchInQuestion)
									if p.id not in self.bv.pitches[index].groups:
										self.bv.pitches[index].groups.append(p.id)
							else:
								self.nonChordTones += 1
						elif isinstance(n, chord.Chord):
							intermittentNoteFlag = 1
							for ptch in n.pitches:
								if ptch.pitchClass in romanN.pitchClasses:
									if ptch not in [x.nameWithOctave for x in self.bv.pitches]:
										ptch.groups.append(p.id)
										self.bv.add(ptch)
								else:
									self.nonChordTones += 1
				else:
					possibleHeldNote = n
			# This one checks in case there is a held note
			if intermittentNoteFlag == 0:
				if isinstance(possibleHeldNote, note.Note):
					if possibleHeldNote.pitch.pitchClass in romanN.pitchClasses:
						if possibleHeldNote.pitch not in self.bv.pitches:
							possibleHeldNote.pitch.groups.append(p.id)
							self.bv.add(possibleHeldNote.pitch)
				# rare case of a held chord.
				elif isinstance(possibleHeldNote, chord.Chord):
					for ptch in possibleHeldNote.pitches:
						if ptch.pitchClass in romanN.pitchClasses:
							if ptch not in self.bv.pitches:
								ptch.groups.append(p.id)
								self.bv.add(ptch)


		self.partVoiceCountList = self.voicePerPartCounter()
		self.degree = len(self.bv.pitches)


	# Checks whether all instruments have exactly one voice. Works with 2-4 voices.
	def hasOneVoiceToEachPart(self, numberOfParts = 4):

		instrumentCounter = 0
		for key in self.partVoiceCountList:
			if self.partVoiceCountList[key] == 0:
				continue
			elif self.partVoiceCountList[key] == 1:
				instrumentCounter = instrumentCounter + 1
			else:
				return False
		if instrumentCounter != numberOfParts:
			return False
		else:
			return True

	# delivers list like this: {'Cello': 1, 'Viola': 1, 'Violin II': 3, 'Violin I': 2}
	def voicePerPartCounter(self):
		partCheckList = {'Cello': 0, 'Viola': 0, 'Violin II': 0, 'Violin I': 0}
		for p in self.bv.pitches:
			for g in p.groups:
				if g == "Violoncello" or g == "Violoncello.":
					partCheckList['Cello'] += 1
				elif g == "Viola.":
					partCheckList['Viola'] += 1
				elif g == "Violin 2" or g == "Violin 2." or g == "Violino 2.":
					partCheckList['Violin II'] += 1
				elif g == "Violin 1" or g == "Violin 1." or g == "Violino 1.":
					partCheckList['Violin I'] += 1
				else:
					partCheckList[g] += 1
		return partCheckList

	def voicePerPartCounterSimple(self):
		simpleParts = []
		for key in self.partVoiceCountList:
			if self.partVoiceCountList[key] != 1:
				simpleParts.append(None)
			else:
				simpleParts.append(1)
		return simpleParts

	# i.e. the part with the most voices is removed
	def voicePerPartCounterSimplified(self):
		adjustedVPPC = self.partVoiceCountList.copy()
		max = -1
		maxKey = None
		for key in self.partVoiceCountList:
			if self.partVoiceCountList[key] > max:
				max = self.partVoiceCountList[key]
				maxKey = key
		adjustedVPPC[maxKey] = "X"
		return adjustedVPPC


	def hasNonChordTones(self):
		return self.nonChordTones

	def getChord(self):
		return self.bv

	def toString(self):
		return (self.bv)

	def toTuple(self):
		pitchesForPrinting = []
		for n in self.bv.pitches:
			if isinstance(n, note.Note):
				pitchesForPrinting.append(n.nameWithOctave)
			elif isinstance(n, chord.Chord):
				tempList = []
				for p in n.pitches:
					tempList.append(p.nameWithOctave)
				printTuple = tuple(tempList)
				pitchesForPrinting.append(printTuple)
			else:
				pitchesForPrinting.append('rest')
		return tuple(pitchesForPrinting)

	def transposeToC(self):
		root = self.globalKey.tonic
		pc = root.pitchClass
		i = 12 - pc #interval to transpose by to get to key of C
		transposedPitches = []
		for p in self.bv.pitches:			
			transposedPitches.append(p.transpose(i).nameWithOctave)
		return tuple(transposedPitches)

# testing
def main():

	mvtString = "op18_no1_mov2"
	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	_QUARTET = _MUSICPATH + mvtString
	timeSignature = meter.TimeSignature('9/8')
	movement = converter.parse(_QUARTET + ".mxl")
	mvt = bigScore.BigScore(movement, timeSignature)
	mvt.globalKey = key.Key('d')

	print("bigVoicing() Tests --------")
	testBV1 = BigVoicing(mvt, 'i', 107, 2, 108, 1.0)
	print("testBV1 = BigVoicing(mvt, 'i', 107, 2, 108, 1.0)")
	print("testBV1.getChord():", testBV1.getChord())
	print("testBV1.nonChordTones (should be 3):", testBV1.nonChordTones)
	print("testBV1.hasOneVoiceToEachPart():", testBV1.hasOneVoiceToEachPart())
	print()

	mvt.globalKey = key.Key('D')
	testBV2 = BigVoicing(mvt, 'I', 90, 1, 92, 1)
	print("testBV2 = BigVoicing(mvt, 'I', 90, 1, 92, 1)")
	print("testBV2.getChord():", testBV2.getChord())
	print("testBV2.nonChordTones (should be like 20):", testBV2.nonChordTones)
	print("testBV2.hasOneVoiceToEachPart():", testBV2.hasOneVoiceToEachPart())
	print("testBV2.transposeToC():", testBV2.transposeToC())
	print()

	print("bigVL.BigVL(testBV1, testBV2).degree:", bigVL.BigVL(testBV1, testBV2).degree)
	print()

	mvt.globalKey = key.Key('d')
	testBV3 = BigVoicing(mvt, 'i6', 2, 2, 2, 3)
	print("testBV3 = BigVoicing(mvt, 'i6', 3, 2, 3, 3)")
	print("testBV3.getChord():", testBV3.getChord())
	print("testBV3.nonChordTones (should be 0):", testBV3.nonChordTones)
	print("testBV3.hasOneVoiceToEachPart():", testBV3.hasOneVoiceToEachPart())
	print("testBV3.transposeToC():", testBV3.transposeToC())
	print()

	mvt6 = getProgs.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no6_mov1")
	mvt6.globalKey = key.Key('B-')
	testBV4 = BigVoicing(mvt6, 'I', 1, 1, 2, 1)
	print("testBV4 = BigVoicing(mvt6, 'I', 1, 1, 2, 1)")
	print("testBV4.getChord():", testBV4.getChord())
	print("testBV4.nonChordTones (should be 0):", testBV4.nonChordTones)
	print("testBV4.hasOneVoiceToEachPart():", testBV4.hasOneVoiceToEachPart())
	print("testBV4.voicePerPartCounter() (should be {'Cello': 1, 'Viola': 1, 'Violin II': 3, 'Violin I': 2}) :", testBV4.voicePerPartCounter())
	print("testBV4.voicePerPartCounterSimple():", testBV4.voicePerPartCounterSimple())
	print("testBV4.voicePerPartCounterSimplified():", testBV4.voicePerPartCounterSimplified())

	print()

if __name__ == "__main__":
	main()

























