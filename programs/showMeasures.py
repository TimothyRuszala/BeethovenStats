from music21 import *
import JPa
import progs
import copy
import pprint



def showAllMeasuresInProg(progs):

	excerpt = stream.Score()
	excerpt.repeatAppend(stream.Part(), 4)
	excerpt.parts[2].append(clef.AltoClef())
	excerpt.parts[3].append(clef.BassClef())

	for mode in ["maj", "min"]:
		for key in progs[mode]:
			for tup in progs[mode][key]:
				mNumbStart = t[1][0]
				beatStart  = t[1][1]
				mNumbEnd = t[1][2]
				beatEnd = t[1][3]

				m = bigscore.excerptGood(mNumbStart, beatStart, mNumbEnd, beatEnd)
				
				for i in range(0, 4):
					if not m[i][0] in excerpt[i]:
						excerpt[i].append(m[i][0])
	excerpt.show('text')
	return excerpt

# for use with getStats.getCleanVLs(), where each line of the list is of th form: (RNtup, locationTup, genericIntervals)
def showProgList(cleanVLlist, mvt = None):
	excerpt = stream.Score()
	excerpt.repeatAppend(stream.Part(), 4)
	excerpt.parts[2].append(clef.AltoClef())
	excerpt.parts[3].append(clef.BassClef())

	x = 0
	limit = 10000000
	for item in cleanVLlist:
		for i in range(0, 4):
			t = item[1]			
			print("t:", t)
			print()
			mNumbStart = t[0]
			beatStart  = t[1]
			mNumbEnd = t[2]
			beatEnd = t[3]
			if mvt == None:
				mxlFile = t[4]
				bigscore = JPa.load(mxlFile)
			else:
				bigscore = mvt

			m = bigscore.excerpt(mNumbStart, mNumbEnd)

			m[i].flat.notes[0].lyric = str(mNumbStart) + " in " + str.split(bigscore.mvtString, '/')[-1] + str(item[2])
			
			
			if not m[i] in excerpt[i]:
				excerpt[i].append(copy.deepcopy(m[i]))

			if x >= limit:
				excerpt.show()
				return excerpt
		x += 1
		print("x:", x)

	excerpt.show()
	return excerpt


def showMeasuresWithRnProg(rnProg, progs, bigscore, mode = "maj"):

	excerpt = stream.Score()
	excerpt.repeatAppend(stream.Part(), 4)
	excerpt.parts[2].append(clef.AltoClef())
	excerpt.parts[3].append(clef.BassClef())


	for t in progs[mode][rnProg]:
		mNumbStart = t[1][0]
		beatStart  = t[1][1]
		mNumbEnd = t[1][2]
		beatEnd = t[1][3]

		m = bigscore.excerptGood(mNumbStart, beatStart, mNumbEnd, beatEnd)
		
		for i in range(0, 4):
			if not m[i][0] in excerpt[i]:
				excerpt[i].append(m[i][0])


	excerpt.show('text')
	return excerpt

def showMeasuresWithRnProgSimple(rnProg, progs, mode = "maj"):

	excerpt = stream.Score()
	excerpt.repeatAppend(stream.Part(), 4)
	excerpt.parts[2].append(clef.AltoClef())
	excerpt.parts[3].append(clef.BassClef())

	for i in range(0, 4):
		for t in progs[mode][rnProg]:
			mNumbStart = t[1][0]
			beatStart  = t[1][1]
			mNumbEnd = t[1][2]
			beatEnd = t[1][3]
			mxlFile = t[1][4]
			#pprint.pprint(t)

			bigscore = JPa.load(mxlFile)

			m = bigscore.excerpt(mNumbStart, mNumbEnd)
			
			#print(len(m[i].flat))
			#m[i].flat.show('text')

			m[i].flat.notes[0].lyric = str(mNumbStart) + " in " + str.split(bigscore.mvtString, '/')[-1]
			#m[0].notesAndRests[0].lyric = str(mNumbStart)
			# except:
			# 	print("tried to write" + str(mNumbStart))
			
			if not m[i] in excerpt[i]:
				excerpt[i].append(copy.deepcopy(m[i]))

	excerpt.show()
	return excerpt

