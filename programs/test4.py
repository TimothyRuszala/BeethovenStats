from music21 import *

romanN = roman.RomanNumeral('V6/5/V', key.Key('C'))
print(romanN.pitches)







# Checks if RN
					chordRE = re.compile("((Ger|It|Fr|N|b?[iIvV]+o?[+]?)+(b?#?o?[0-9]?/?)*)+|  ")
					isChord = chordRE.match(beatsChordsKeys[i])
					if isChord:
						chordRN = isChord.group()
						if chordRN == "  ":
							chordRN = "No RN"
						if currentBeat == None:
							currentBeat = 1.0
						currentVoicing = mvt.getVoicingAt(mNumb, currentBeat, chordRN)
						prevVoicing.update(mNumb, currentBeat)
						if prevVoicing == None: 
							prevVoicing = currentVoicing
							continue
#~~ADD_VL_TO_PROGS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
						newVL = voicing.VL(prevVoicing, currentVoicing, mvt)
						print(mNumb, currentBeat, newVL.rnTuple(), newVL.toString())
						progDict.addToProgs(newVL)
						giantProgDict.addToProgs(newVL)
						#currentBigVoicing = bigVoicing.BigVoicing(mvt, prevVoicing.rn, prevVoicing.mNumb, prevVoicing.beat, mNumb, currentBeat)
						prevVoicing = currentVoicing

def bass(self):
		lowestNote = note.Note(120)
		for x in range(0, 4):
			if isinstance(x, note.Note):
				if n.pitch.midi < lowestNote.pitch.midi:
					lowestNote = n
			elif isinstance(x, chord.Chord):
				if n.bass().midi < lowestNote.pitch.midi:
					lowestNote = note.Note(n.bass())
		if lowestNote.pitch.midi == 120:
			return 3
		else:
			return lowestNote

	def bassIndex(self):
		lowestNote = note.Note(120)
		lowestNoteIndex = None
		for x in range(0, 4):
			if isinstance(n, note.Note):
				if n.pitch.midi < lowestNote.pitch.midi:
					lowestNote = n
					lowestNoteIndex = x
			elif isinstance(n, chord.Chord):
				if n.bass().midi < lowestNote.pitch.midi:
					lowestNote = note.Note(n.bass())
					lowestNoteIndex = x
		if lowestNote.pitch.midi == 120:
			return 3 # this will probably cause the least damage
		else:
			return lowestNoteIndex





			
















