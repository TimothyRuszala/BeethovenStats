from music21 import *
c = converter.parse("Music/Beethoven Quartets/op18_no1_mov2.mxl")

s = "testString"
with s as f:
	data = f.read()
print(s[0])

