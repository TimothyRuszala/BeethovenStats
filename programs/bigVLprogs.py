from music21 import *
import voicing
import bigScore
import bigVoicing
import bigVL
import pprint
import pickle

# A data structure which stores BigVL objects.
class BigVLprogs:

	# Progs is dictionary of form {"maj" : {}, "min" : {}}
	def __init__(self):
		self.progs = {} 

	# Loads progs. Returns a true flag for purposes of control flow
	def loadProgs(self, progsStorage):
		with open(progsStorage, 'rb') as infile:
			self.progs = pickle.load(infile)
		return "Progs Loaded"

	def dumpProgs(self, progsStorage):
		with open(progsStorage, 'wb') as outfile:
			pickle.dump(self.progs, outfile)
		return "Progs Dumped"

	# Example: progs[degree][span, BigVL]
	def addToProgs(self, newBigVL):
		bvlDegreeTuple = newBigVL.degree
		
		if bvlDegreeTuple not in self.progs:
			self.progs[bvlDegreeTuple] = [(newBigVL.rnTuple(), newBigVL.span, newBigVL.toString(), newBigVL.hasNonChordTones(), newBigVL.hasOneVoiceToEachPart())]
		else:
			self.progs[bvlDegreeTuple].append((newBigVL.rnTuple(), newBigVL.span, newBigVL.toString(), newBigVL.hasNonChordTones(), newBigVL.hasOneVoiceToEachPart()))

	def searchForSimpleBigVLs(self, mvt, degree = (4, 4), noNonChordTones = "Yes", oneVoiceForEachPart = "Yes"):
		vlStream = stream.Score()
		vlStream.repeatAppend(stream.Part(), 4)
		vlStream.parts[2].append(clef.AltoClef())
		vlStream.parts[3].append(clef.BassClef())
		relevantVLs = []

		for tup in self.progs[degree]:
			m = mvt.excerptGood(tup[1][0], tup[1][1], tup[1][2], tup[1][3])
			print(tup[1], tup[0], tup[2], tup[3])
			if noNonChordTones == "Yes":
				if tup[3] > 0:
					continue

			relevantVLs.append(tup)
			for i in range(0, 4):
				if not m[i][0] in vlStream[i]:
					vlStream[i].append(m[i][0])
		return (vlStream, relevantVLs)

def main():
	mvtString = "op18_no1_mov2"
	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	_QUARTET = _MUSICPATH + mvtString
	timeSignature = meter.TimeSignature('9/8')
	movement = converter.parse(_QUARTET + ".mxl")
	mvt = bigScore.BigScore(movement, timeSignature)
	mvt.globalKey = key.Key('d')
	bigVLprogs = BigVLprogs()

	testBV1 = bigVoicing.BigVoicing(mvt, 'i', 107, 2, 108, 1.0)
	testBV2 = bigVoicing.BigVoicing(mvt, 'V7', 108, 1, 108, 2.0)
	testBVL = bigVL.BigVL(testBV1, testBV2)

	bigVLprogs.addToProgs(testBVL)




if __name__ == "__main__":
	main()






