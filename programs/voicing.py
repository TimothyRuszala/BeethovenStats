from music21 import *
import pprint
import operator
import JPa

class Voicing():
	""" Voicing object to contain a given chordal verticality """
	# This program I think mostly inputs as notes. Might possibly want to do pitches. Also accepts chords!.
	def __init__(self, cello = None, viola = None, violin2 = None, violin1 = None, rn = None, mNumb = None, beat = None, theKey = None, celloClef = None, mvtString = None):
		#voi = voicing.Voicing(cel, viol, v2, v1, rn, mNumb, beat, self.globalKey, celloClef)
		if celloClef is not None and isinstance(celloClef, clef.TrebleClef): #Probably won't work if clef changes in middle of the bar...
			if isinstance(cello, note.Note):
				cello.pitch.transpose('-P8')
		
		self.cello = cello
		self.viola = viola
		self.violin2 = violin2
		self.violin1 = violin1
		self.pitches = [violin1, violin2, viola, cello] # CHECK HERE FOR BUGS!

		self.rn = rn # this is the roman numeral associated with this voicing
		self.mNumb = mNumb
		self.beat = beat
		self.theKey = theKey

		self.mvtString = mvtString
		self.degree = self.findDegree()

	def findDegree(self):
		degree = 0
		for x in self.pitches:
			if isinstance(x, note.Note):
				degree += 1
			elif isinstance(x, chord.Chord):
				degree += len(x.pitches)
		return degree


	def getKey(self):
		return self.theKey

	def bass(self):
		lowestNote = note.Note(120)
		for n in self.pitches:
			if isinstance(n, note.Note):
				if n.pitch.midi < lowestNote.pitch.midi:
					lowestNote = n
			elif isinstance(n, chord.Chord):
				for i in n.pitches:
					if i.midi < lowestNote.pitch.midi:
						lowestNote = note.Note(i)
		else:
			return lowestNote

	def bassIndex(self):
		lowestNote = note.Note(120)
		lowestNoteIndex = None
		for x in range(0, 4):
			if isinstance(x, note.Note):
				if n.pitch.midi < lowestNote.pitch.midi:
					lowestNote = x
					lowestNoteIndex = x
			elif isinstance(x, chord.Chord):
				if x.bass().midi < lowestNote.pitch.midi:
					lowestNote = note.Note(x.bass())
					lowestNoteIndex = x
		if lowestNote.pitch.midi == 120:
			return 3 # this will probably cause the least damage
		else:
			return lowestNoteIndex

	# transposes the voicing to C for the sake of VL's toString()
	def transposeToC(self):
		#print("self.key =", self.key)
		root = self.theKey.tonic
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
		v = (transposedPitches[0], transposedPitches[1], transposedPitches[2], transposedPitches[3])
		return v

	# in original key
	def toString(self):
		pitchesForPrinting = []
		for n in self.pitches:
			if isinstance(n, note.Note):
				pitchesForPrinting.append(n.name)
			elif isinstance(n, chord.Chord):
				tempList = []
				for p in reversed(n.pitches):
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



		# the pitchclass content, abstracted away from chords and octaves
	def toTransposedTuplePC(self):
		transposedVLList = self.transposeToC()
		transposedVLPC = []
		for n in reversed(transposedVLList):
			if isinstance(n, note.Note):
				pc = n.pitch.pitchClass
				if pc not in transposedVLPC:
					transposedVLPC.append(pc)
			elif isinstance(n, chord.Chord):
				pcTuple = []
				for p in n.pitches:
					pc = p.pitchClass
					if pc not in transposedVLPC:
						transposedVLPC.append(pc)
			# no rests included
		return transposedVLPC

		return tuple(transposedVLPC)

	def location(self):
		return (mNumb, beat)

