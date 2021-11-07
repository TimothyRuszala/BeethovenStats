from music21 import *

def getLastChord(score):
	lastPitches = []
	for part in score.parts:
		lastPitch = part.pitches[-1]
		lastPitches.append(lastPitch)
	c = chord.Chord(lastPitches)
	c.duration.type = "whole"
	c.closedPosition(inPlace = True)
	return c

def isRelevant(score):
	c = getLastChord(score)
	if score.analyze('key').mode == 'major':
		return False
	elif c.isMajorTriad():
		return False
	elif c.root().name != score.analyze('key').tonic.name:
		return False
	else:
		return c


## MAIN
chorales = corpus.search('bach', fileExtensions = 'xml')
relevantStream = stream.Stream()
relevantStream.append(meter.TimeSignature('4/4'))
minorCount = 0

for chorale in chorales:
	cScore = chorale.parse()
	if cScore.analyze('key').mode == "minor":
		minorCount += 1
	falseOrChord = isRelevant(cScore)
	if falseOrChord:
		theChord = falseOrChord
		relevantStream.append(theChord)
		theChord.lyric = cScore.metadata.title
relevantStream.show()
print(minorCount)

	



# count = 0
# if (lastChord.isMajorTriad() == True) or lastChord.isIncompleteMajorTriad() == True:
# 	count += 1
# 	print(bwv10)
# print(finalChord)



# c1 = chorales[0].parse()
# c1chords = c1.chordify()
# for c in c1chords.flat.notes:
# 	c.closedPosition(inPlace = True)
# finalChord = c1chords.flat.notes[-1]
# c1chords.show()

# count = 0
# if (finalChord.isMajorTriad() == True) or finalChord.isIncompleteMajorTriad() == True:
# 	count += 1
# print(finalChord)
