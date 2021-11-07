from music21 import *

bach = corpus.parse('bwv66.6')
lastNote = bach.recurse().getElementsByClass('Note')[-1]
print(lastNote)

count = 0
for e in bach.flat.notes:
	count += 1
print(count)

gloria = corpus.parse('luca/gloria')
soprano = gloria.parts[0]

lastTimeSignature = None
for n in soprano.flat.notes:
	thisTimeSignature = n.getContextByClass('TimeSignature')
	if thisTimeSignature is not lastTimeSignature:
		lastTimeSignature = thisTimeSignature
		# print (thisTimeSignature, n.measureNumber)

lastGloriaNote = soprano.flat.notes[-1]
for ts in lastGloriaNote.getAllContextsByClass("TimeSignature"):
	print(ts, ts.measureNumber)

# for cs in lastNote.contextSites():
# 	print(cs)

n = note.Note('C#5')
n.duration.type = "whole"
n.articulations = [articulations.Staccato(), articulations.Accent()]
n.lyric = 'hi!'
n.expressions = [expressions.Mordent(), expressions.Trill(), expressions.Fermata()]
# n.show()

splitTuple = n.splitAtQuarterLength(3.0)
s = stream.Stream()
s.append(splitTuple)

for thisSpanner in splitTuple.spannerList:
        s.insert(0, thisSpanner)
s.show()



