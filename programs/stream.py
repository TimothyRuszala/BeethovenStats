from music21 import *

note1 = note.Note('C2')
note2 = note.Note('G4')
note3 = note.Note('B6')


note1.duration.type = "half"

notelist = [note1, note2]


stream1 = stream.Stream()
stream1.append(note1)
stream1.append(note2)
stream1.append(note3)

print(stream1.analyze("ambitus"))

print("/ ")



stream2 = stream.Stream()
n3 = note.Note('e-5')
stream2.repeatAppend(n3, 4)
stream2.show('text')

print("biggerStream")
biggerStream = stream.Stream()
n2 = note.Note("D#3")
biggerStream.insert(0, n2)
biggerStream.append(stream1)
stream1.id = "eggy!"
biggerStream.show("text")
