from music21 import *
import voicing
import pickle
import pprint

class Progs:

	# progs is dictionary of form {"maj" : {}, "min" : {}}
	def __init__(self):
		self.progs = {"maj" : {}, "min" : {}} # e.g.: progs["maj"][rnProgs][spec vls : freq]
											  # e.g.: progs["maj" : (rnProgs : (spec vls : freq))]

	def getProgs(self):
		return self.progs

	# returns a true flag for purposes of control flow
	def loadProgs(self, progsStorage):
		with open(progsStorage, 'rb') as infile:
			self.progs = pickle.load(infile)
		return "Progs Loaded"

	def dumpProgs(self, progsStorage):
		with open(progsStorage, 'wb') as outfile:
			pickle.dump(self.progs, outfile)
		return "Progs Dumped"

	

	# Example: progs["maj"][rnProgs][spec vls : freq]
	def addToProgsFAKE(self, newVL):
		return

	def is_non_zero_file(self, fpath):
		return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

	# rnProg is a two-element tuple. E.g.: ('i', 'V')
	# if inversions is any value, will also return all inversion of these chords
	# returns a dictionary
	# I think that something is broken...
	def searchForRnProg(self, rnProg, inversions = None):
		
		romanNumeral0 = roman.RomanNumeral(rnProg[0])
		rn0 = romanNumeral0.romanNumeral
		romanNumeral1 = roman.RomanNumeral(rnProg[1])
		rn1 = romanNumeral1.romanNumeral

		inversionListTriads = ('', '6', '6/4') 
		inversionListSevenths = ('7', '6/5', '4/3', '4/2')
		allRelevantProgs = {"maj" : {}, "min" : {}}
		if inversions is None:
			if rnProg in self.progs["maj"]:
				allRelevantProgs.append(progs["maj"][rnProg])
				#print(allRelevantProgs)
			if rnProg in self.progs["min"]:
				allRelevantProgs.append(progs["min"][rnProg])
				#print(allRelevantProgs)

		else: # counting inversions. Needs to take into account 9th chords, since they're there.
			if romanNumeral0.isTriad():
				for i in inversionListTriads:
					if romanNumeral1.isTriad():
						for j in inversionListTriads:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs["maj"] = self.progs["maj"][rnCheck]
							if rnCheck in self.progs["min"]:
								allRelevantProgs["min"] = self.progs["min"][rnCheck]
					elif romanNumeral1.isSeventh():
						for j in inversionListSevenths:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs["maj"] = self.progs["maj"][rnCheck]
							if rnCheck in self.progs["min"]:
								allRelevantProgs["min"] = self.progs["min"][rnCheck]

			elif romanNumeral0.isSeventh():
				for i in inversionListSevenths:
					if romanNumeral1.isTriad():
						for j in inversionListTriads:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs["maj"] = self.progs["maj"][rnCheck]
							if rnCheck in self.progs["min"]:
								allRelevantProgs["min"] = self.progs["min"][rnCheck]
					elif romanNumeral1.isSeventh():
						for j in inversionListSevenths:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs["maj"] = self.progs["maj"][rnCheck]
							if rnCheck in self.progs["min"]:
								allRelevantProgs["min"] = self.progs["min"][rnCheck]
		return allRelevantProgs

	def searchForRnProgBACKUP(self, rnProg, inversions = None):
		
		romanNumeral0 = roman.RomanNumeral(rnProg[0])
		rn0 = romanNumeral0.romanNumeral
		romanNumeral1 = roman.RomanNumeral(rnProg[1])
		rn1 = romanNumeral1.romanNumeral

		inversionListTriads = ('', '6', '6/4') 
		inversionListSevenths = ('7', '6/5', '4/3', '4/2')
		allRelevantProgs = []
		if inversions is None:
			if rnProg in self.progs["maj"]:
				allRelevantProgs.append(progs["maj"][rnProg])
				#print(allRelevantProgs)
			if rnProg in self.progs["min"]:
				allRelevantProgs.append(progs["min"][rnProg])
				#print(allRelevantProgs)

		else: # counting inversions. Needs to take into account 9th chords, since they're there.
			if romanNumeral0.isTriad():
				for i in inversionListTriads:
					if romanNumeral1.isTriad():
						for j in inversionListTriads:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs.append(self.progs["maj"][rnCheck])
							if rnCheck in self.progs["min"]:
								allRelevantProgs.append(self.progs["min"][rnCheck])
					elif romanNumeral1.isSeventh():
						for j in inversionListSevenths:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs.append(self.progs["maj"][rnCheck])
							if rnCheck in self.progs["min"]:
								allRelevantProgs.append(self.progs["min"][rnCheck])

			elif romanNumeral0.isSeventh():
				for i in inversionListSevenths:
					if romanNumeral1.isTriad():
						for j in inversionListTriads:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs.append(self.progs["maj"][rnCheck])
							if rnCheck in self.progs["min"]:
								allRelevantProgs.append(self.progs["min"][rnCheck])
					elif romanNumeral1.isSeventh():
						for j in inversionListSevenths:
							rnCheck = (rn0 + i, rn1 + j)
							if rnCheck in self.progs["maj"]:
								allRelevantProgs.append(self.progs["maj"][rnCheck])
							if rnCheck in self.progs["min"]:
								allRelevantProgs.append(self.progs["min"][rnCheck])
		return allRelevantProgs

	def searchForRnProgTest(self, rnProg, inversions = None):
		searchForRnProg(self, rnProg, inversions)
		#for relevantProg in allRelevantProgs:

	# Example: 
	def addToProgs(self, newVL, newBVL):
		mode = newVL.getKey().mode
		if mode == 'major':
			rnProg = newVL.rnTuple() 
			newVLstring = newVL.toTransposedTupleTuple()
			newBVLstring = newBVL.toTransposedTupleTuple()
			vlStrings = (newVLstring, newBVLstring)
			if rnProg not in self.progs["maj"]:
				self.progs["maj"][rnProg] = [(vlStrings, newVL.getRange(), newVL.filename, newVL.isSimple(), newVL.degree, newBVL.degree, newVL.getGenericIntervals(shouldSort = False))]
			else:
				self.progs["maj"][rnProg].append((vlStrings, newVL.getRange(), newVL.filename, newVL.isSimple(), newVL.degree, newBVL.degree, newVL.getGenericIntervals(shouldSort = False)))
		else:
			rnProg = newVL.rnTuple()
			newVLstring = newVL.toTransposedTupleTuple()
			newBVLstring = newBVL.toTransposedTupleTuple()
			vlStrings = (newVLstring, newBVLstring)
			if rnProg not in self.progs["min"]:
				self.progs["min"][rnProg] = [(vlStrings, newVL.getRange(), newVL.filename, newVL.isSimple(), newVL.degree, newBVL.degree, newVL.getGenericIntervals(shouldSort = False))]
			else:
				self.progs["min"][rnProg].append((vlStrings, newVL.getRange(), newVL.filename, newVL.isSimple(), newVL.degree, newBVL.degree, newVL.getGenericIntervals(shouldSort = False)))

	# Should have written this a loooong time ago... Would have saved me a lot of time. Combines individual prog dicts into one giant prog dict such that
	# I don't have to run the whole program (about 3 hrs) to get a complete dataset, but I can update it file by file.
	def combineProgs(self, smallProg):
		for mode in ["maj", "min"]:
			for rnProg in smallProg[mode]:
				for tup in smallProg[mode][rnProg]:
					if rnProg in self.progs[mode]:
						if tup not in self.progs[mode][rnProg]:
							self.progs[mode][rnProg].append(tup)
					else:
						self.progs[mode][rnProg] = smallProg[mode][rnProg]
		





def main():
	print("Testing combineProgs")
	testBigProg = Progs()

	p = Progs()
	p.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no1_mov4_progs")
	smallProg1 = p.progs
	testBigProg.combineProgs(smallProg1)
	print("smallLen:", len(smallProg1["maj"]))
	print("len:", len(testBigProg.progs["maj"]))


	p2 = Progs()
	p2.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no1_mov3_progs")
	smallProg2 = p2.progs
	testBigProg.combineProgs(smallProg2)
	print("smallLen:", len(smallProg2["maj"]))
	print("len:", len(testBigProg.progs["maj"]))


	giantProgs = Progs()
	giantProgs.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay7")
	giantProgsMay6 = Progs()
	giantProgsMay6.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay6")
	giantProgs.combineProgs(giantProgsMay6.progs)
	giantProgs.dumpProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay7HopefullyGood")

	oldGP = Progs()
	oldGP.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorage")
	print("len(oldGP.progs['maj']):", len(oldGP.progs["maj"]))
	print("len(newGP.progs['maj']):", len(oldGP.progs["maj"]))



	#pprint.pprint(testBigProg.progs)








if __name__ == "__main__":
	main()