class VL():
	""" Voice-Leading object to contain motion between two Voicings """
	def __init__(self, voicing1, voicing2, bigscore = None):
		self.v1 = voicing1
		self.v2 = voicing2		

		# print("RE-UPDATING.....")
		# updating self.v1. Note that it ignores rests.
		if bigscore != None: # i.e. update self.v1
			self.filename = bigscore.movement.id
			startMNumb = self.v1.mNumb
			startBeat = self.v1.beat

			endMNumb = self.v2.mNumb
			endBeat = self.v2.beat
			romanN = roman.RomanNumeral(self.v1.rn, self.v1.theKey)
			#print(self.v1.theKey, bigscore.globalKey, self.v1.pitches, self.v1.bass().pitch.midi)
			bassVoiceIndex = self.v1.bassIndex()
			for part in range(0, 4):
				updatedFlag = False # Sorry that this is so clumsy lol
				for x in reversed(range(startMNumb, endMNumb + 1)):
					m = bigscore.getMeasure(x, part)
					stack = []
					# print("mNumb:", x, "PART", part, "m.notes", len(m.notes), [n for n in m.notes])
					for n in m.notes:
						if x == startMNumb and n.beat < startBeat:
							#print(x, "n.beat:", n.beat, "startBeat:", startBeat)
							continue
						elif x == endMNumb and n.beat >= endBeat:
							#print(x, "n.beat:", n.beat, "endBeat:", endBeat)
							break
						else:
							# print("appending", n)
							stack.append(n)
					# print("in ReUpdating... part:", part, "stack:", stack)
					while stack:
						# print("hit while stack()")
						noteInQuestion = stack.pop()
						# print("noteInQuestion:", part, noteInQuestion)

						#handles rests and noChord
						if isinstance(noteInQuestion, (note.Rest, harmony.NoChord)):
							#self.v1.pitches[part] = note.Rest()
							continue

						# handles notes
						elif isinstance(noteInQuestion, note.Note):
							if part == bassVoiceIndex:
								continue # no update for cello (bass) part because that should reflect in the romanN
							elif noteInQuestion.pitch.pitchClass in romanN.pitchClasses:
								self.v1.pitches[part] = noteInQuestion
								updatedFlag = True
								break

						#Handling Chords. This might to be weird with chords in the cello. Maybe fix later.
						# The only error I think would be in the case of a cello chord with NCTs above bass, or in pedal chords.
						elif isinstance(noteInQuestion, chord.Chord):
							chordInQuestion = noteInQuestion # for readability
							if part == bassVoiceIndex:
								if chordInQuestion.bass() == romanN.bass().pitchClass:
									self.v1.pitches[part] = chordInQuestion
									updatedFlag = True
									break
								else:
									continue
							else:
								self.v1.pitches[part] = chordInQuestion
								# index = 0
								# for x in chordInQuestion.pitches:
								# 	if x.pitchClass in romanN.pitchClasses:
										
								# 		self.v1.pitches[part][index] = x
								updatedFlag = True
									# for now, in the case where there's a NCT in the chord, it's just skipped. Might want to fix.
									#index += 1
								break
						else:
							print("missed something 2!")
					if updatedFlag:
						break

		self.degree = (self.v1.degree, self.v2.degree)

		self.theKey = voicing2.getKey()

		self.intervals = []

		v1Instruments = [voicing1.cello, voicing1.viola, voicing1.violin2, voicing1.violin1]
		v2Instruments = [voicing2.cello, voicing2.viola, voicing2.violin2, voicing2.violin1]

		# Gets intervals
		for n in range(0, 4):
			i = self.v1.pitches[n]
			j = self.v2.pitches[n]
			if isinstance(i, note.Note) and isinstance(j, note.Note):
				self.intervals.append(interval.notesToChromatic(i, j).semitones)
			# handling chords
			elif isinstance(i, chord.Chord) and isinstance(j, chord.Chord):
				pitchIntList = []
				if len(i.pitches) is len(j.pitches):
					for q in range(0, len(i.pitches)):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
				else: # In the case of chords of different numbers of pitches, simply ignores some notes.
					#self.simple = 0
					lo = min(len(i.pitches), len(j.pitches))
					pitchIntList = []
					for q in range(0, lo):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, note.Note) and isinstance(j, chord.Chord):
				#self.simple = 0
				pitchIntList = []
				for q in range(0, len(j.pitches)):
					pitchIntList.append(interval.notesToChromatic(i, j.pitches[q]).semitones)
				self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, chord.Chord) and isinstance(j, note.Note):
				#self.simple = 0
				pitchIntList = []
				for q in range(0, len(i.pitches)):
					pitchIntList.append(interval.notesToChromatic(i.pitches[q], j).semitones)
				self.intervals.append(tuple(pitchIntList))
			else:
				self.intervals.append(999)
		#self.intervals.sort() 				FOR NOW THERE IS NO SORTING. THIS WILL NEED TO BE FIXED.
		self.intervals = tuple(self.intervals)
		#self.isSimple = self.isSimple()

	# Is there a 1:1 correspondence between the notes in each voicing?
	def isSimple(self):

		intervalsLength = 0
		for x in self.intervals:
			if isinstance(x, int):
				intervalsLength += 1
			elif isinstance(x, tuple):
				intervalsLength += len(x)
		

		# print("intervalsLength:", intervalsLength)
		# print("self.degree:", self.degree)
		if self.degree[0] == self.degree[1] and self.degree[0] == intervalsLength:
			return True
		else:
			return False

	def getLocation(self):
		return (self.v2.mNumb, self.v2.beat)

	def getRange(self):
		return (self.v1.mNumb, self.v1.beat, self.v2.mNumb, self.v2.beat, self.v1.mvtString)

	def rnTuple(self):
		return (self.v1.rn, self.v2.rn)

	def getKey(self):
		return self.theKey

	def toString(self):
		return self.v1.toString() + " -> " + self.v2.toString()

	def toStringTransposed(self):
		return self.v1.transposeToC().toString() + " -> " + self.v2.transposeToC().toString() #+ "intervals: " + intervals

	def intervalTuple(self):
		return self.intervals

	def toTupleTuple(self):
		return (self.v1.toTuple(), self.v2.toTuple())

	def toTransposedTupleTuple(self):
		return (self.v1.transposeToC(), self.v2.transposeToC())

	# condenses intervals such that each pitch class is only represented once. e.g. ((0, 0), (5, (-1, 2), (9, -2))) means IV6/4 -> I
	def getGenericIntervals(self, shouldSort = True):
		genIntDict = {}
		tttv1 = self.toTransposedTupleTuple()[0]
		for i in range(0, 4):
			n = tttv1[i]
			#print(n)
			if isinstance(n, note.Note):
				pc = tttv1[i].pitch.pitchClass
				if pc not in genIntDict:
					genIntDict[pc] = []
				# if self.intervals[i] == None:
				# 		genIntDict[pc].append(None)
				# 		continue
				intervalValue = self.intervals[i]
				if isinstance(intervalValue, int):
					genIntDict[pc].append(intervalValue)
					genIntDict[pc].sort()
				elif isinstance(intervalValue, tuple):
					for z in intervalValue:
						genIntDict[pc].append(z)
					genIntDict[pc].sort()
			elif isinstance(n, chord.Chord):
				for x in range(0, len(n.pitches)):
					pc = n.pitches[x].pitchClass
					if pc not in genIntDict:
						genIntDict[pc] = []
					if self.intervals[i] == 999:
						genIntDict[pc].append(999)
						continue
					try:
						intervalValue = self.intervals[i][x]
					except:
						intervalValue = self.intervals[i]
					if isinstance(intervalValue, int):
						genIntDict[pc].append(intervalValue)
						genIntDict[pc].sort()
					elif isinstance(intervalValue, tuple):
						for z in intervalValue:
							genIntDict[pc].append(z)
						genIntDict[pc].sort()

		#pprint.pprint(genIntDict)
		if shouldSort == True:
			genIntSorted = sorted(genIntDict.items(), key = operator.itemgetter(0))
			return genIntSorted
		else:
			return genIntDict




