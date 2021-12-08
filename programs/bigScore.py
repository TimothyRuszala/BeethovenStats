from music21 import *
import voicing
import re
import pprint
import bigScore
import getProgs
from fractions import Fraction


# BigScore is an object which preprocesses a .mxl music file to prepare it for statistical analysis.

class BigScore:
# extracts all the parts of the movement into its individual instruments
	def __init__(self, movement, timeSignature = None, globalKey = None, mxlFile = None):
		self.movement = movement
		if mxlFile != None:
			self.mvtString = mxlFile.replace('.mxl', '')
		self.violin1  = movement.parts[0]
		self.violin2  = movement.parts[1]
		self.viola    = movement.parts[2]
		self.cello    = movement.parts[3]
		self.instruments = [self.violin1, self.violin2, self.viola, self.cello]
		self.timeSignature = timeSignature
		self.globalKey = globalKey

	# returns the name of the movement
	def getMvtString(self):
		return self.mvtString

	# Shows the score in the default music notation software
	def show(self):
		self.movement.show()

	# Does the score have a pickup measure?
	def hasPickup(self):
		if self.movement.parts[0].getElementsByClass(stream.Measure)[1].number == 0:
			return "true"
		else:
			return 0

	# finds the first voicing
	def firstVoicing(self):

		v1Note = self.violin1.getElementsByClass(stream.Measure)[0].notesAndRests[0]
		v2Note = self.violin2.getElementsByClass(stream.Measure)[0].notesAndRests[0]
		violNote = self.viola.getElementsByClass(stream.Measure)[0].notesAndRests[0]
		cNote    = self.cello.getElementsByClass(stream.Measure)[0].notesAndRests[0]
		firstVoicing = voicing.Voicing(cNote, violNote, v2Note, v1Note)
		return firstVoicing

	# creates an excerpt of the score, starting at mNumbStart, ending at mNumbEnd
	def excerpt(self, mNumbStart, mNumbEnd):
		# Very small bug: When mNumbStart = 1, also includes pickup measure if one exists.
		if self.hasPickup():
			mNumbStart -= 1
			mNumbEnd   -= 1
		return self.movement.measures(mNumbStart, mNumbEnd)

	def excerptGood(self, mNumbStart, beatStart, mNumbEnd, beatEnd):
		measureExcerpt = self.excerpt(mNumbStart, mNumbEnd)
		smallExcerpt = stream.Score()
		smallExcerpt.repeatAppend(stream.Part(), 4)
		for p in smallExcerpt.parts:
			p.append(stream.Measure())
		lastNoteBeforeStart = None
		youShouldAppendLastNoteBeforeStartFlag = True

		for i in range(0, 4):
			for n in measureExcerpt.parts[i].flat.notesAndRests:
				if n.measureNumber == mNumbStart:
					if n.beat < beatStart:
						lastNoteBeforeStart = n
						continue
					else:
						smallExcerpt.parts[i][0].append(n)
				elif n.measureNumber == mNumbEnd:
					if n.beat > beatEnd:
						break
					else:
						smallExcerpt.parts[i][0].append(n)
				else:
					smallExcerpt.parts[i][0].append(n)
		return smallExcerpt


	# Because a chord's voicing can change while the chord's roman numeral itself stays the same,
	# this method updates a voicing to show what the voicing looks like at a specified beat. Useful
	# for determining voice-leadings.
	def update(self, voi, mNumb, beat):
		romanN = roman.RomanNumeral(voi.rn, self.globalKey)
		bassPitchClass = romanN.bass().pitchClass

		# Finding the bass note is slightly challenging becuase sometimes it is in the viola, not
		# the cello. This variable helps determine which part has the lowest note.
		lowestPossibleBassNotesForEachPart = [None, None, None, None]
		for part in range(0, 4):
			correctNote = None
			for x in range(voi.mNumb, mNumb + 1):
				m = self.getMeasure(x, part)
				for n in m.notesAndRests:
					if n.beat < voi.beat and x == voi.mNumb:
						continue
					elif x == mNumb and n.beat >= beat:
						break
					elif isinstance(n, harmony.NoChord):
						continue
					elif isinstance(n, note.Note):
						if n.pitch.pitchClass in romanN.pitchClasses:
							correctNote = n
							if n.pitch.pitchClass == bassPitchClass:
								lowestPossibleBassNotesForEachPart[part] = n
							break
					elif isinstance(n, chord.Chord):
						correctNote = n
						if n.bass().pitchClass == bassPitchClass:
							lowestPossibleBassNotesForEachPart[part] = note.Note(n.bass())
						break
				if correctNote != None:
					break
			if correctNote != None:
				voi.pitches[part] = correctNote

		# making sure we have the right bass.
		if voi.bass() == -1:
			print("bass Error")
			return
		if voi.bass().pitch.pitchClass != romanN.bass().pitchClass and voi.theKey == self.globalKey:
			trueBass = note.Note(120)
			for n in lowestPossibleBassNotesForEachPart:
				if n == None:
					continue
				if n.pitch.midi < trueBass.pitch.midi:
					trueBass = n
			if trueBass.pitch.midi != 120:
				bassPart = lowestPossibleBassNotesForEachPart.index(trueBass)
				voi.pitches[bassPart] = trueBass
		return voi


	# Creates a voicing object representing a specific point in the score. Filters out
	# non-chord tones.
	def getVoicingAt(self, mNumb, beat, rn = None):

		notes = [None, None, None, None]
		try:
			celloClef = self.getMeasure(mNumb, 3).clef
		except: 
			print("oops! Sorry, cello clef! That's the end!")
			return None

		for i in range(0, 4):
			notes[i] = self.getNoteOrRestAtBeat(i, mNumb, beat)

		voi = voicing.Voicing(notes[3], notes[2], notes[1], notes[0], rn, mNumb, beat, self.globalKey, celloClef, self.mvtString)
		return voi

	# helper function which determines what note is sounding, or whether the part is resting, at a specified
	# beat. This operation is trickier than it sounds, because if e.g. we are interested in beat 3, and the part
	# has a half note on beat 2, the "sounding element" at beat 3 is specified earlier in the score.
	def getNoteOrRestAtBeat(self, part, measure, beat,):

		excerpt = self.getMeasure(measure, part)
		beatCap = beat
		noteOrRest = None
		prevElement = None
		for n in excerpt.notesAndRests:
			if n.beat > beatCap:
					break
			prevElement = n
		else:
			for n in excerpt.notesAndRests:
				if n.beat > beatCap:
					if isinstance(n, note.Rest):
						break
					elif isinstance(n, note.Note) and (n.pitch.pitchClass in romanN.pitchClasses):
						break
					elif isinstance(n, chord.Chord) and (n.pitchClasses in romanN.pitchClasses):
						break
				prevElement = n
		return prevElement # this gives us the element not greater than beatCap, i.e. the element at or before beatCap


	# Helper function which finds the first chord tone in a part after a given beat. Because we have roman numeral
	# information, this effectively filters out non-chord tones.
	def getChordToneAtOrAfterBeat(self, part, measure, beat, rn):

		excerpt = self.getMeasure(measure, part)
		noteOrRest = None
		prevElement = None
		romanN = roman.RomanNumeral(rn, globalKey)
		for n in excerpt.notesAndRests:
			if n.beat < beat:
				if n.pitch.pitchClass in romanN.pitchClasses:
					prevElement = n
			elif n.beat >= beatCap:
				if isinstance(n, note.Rest):
					return "rest"
				elif isinstance(n, note.Note) and (n.pitch.pitchClass in romanN.pitchClasses):
					return n
				elif isinstance(n, chord.Chord):
					return n
			prevElement = n
		return prevElement # this gives us the element not greater than beatCap, i.e. the element at or before beatCap

	# extracts measure number from a line of rntext
	def getMeasureNumber(self, line):
		mmRE = re.compile('[0-9]*')
		m = mmRE.match(line, 1) #Gets the measure number in form "mxxx"
		mNumb = int(m.group()) # measure number
		return mNumb

	# creates a list of beats specified in the rntext file, i.e. beats which coincide with a chord change
	def extractBeatInfo(self, line):
		#This RE makes a list of relevant beats in the rntext.
		isBeat = re.compile('\\sb\\d.?\\d*')
		beats = isBeat.findall(line)
		for i in range(0, len(beats)):
			beats[i] = float(beats[i][2:len(beats[i])]) # removes 'b' from e.g. 'b1.33'
			beats[i] = Fraction(beats[i]).limit_denominator(20)
		beats.insert(0, 1) #inserts beat 1
		return beats

	# Makes a list of the chords in each line.
	def extractChordAndKeyInfo(self, line):
		isChordOrKey = re.compile("[a-g][b|#]?:|b?[(Ger)iIvV]+[bo\\+/(Ger)iIvV[0-9]*|  ", re.IGNORECASE)
		chordsOrKey = isChordOrKey.findall(line)
		return chordsOrKey

	def extractChords(self, line):
		chordRE = re.compile("b?(Ger|[iIvV])+(Ger|[bo\\+/iIvV[0-9])*|  ", re.IGNORECASE)
		return chordRE.findall(line)

	def getKey(self):
		return self.globalKey

	# Excerpts a given measure from the BigScore as a music21 Measure object.
	def getMeasure(self, mNumb, part = 0):
		measures = self.movement.parts[part].recurse().getElementsByClass(stream.Measure)
		if mNumb >= len(measures):
			return None
		m = measures[mNumb]
		counter = 0
		if m.measureNumber != mNumb:
			m = measures[mNumb + (mNumb - m.measureNumber)]
		return m

