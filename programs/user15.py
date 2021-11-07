from music21 import *

ks2 = key.KeySignature(2)

print(ks2.alteredPitches)
print(ks2.accidentalByStep('C'))
print(ks2.accidentalByStep('E') is None)

ks4 = ks2.transpose('M2')
print(ks4.sharps)
ks4.sharps = 0
print(ks4.getScale('minor'))

m = stream.Measure()
m.insert(0, meter.TimeSignature('3/4'))
m.insert(0, ks2)
d = note.Note("D")
c = note.Note("C")
fis = note.Note("F#")
m.append([d, c, fis])

m1 = stream.Measure()
m1.timeSignature = meter.TimeSignature("2/4")
m1.keySignature = key.KeySignature(-5)
m1.append([note.Note("D"), note.Note("A")])
m2 = stream.Measure()
m2.append([note.Note("B-"), note.Note("G#")])
p = stream.Part()
p.append([m1, m2])


ks = m1.keySignature
for n in p.recurse().notes:
    nStep = n.pitch.step
    rightAccidental = ks.accidentalByStep(nStep)
    n.pitch.accidental = rightAccidental

#p.show()

kD = key.Key('D')
aMixy = key.Key('A', 'Mixolydian')
print(aMixy)

bach = corpus.parse('bwv66.6')
fis = bach.analyze("key")
print(fis.correlationCoefficient)
# bach.plot('key')

c = bach.chordify()
for n in c.notes:
    n.closedPosition(inPlace=True)
# c.show()

s = stream.Stream()
s.append(key.Key('D'))
s.append(note.Note('F', type='whole'))
s.append(key.Key('b-', 'minor'))
s.append(note.Note('F', type='whole'))
s2 = s.makeNotation()
#s2.show()

out = stream.Part()
for i in range(0, 8):
	pitchStream = converter.parse("tinyNotation: 4/4 c8 e d f e g f a g e f d c e c4")
	k = key.Key('C')
	pitchStream.measure(1).insert(0, k)
	k.transpose(i, inPlace = True)
	for n in pitchStream.recurse().notes:
		n.transpose(i, inPlace = True)
	for m in pitchStream:
		out.append(m)
out.show()

