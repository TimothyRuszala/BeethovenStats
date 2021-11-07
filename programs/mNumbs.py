# INCOMPLETE PROGRAM, DOESN't RUN!

def getMeasureNumbers(filename):

#~~VARIABLES_AND_DICTIONARIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	mxlFile = filename + '.mxl'

#~~OPEN_FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# Extracting the analysis information
	with open(filename + '.txt', 'r') as rnFile:
		for i in range(4):
			rnFile.readline()
		timeSignatureLine = rnFile.readline().split()
		print(timeSignatureLine)
		#timeSignature = meter.TimeSignature(timeSignatureLine[2]) #FIX: what happens when there's a time signature change within the movement?
		rnFile.readline()
		# # Extracting the string parts
		# try:
		# 	movement = converter.parse(mxlFile)
		# except:
		# 	print(filename + " could not be opened")
		# 	return
		# mvt = bigScore.BigScore(movement, timeSignature, mxlFile = mxlFile)
		# print(mvt.mvtString)

#~~PARSE_BY_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		for line in rnFile:
			#print(line[0:])
			if line[0] == 'N': # i.e. "Note: ..."
				continue
			if line[0] == '\n' or line[0] == ' ':
				continue
			beatsChordsKeys = line.split()
			if beatsChordsKeys[0][0] == 'T': #i.e. "Time Signature: 4/4"
				print(beatsChordsKeys[0])
				continue
			mmStr = beatsChordsKeys[0]
			mNumb = int(mmStr[1:])
			print(mNumb)
			# in case a measure doesn't actually exist.
			if mvt.violin1.measure(mNumb) is None:
				continue
			currentBeat = None





def getListOfQuartetFilesWithoutExtensions():
	_MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	_MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'

	unfilteredFilelist = os.listdir(_MUSICPATH)
	fileList = []
	for file in unfilteredFilelist:
		if file[-1] == 't': #i.e. '.txt'
			fileList.append(_MUSICPATH + file[0:-4])

	return fileList

def getAllProgs():

	fileList = getListOfQuartetFilesWithoutExtensions()

	for file in reversed(fileList):
		print(file)
		# try:
		getProgs(file, load = False)
		# except:
		# 	print(file + "did not work for some reason.")
		# 	continue




# MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
def main():

	#getAllProgs()

	# _MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
	# _MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'
	# mvtString = "op18_no3_mov1"
	# filename = _MUSICPATH + mvtString
	# print(filename)

	# testProgs = getProgs(filename, load = False)

	getMeasureNumbers("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/op127_no12_mov2")