def main():

	# mvt_op59_no7_mov3_HAS_PICKUP = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op59_no7_mov3")
	# mvt_op18_no1_mov3_NO_PICKUP = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no1_mov3")
	# mvt_op131_no14_mov2_WEIRD = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op131_no14_mov2")


	# print("getMeasure() tests ~ ~ ~ ~ ~ ~ ~ ~ ~")
	# print("mvt_op59_no7_mov3_HAS_PICKUP.getMeasure(", 1, ") (should be 1):")
	# mvt_op59_no7_mov3_HAS_PICKUP.getMeasure(1).show('text')
	# print("mvt_op18_no1_mov3_NO_PICKUP.getMeasure(", 1, ") (should be 1):")
	# mvt_op18_no1_mov3_NO_PICKUP.getMeasure(1).show('text')
	# print("mvt_op131_no14_mov2_WEIRD.getMeasure(", 1, ") (should be 1):")
	# mvt_op131_no14_mov2_WEIRD.getMeasure(1).show('text')
	# print("fin.")

	#mvt_op18_no1_mov3_NO_PICKUP.excerptGood(2, 1, 6, 2).show()

	op18no3mov1 = getProgs.load(str(pathlib.Path(__file__).parents[1]) +
             "/Music/Beethoven Quartets/op18_no3_mov1")
	m = op18no3mov1.getMeasure(13, part = 2)
	print(len(m.notes))

if __name__ == "__main__":
	main()




