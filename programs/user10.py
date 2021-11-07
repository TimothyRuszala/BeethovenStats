from music21 import *

s = corpus.parse('bwv66.6')
sChords = s.chordify()
sFlat = sChords.flat
sOnlyChords = sFlat.getElementsByClass('Chord')

displayPart = stream.Part(id='displayPart')

def appendChordPairs(thisChord, nextChord):
	if ((thisChord.isTriad() is True or
		thisChord.isSeventh() is True) and
			thisChord.root().name == "A"):
		closePositionThisChord = thisChord.closedPosition(forceOctave = 4)
		closePositionNextChord = nextChord.closedPosition(forceOctave = 4)

		m = stream.Measure()
		m.append(closePositionThisChord)
		m.append(closePositionNextChord)
		displayPart.append(m)

for i in range(0, len(sOnlyChords)-1):
	thisChord = sOnlyChords[i]
	nextChord = sOnlyChords[i+1]
	appendChordPairs(thisChord, nextChord)

keyA = key.Key('A')
for c in displayPart.recurse().getElementsByClass('Chord'):
    rn = roman.romanNumeralFromChord(c, keyA)
    c.addLyric(str(rn.figure))

for c in displayPart.recurse().getElementsByClass('Chord'):
    if c.lyric == 'III6':
        c.color = 'pink'
        for x in c.derivation.chain():
            x.color = 'pink'

for m in sChords.getElementsByClass('Measure'):
        k = m.analyze('key')
        print(k)

