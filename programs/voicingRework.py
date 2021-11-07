from music21 import *

class Voicing():
	""" Voicing object to contain a given chordal verticality """
	# This program I think mostly inputs as notes. Might possibly want to do pitches. ¡Also accepts chords!.
	def __init__(self, cello = None, viola = None, violin2 = None, violin1 = None, rn = None, mNumb = None, beat = None, theKey = None, celloClef = None):
		#voi = voicing.Voicing(cel, viol, v2, v1, rn, mNumb, beat, self.globalKey, celloClef)
		if celloClef is not None and isinstance(celloClef, clef.TrebleClef): #Probably won't work if clef changes in middle of the bar...
			if isinstance(cello, note.Note):
				cello.pitch.transpose('-P8')
		self.cello = cello
		self.viola = viola
		self.violin2 = violin2
		self.violin1 = violin1
		self.instruments = [self.violin1, self.violin2, self.viola, self.cello]
		self.pitches = [cello, viola, violin2, violin1]

		self.rn = rn # this is the roman numeral associated with this voicing
		self.mNumb = mNumb
		self.beat = beat
		#print("in Voicing(), theKey =", theKey)
		self.theKey = theKey
		#print("in Voicing(), self.key =", self.key)

	def getKey(self):
		return self.theKey

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

		v1Instruments = [voicing1.cello, voicing1.viola, voicing1.violin2, voicing1.violin1]
		v2Instruments = [voicing2.cello, voicing2.viola, voicing2.violin2, voicing2.violin1]

		self.v1 = voicing1
		self.theKey = voicing1.getKey()
		self.v2 = voicing2
		self.intervals = []

		

		#Ok, so this whole segment definitely has 1000 bugs. Test.
		for n in range(0, 4):
			i = self.v1.pitches[n]
			j = self.v2.pitches[n]
			if isinstance(i, note.Note) and isinstance(j, note.Note):
				self.intervals.append(interval.notesToChromatic(i, j).semitones)
			elif isinstance(i, chord.Chord) and isinstance(j, chord.Chord):
				pitchIntList = []
				if len(i.pitches) is len(j.pitches):
					for q in range(0, len(i.pitches)):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
				else: # In the case of chords of different numbers of pitches, simply ignores some notes.
					lo = min(len(i.pitches), len(j.pitches))
					pitchIntList = []
					for q in range(0, lo):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, note.Note) and isinstance(j, chord.Chord):
				pitchIntList = []
				for q in range(0, len(j.pitches)):
					pitchIntList.append(interval.notesToChromatic(i, j.pitches[q]).semitones)
				self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, chord.Chord) and isinstance(j, note.Note):
				pitchIntList = []
				for q in range(0, len(i.pitches)):
					pitchIntList.append(interval.notesToChromatic(i.pitches[q], j).semitones)
				self.intervals.append(tuple(pitchIntList))
			else:
				self.intervals.append(999)
		#self.intervals.sort() 				FOR NOW THERE IS NO SORTING. THIS WILL NEED TO BE FIXED.
		self.intervals = tuple(self.intervals)

	def getLocation(self):
		return (self.v2.mNumb, self.v2.beat)

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
		return (self.v1.transposeToC().toTuple(), self.v2.transposeToC().toTuple())

class VLBackup():
	""" Voice-Leading object to contain motion between two Voicings """
	def __init__(self, voicing1, voicing2):
		self.v1 = voicing1
		#print("voicing1.getKey() =", voicing1.getKey())
		self.theKey = voicing1.getKey()
		#print("self.theKey =", self.theKey)
		self.v2 = voicing2
		self.intervals = []

		v1Instruments = [voicing1.cello, voicing1.viola, voicing1.violin2, voicing1.violin1]
		v2Instruments = [voicing2.cello, voicing2.viola, voicing2.violin2, voicing2.violin1]

		#Ok, so this whole segment definitely has 1000 bugs. Test.
		for n in range(0, 4):
			i = self.v1.pitches[n]
			j = self.v2.pitches[n]
			if isinstance(i, note.Note) and isinstance(j, note.Note):
				self.intervals.append(interval.notesToChromatic(i, j).semitones)
			elif isinstance(i, chord.Chord) and isinstance(j, chord.Chord):
				pitchIntList = []
				if len(i.pitches) is len(j.pitches):
					for q in range(0, len(i.pitches)):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
				else: # In the case of chords of different numbers of pitches, simply ignores some notes.
					lo = min(len(i.pitches), len(j.pitches))
					pitchIntList = []
					for q in range(0, lo):
						pitchIntList.append(interval.notesToChromatic(i.pitches[q], j.pitches[q]).semitones)
					self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, note.Note) and isinstance(j, chord.Chord):
				pitchIntList = []
				for q in range(0, len(j.pitches)):
					pitchIntList.append(interval.notesToChromatic(i, j.pitches[q]).semitones)
				self.intervals.append(tuple(pitchIntList))
			elif isinstance(i, chord.Chord) and isinstance(j, note.Note):
				pitchIntList = []
				for q in range(0, len(i.pitches)):
					pitchIntList.append(interval.notesToChromatic(i.pitches[q], j).semitones)
				self.intervals.append(tuple(pitchIntList))
			else:
				self.intervals.append(999)
		#self.intervals.sort() 				FOR NOW THERE IS NO SORTING. THIS WILL NEED TO BE FIXED.
		self.intervals = tuple(self.intervals)

	def getLocation(self):
		return (self.v2.mNumb, self.v2.beat)

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
		return (self.v1.transposeToC().toTuple(), self.v2.transposeToC().toTuple())


def main():
	c = note.Note('c', quarterLength = 1)
	d = note.Note('d', quarterLength = 1)
	e = note.Note('e', quarterLength = 1)
	f = note.Note('f', quarterLength = 1)
	g = note.Note('g', quarterLength = 1.5)


	testMNumb = 1
	testBeat = 1
	testKey = key.Key('C')
	testCelloClef = None

	testVoicing1 = Voicing(c, d, e, f, "I", testMNumb, testBeat, testKey, testCelloClef)
	print("testVoicing1:", testVoicing1.toTuple(), "evidence (should be 1):", testVoicing1.findSelfEvidence())
	testVoicing2 = Voicing(c, d, e, g, "V", testMNumb, testBeat + 1, testKey, testCelloClef)
	print("testVoicing2:", testVoicing2.toTuple(), "evidence (should be 2):", testVoicing2.findSelfEvidence())
	print("testVoicing1.getKey() =", testVoicing1.getKey())

	testVL = VL(testVoicing1, testVoicing2)
	print("testVL.getKey() =", testVL.getKey())









if __name__ == "__main__":
	main()