def main():
	
	print("Voicing bass() testing ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
	lowestInCello = Voicing(cello = note.Note('C3'), viola = note.Note('E4'), violin2 = note.Note('C5'), violin1 = note.Note('G5'), rn = 'I', theKey = key.Key('C'))
	print("lowestInCello.pitches.index(lowestInCello.bass()) (should be 3):", lowestInCello.pitches.index(lowestInCello.bass()))
	lowestInViola = Voicing(cello = note.Note('C4'), viola = note.Note('E3'), violin2 = note.Note('C5'), violin1 = note.Note('G5'), rn = 'I', theKey = key.Key('C'))
	print("lowestInViola.pitches.index(lowestInViola.bass()) (should be 2):", lowestInViola.pitches.index(lowestInViola.bass()))
	print()

	print("Voicing isSimple() testing ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
	simpleVoicing1 = Voicing(cello = note.Note('C3'), viola = note.Note('E4'), violin2 = note.Note('C5'), violin1 = note.Note('G5'), rn = 'I', theKey = key.Key('C'))
	simpleVoicing2 = Voicing(cello = note.Note('G2'), viola = note.Note('D4'), violin2 = note.Note('B4'), violin1 = note.Note('F5'), rn = 'V7', theKey = key.Key('C'))
	complexVoicing1 = Voicing(cello = chord.Chord(('C2', 'G2')), viola = note.Note('E4'), violin2 = note.Note('C5'), violin1 = note.Note('G5'), rn = 'I', theKey = key.Key('C'))
	complexVoicing2 = Voicing(cello = chord.Chord(('D2', 'G2')), viola = note.Note('D4'), violin2 = note.Note('B4'), violin1 = note.Note('F5'), rn = 'V7', theKey = key.Key('C'))
	complexVoicing3 = Voicing(cello = note.Note('D2'), viola = chord.Chord(('D4', 'G4')), violin2 = note.Note('B4'), violin1 = note.Note('F5'), rn = 'V7', theKey = key.Key('C'))
	complexerVoicing1 = Voicing(cello = note.Note('C3'), viola = chord.Chord(('G3', 'C4', 'E4')), violin2 = note.Note('C5'), violin1 = note.Note('G5'), rn = 'I', theKey = key.Key('C'))
	complexerVoicing2 = Voicing(cello = note.Note('G2'), viola = chord.Chord(('G3', 'B3', 'D4')), violin2 = note.Note('B4'), violin1 = note.Note('F5'), rn = 'V7', theKey = key.Key('C'))
	simpleVoicingWithRests1 = Voicing(cello = note.Note('G2'), viola = None, violin2 = note.Note('B4'), violin1 = note.Note('F5'), rn = 'V7', theKey = key.Key('C'))

	noteToNoteVL = VL(simpleVoicing1, simpleVoicing2)
	print("noteToNoteVL.toTupleTuple()", noteToNoteVL.toTupleTuple())
	print("noteToNoteVL.intervals:", noteToNoteVL.intervals)
	print("noteToNoteVL.getGenericIntervals():", noteToNoteVL.getGenericIntervals())
	print("noteToNoteVL.isSimple():", noteToNoteVL.isSimple())
	print()
	print("noteToNoteVL.degree:", noteToNoteVL.degree)
	print()

	noteToChordVL = VL(simpleVoicing1, complexVoicing2)
	print("noteToChordVL.toTupleTuple()", noteToChordVL.toTupleTuple())
	print("noteToChordVL.intervals:", noteToChordVL.intervals)
	print("noteToChordVL.getGenericIntervals():", noteToChordVL.getGenericIntervals())
	print("noteToChordVL.isSimple():", noteToChordVL.isSimple())
	print()
	print("noteToChordVL.degree:", noteToChordVL.degree)
	print()

	chordToNoteVL = VL(complexVoicing1, simpleVoicing2)
	print("chordToNoteVL.toTupleTuple()", chordToNoteVL.toTupleTuple())
	print("chordToNoteVL.intervals:", chordToNoteVL.intervals)
	print("chordToNoteVL.getGenericIntervals():", chordToNoteVL.getGenericIntervals())
	print("chordToNoteVL.isSimple():", chordToNoteVL.isSimple())
	print()
	print("chordToNoteVL.degree:", chordToNoteVL.degree)
	print()

	chordToChordVL = VL(complexVoicing1, complexVoicing2)
	print("chordToChordVL.toTupleTuple()", chordToChordVL.toTupleTuple())
	print("chordToChordVL.intervals:", chordToChordVL.intervals)
	print("chordToChordVL.getGenericIntervals():", chordToChordVL.getGenericIntervals())
	print("chordToChordVL.isSimple():", chordToChordVL.isSimple())
	print()
	print("chordToChordVL.degree:", chordToChordVL.degree)
	print()

	chordToChordVL2 = VL(complexVoicing2, complexVoicing3)
	print("chordToChordVL2.toTupleTuple()", chordToChordVL2.toTupleTuple())
	print("chordToChordVL2.intervals:", chordToChordVL2.intervals)
	print("chordToChordVL2.getGenericIntervals():", chordToChordVL2.getGenericIntervals())
	print("chordToChordVL2.isSimple():", chordToChordVL2.isSimple())
	print()
	print("chordToChordVL2.degree:", chordToChordVL2.degree)
	print()

	chordToComplexerChordVL = VL(complexVoicing1, complexerVoicing2)
	print("chordToComplexerChordVL.toTupleTuple()", chordToComplexerChordVL.toTupleTuple())
	print("chordToComplexerChordVL.intervals:", chordToComplexerChordVL.intervals)
	print("chordToComplexerChordVL.getGenericIntervals():", chordToComplexerChordVL.getGenericIntervals())
	print("chordToComplexerChordVL.isSimple():", chordToComplexerChordVL.isSimple())
	print()
	print("chordToComplexerChordVL.degree:", chordToComplexerChordVL.degree)
	print()

	complexerChordToChordWithRests = VL(complexerVoicing1, simpleVoicingWithRests1)
	print("complexerChordToChordWithRests.toTupleTuple()", complexerChordToChordWithRests.toTupleTuple())
	print("complexerChordToChordWithRests.intervals:", complexerChordToChordWithRests.intervals)
	print("complexerChordToChordWithRests.getGenericIntervals():", complexerChordToChordWithRests.getGenericIntervals())
	print("complexerChordToChordWithRests.isSimple():", complexerChordToChordWithRests.isSimple())
	print()
	print("complexerChordToChordWithRests.degree:", complexerChordToChordWithRests.degree)
	print()



	# print("Testing VL() with updating self.v1: ~ ~ ~")
	# mvt = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op59_no7_mov3")
	print(complexVoicing1.pitches)
	print("complexVoicing1.toTransposedTuplePC():", complexVoicing1.toTransposedTuplePC())


	# ('V', 'viio2/V') ['E', 'E', 'C', 'C'] -> ['rest', ('B', 'F'), 'D', 'rest']
	yetAnotherTestVoicing1 = Voicing(cello = note.Note('E3'), viola = note.Note('E4'), violin2 = note.Note('C5'), violin1 = note.Note('C5'), rn = 'V', theKey = key.Key('F'))
	yetAnotherTestVoicing2 = Voicing(cello = None, viola = chord.Chord(('B3', 'F4')), violin2 = note.Note('D5'), violin1 = None, rn = 'viio2/V', theKey = key.Key('F'))
	yetAnotherTestVL = VL(yetAnotherTestVoicing1, yetAnotherTestVoicing2)
	print("yetAnotherTestVL.toTupleTuple()", yetAnotherTestVL.toTupleTuple())
	print("yetAnotherTestVL.intervals:", yetAnotherTestVL.intervals)
	print("yetAnotherTestVL.getGenericIntervals():", yetAnotherTestVL.getGenericIntervals())
	print("yetAnotherTestVL.isSimple():", yetAnotherTestVL.isSimple())
	print()
	print("yetAnotherTestVL.degree:", yetAnotherTestVL.degree)
	print()


	# NOTE: When we have an incorrect RN analysis, we can get really weird stuff. Note in paper, move on.
	print("Specific spot check:")
	mvt = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op74_no10_mov4")
	mvt.globalKey = key.Key('Eb')
	specVoi1 = mvt.getVoicingAt(21, 4, rn = 'V7')
	mvt.update(specVoi1, 22, 1)
	specVoi2 = mvt.getVoicingAt(25, 1, rn = 'I')
	specVL = VL(specVoi1, specVoi2, mvt)
	print(specVL.rnTuple(), specVL.toString())
	print(print("specVL.getGenericIntervals():", specVL.getGenericIntervals()))




if __name__ == "__main__":
	main()






