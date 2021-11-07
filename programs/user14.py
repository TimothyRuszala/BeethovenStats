from music21 import *

noteC = note.Note("C4", type="half")
noteD = note.Note("D4", type="quarter")
noteE = note.Note("E4", type="quarter")
noteF = note.Note("F4", type="half")

tsThreeFour = meter.TimeSignature('3/4')

# print(tsThreeFour.ratioString)

stream1 = stream.Stream()

for thing in [tsThreeFour, noteC, noteD, noteE, noteF]:
	stream1.append(thing)

#stream1.show()

stream2 = stream1.makeMeasures()
#stream2.show('text')

#tsThreeFour.ratioString = '2/4'
tsThreeFour.numerator = 6
tsThreeFour.denominator = 8
tsThreeFour.beatCount = 6
for n in stream1.notes:
	print(n, n.beatStr)

bach = corpus.parse('bach/bwv57.8')
print(bach.__class__)
alto = bach.parts['Alto']
#alto.show()

print(alto.recurse().getElementsByClass(meter.TimeSignature)[0])
print(alto.measure(1).timeSignature)

alto.measure(7).timeSignature = meter.TimeSignature('6/8')
alto.makeBeams(inPlace = True)
for n in alto.flat.notes:
        n.stemDirection = None
#alto.show()

newAlto = alto.flat.getElementsNotOfClass(meter.TimeSignature).stream()
newAlto.insert(0, meter.TimeSignature('2/4'))
newAlto.makeMeasures(inPlace=True)

newAltoFixed = newAlto.makeNotation()
newAltoFixed.show()

