from music21 import *

n = note.Note("A4")
s = stream.Stream()
s.id = "s!"
s.insert(n)
t = stream.Stream()
t.id = 'new_stream'
t.insert(4.0, n)

n.activeSite = s
n.offset = 2.0
# n.activeSite = t
# n.activeSite = s
print(n.activeSite)
