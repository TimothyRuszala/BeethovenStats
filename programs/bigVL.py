from music21 import *
import bigScore
import bigVoicing
import JPa

class BigVL():

	def __init__(self, bigVoicing1, bigVoicing2):
		self.bv1 = bigVoicing1
		self.bv2 = bigVoicing2
		self.globalKey = bigVoicing2.globalKey
		self.degree = (self.bv1.degree, self.bv2.degree)
		self.location = (bigVoicing2.mNumbStart, bigVoicing2.beatStart)
		self.start = (self.bv1.mNumbStart, self.bv1.beatStart)
		self.end = (self.bv2.mNumbStart, self.bv2.beatStart)
		self.span = (self.bv1.mNumbStart, self.bv1.beatStart, self.bv2.mNumbStart, self.bv2.beatStart)

	def getKey(self):
		return self.globalKey

	def hasNonChordTones(self):
		return self.bv1.hasNonChordTones()

	def hasOneVoiceToEachPart(self):
		return (self.bv1.hasOneVoiceToEachPart() and self.bv2.hasOneVoiceToEachPart())

	def rnTuple(self):
		return (self.bv1.rn, self.bv2.rn)

	def toString(self):
		return (self.bv1.toString(), self.bv2.toString())

	def toTransposedTupleTuple(self):
		return (self.bv1.transposeToC(), self.bv2.transposeToC())

	# where lower means more obvious
	def obviousness(self):
		# checks if we have a 1:1 correspondence between voices
		if self.bv1.hasOneVoiceToEachPart(numberOfParts = 4) and self.bv2.hasOneVoiceToEachPart(numberOfParts = 4):
			if self.bv1.nonChordTones == 0 and self.bv2.nonChordTones == 0:
				return 1
			else:
				return 2
		elif self.bv1.hasOneVoiceToEachPart(numberOfParts = 3) and self.bv2.hasOneVoiceToEachPart(numberOfParts = 3):
			if self.bv1.voicePerPartCounter() == self.bv2.voicePerPartCounter():
				if self.bv1.nonChordTones == 0 and self.bv2.nonChordTones == 0:
					return 1
				else:
					return 2

		# checks if we *could* have a 1:1 correspondence between 3 parts if we were to remove one of them
		bv1Simple = self.bv1.voicePerPartCounterSimple()
		bv1sLen = self.obviousnessHelperCheckSimpleTrueLength(bv1Simple)
		bv2Simple = self.bv2.voicePerPartCounterSimple()
		if bv1Simple == bv2Simple:
			if bv1sLen == 3:
				return 3
		return 4

		


	def obviousnessHelperCheckSimpleTrueLength(self, partVoiceCountListSimple):
		l = 0
		for i in partVoiceCountListSimple:
			if i != None:
				l += 1
		return l
	




# That's all for now!

def main():
	mvt = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no1_mov2")
	
	mvt.globalKey = key.Key('d')

	testBV1 = bigVoicing.BigVoicing(mvt, 'i', 107, 2, 108, 1.0)
	testBV2 = bigVoicing.BigVoicing(mvt, 'V7', 108, 1, 108, 2.0)

	print(testBV1.bv)
	print(testBV2.bv)

	testBVL = BigVL(testBV1, testBV2)
	print(testBVL.toString())
	print(testBVL.obviousness())
	print()

	mvt5 = JPa.load("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no5_mov1")
	mvt5.globalKey = key.Key('A')

	testBV3 = bigVoicing.BigVoicing(mvt5, "V7", 12, 1, 13, 1)
	print("testBV3 = BigVoicing(mvt5, 'V7', 12, 1, 13, 1)")
	print("testBV3.getChord():", testBV3.getChord())
	print("testBV3.nonChordTones (should be 2):", testBV3.nonChordTones)
	print("testBV3.hasOneVoiceToEachPart() (should be False):", testBV3.hasOneVoiceToEachPart())
	print("testBV3.degree:", testBV3.degree)
	print()
	testBV4 = bigVoicing.BigVoicing(mvt5, "I6", 13, 1, 14, 1)
	print("testBV4 = BigVoicing(mvt5, 'I6', 13, 1, 14, 1)")
	print("testBV4.getChord():", testBV4.getChord())
	print("testBV4.nonChordTones (should be 2):", testBV4.nonChordTones)
	print("testBV4.hasOneVoiceToEachPart() (should be False):", testBV4.hasOneVoiceToEachPart())
	print("testBV4.degree:", testBV4.degree)
	print()
	testBVL34 = BigVL(testBV3, testBV4)
	print("testBVL34 = BigVL(testBV3, testBV4)")
	print(testBVL34.toTransposedTupleTuple())
	print("testBVL34.obviousness():", testBVL34.obviousness())




if __name__ == "__main__":
	main()


