from music21 import *


#s = converter.parse("tinyNotation: 4/4 C.4_doo D8~_dee D r c4_dah")
#s.show()

s = converter.parse("tinyNotation: 4/4 c4 trip{d=id2 e f} g")
n = s.recurse().getElementById('id2')
ch = chord.Chord('D4 F#4 A4')
ch.style.color = 'pink'
n.activeSite.replace(n, ch)
s.show()

tnc = tinyNotation.converter('6/8 e4. d8 c# d e2.')
tnc.parse()
j = tnc.stream()