def getRnProgNoInv(rnProg, sevenths = True):
	
	cleanRN1 = rnProg[0]
	cleanRN2 = rnProg[1]

	if sevenths:
		cleanRN1 = cleanRN1.replace('6/5', '7')
		cleanRN1 = cleanRN1.replace('4/3', '7')
		cleanRN1 = cleanRN1.replace('2', '7')

		cleanRN2 = cleanRN2.replace('6/5', '7')
		cleanRN2 = cleanRN2.replace('4/3', '7')
		cleanRN2 = cleanRN2.replace('2', '7')
		remove_digits = str.maketrans('', '', '012345689') # no 7

	else:
		remove_digits = str.maketrans('', '', '0123456789') # no 7

	cleanRN1 = cleanRN1.translate(remove_digits).replace('//', '/')
	if cleanRN1.endswith('/'):
		cleanRN1 = cleanRN1[0:-1]
	cleanRN2 = cleanRN2.translate(remove_digits).replace('//', '/')
	if cleanRN2.endswith('/'):
		cleanRN2 = cleanRN2[0:-1]
	res = (cleanRN1, cleanRN2)

	return res


def showMeasuresWithRnProgSimpleNoInv(rnProg, progs, mode = "maj", sevenths = True):

	rnProg = getRnProgNoInv(rnProg, sevenths)

	excerpt = stream.Score()
	excerpt.repeatAppend(stream.Part(), 4)
	excerpt.parts[2].append(clef.AltoClef())
	excerpt.parts[3].append(clef.BassClef())

	hitcounter = 0
	for rnpr in progs[mode]:
		# if hitcounter > 10:
		# 	break
		rnProgNoInv = getRnProgNoInv(rnpr, sevenths)
		if rnProgNoInv == rnProg:
			hitcounter += 1
			print("hitcounter:", hitcounter)
			print(rnpr, rnProgNoInv)
			for t in progs[mode][rnpr]:
				for i in range(0, 4):
					print("t:", t)
					print()
					mNumbStart = t[1][0]
					beatStart  = t[1][1]
					mNumbEnd = t[1][2]
					beatEnd = t[1][3]
					mxlFile = t[1][4]
					if mxlFile == None:
						print("break on ", rnpr)
						# mxlFile = "/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op127_no12_mov2_progs" # eh what da heeck
						break
					#pprint.pprint(t)

					#try:
					bigscore = JPa.load(mxlFile)
					# except:
					# 	print("well we tried:", rnpr)
					# 	continue


					m = bigscore.excerpt(mNumbStart, mNumbEnd)
					
					#print(len(m[i].flat))
					#m[i].flat.show('text')
					try:
						m[i].flat.notes[0].lyric = str(mNumbStart) + " in " + str.split(bigscore.mvtString, '/')[-1]
					except:
						print("something happened here")
					#m[0].notesAndRests[0].lyric = str(mNumbStart)
					# except:
					# 	print("tried to write" + str(mNumbStart))
					
					if not m[i] in excerpt[i]:
						excerpt[i].append(copy.deepcopy(m[i]))

	excerpt.show()
	return excerpt



def main():

	filename = "/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op18_no1_mov3"
	mvt = JPa.load(filename)

	giantProgDict = progs.Progs()
	giantProgDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorageMay7HopefullyGood")
	gp = giantProgDict.progs
	print("gp loaded")
	#pprint.pprint(gp)

	mvtProgDict = progs.Progs()
	mvtProgDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op127_no12_mov2_progs")
	pd = mvtProgDict.progs
	#pprint.pprint(pd)

	rnProg = ("IV", "I")

	showMeasuresWithRnProgSimpleNoInv(rnProg, gp, mode = "maj")


if __name__ == "__main__":
	main()



