
from music21 import *

note1 = note.Note("C4")
note1.duration.type = 'half'
note2 = note.Note("F#4")
note3 = note.Note("B-2")

stream1 = stream.Stream()
stream1.id = 'some notes'
stream1.append(note1)
stream1.append(note2)
stream1.append(note3)

biggerStream = stream.Stream()
note2 = note.Note("D#5")
biggerStream.insert(0, note2)
biggerStream.append(stream1)

#biggerStream.show('text')
#help(note.Note)

sBach = corpus.parse('bach/bwv57.8')

alto = sBach.parts[1]
excerpt = alto.measures(1, 8)

measureStack = sBach.measures(2,3)
#measureStack.show()

s = stream.Score(id= 'mainScore')
p0 = stream.Part(id= 'part0')
p1 = stream.Part(id= 'part1')

m01 = stream.Measure(number=1)
m01.append(note.Note('C', type="whole"))
m02 = stream.Measure(number=2)
m02.append(note.Note('D', type="whole"))
p0.append([m01, m02])

m11 = stream.Measure(number=1)
m11.append(note.Note('E', type="whole"))
m12 = stream.Measure(number=2)
m12.append(note.Note('F', type="whole"))
p1.append([m11, m12])

s.insert(0, p0)
s.insert(1, p1)

#for el in s.recurse().notes:
#	print(el.offset, el, el.activeSite)

#for el in s.flat:
#	print(el.offset, el, el.activeSite)

print(len(sBach.flat.notes))

