# import os
import operator
import os
import collections
import pickle
import copy
from music21 import *
import DT
import matplotlib.pyplot as plt
import rn

progs = [{}, {}]
locations = [{}, {}]
chorale = stream.Score()
analysis_path = DT._HUMANANALYSES

"""
progs[modeIndex][progStr][voiceLeadingStr] = count
modeIndex = 0 for major, 1 for minor
progStr = 'V7 -> I'
voiceLeadingStr = '[[0, 0], [4, 1], [7, 2]]' (PC, path) with PCs transposed to C major or C minor -- 0 2 4 5 7 9 11 are the major scale degrees
S indicates soprano voice, P indicates a 'filled-in third' with a passing tone

TODO: 
	- perhaps store locations?
	- trigrams, tetragrams, etc.
	
Currently, paths representing "filled-in thirds" are multiplied by 100, while the soprano has .5 added/subtracted to it. 
Could be a bit more systematic here.

"""

def gather_stats(source = 'BACH', fileName = '', includeBass = True):
	global progs, chorale, analysis_path, analyzed_file, globalSource, locations, locNames, OUCHReport, d5progs, a4progs
	globalSource = source.upper() # USED FOR FILENAMES
	progs = [{}, {}]
	d5progs = [{}, {}]
	a4progs = [{}, {}]
	locations = [{}, {}]
	locNames = {}
	OUCHReport = [{}, {}]
	if globalSource not in DT._PATHS:
		print("Source not found!")
		return
	analysisPath = DT._PATHS[globalSource][0]
	scorePath = DT._PATHS[globalSource][1]
	fileStr = globalSource
	files = os.listdir(analysisPath)
	recordResults = True
	counter = 1
	for myFile in files:
		if myFile[-3:] == 'txt':
			if fileName and myFile[:-3] != fileName: continue
			print('Analyzing', myFile)
			analyzed_file = converter.parse(analysisPath + myFile, format='romantext')
			for ext in ['.xml', '.krn', '.mxl']:
				try:
					chorale = converter.parse(scorePath + myFile.replace('.txt', ext))
					break
				except:
					pass
			dochorale(counter, includeBass)
			locNames[counter] = myFile[:-4]
			counter += 1
	if not fileName:
		outputFile = open(DT._DATAPATH + 'voiceleading' + fileStr +'.pkl', 'w+')
		pickle.dump(progs, outputFile)
		pickle.dump(locations, outputFile)
		pickle.dump(locNames, outputFile)
		pickle.dump(OUCHReport, outputFile)
		outputFile.close()
	return

def v(source = 'BACH'):
	global progs, globalSource, locations, locNames, OUCHReport
	globalSource = source.upper()
	with open(DT._DATAPATH + 'voiceleading' + globalSource +'.pkl', 'rb') as inputFile:
		progs = pickle.load(inputFile)
		try:
			locations = pickle.load(inputFile)
			locNames = pickle.load(inputFile)
			OUCHReport = pickle.load(inputFile) 
		except:
			pass

load('Bach')

def dochorale(n, useBass = False):								# FIX TO ACCOUNT FOR VOICE CROSSINGS IN BASS!!!!
	global progs, locations, chorale, analysis_path, analyzed_file, OUCHReport, d5progs, a4progs
	score = [chorale.parts[i].flat.getElementsByClass('Note') for i in range(len(chorale.parts))]
	if globalSource == "GOUDIMEL":
		tempPart = score[0]
		score[0] = score[1]
		score[1] = tempPart
	anal = analyzed_file[1].flat.getElementsByClass('RomanNumeral')
	for i in range(len(anal) - 1):
		RN = anal[i]
		nRN = anal[i+1]
		if RN.figure == '?' or nRN.figure == '?': continue
		myMeasure = analyzed_file[1].getElementsByOffset(RN.offset, RN.offset, includeEndBoundary = True, mustBeginInSpan = False)
		if not myMeasure: 
			mNumber = -1
		else:
			mNumber = myMeasure[0].number
		locList = [n, mNumber]
		RNpitches = RN.pitches
		RNoffset = RN.offset
		transpositionOffset = RN.key.tonic.pitchClass
		startPos = []
		endPos = []
		voiceLeading = []
		middlePitches = []
		allPaths = []
		nRNpitches = nRN.pitches
		nRNoffset = nRN.offset
		progStr = RN.figure + ' -> ' + nRN.figure
		worthContinuing = True
		firstChordSoprano = -1
		firstChordMaxNote = -1
		secondChordSoprano = -1
		secondChordMaxNote = -1
		firstChordPitches = []
		if useBass: 
			bottomVoice = len(chorale.parts)
		else:
			bottomVoice = len(chorale.parts) - 1
		for j in range(0, bottomVoice):	
			firstChordTone = False
			secondChordTone = False									
			p = score[j].getElementsByOffset(RNoffset + .01, RNoffset + RN.duration.quarterLength, includeEndBoundary = False, mustBeginInSpan = False)
			for myNote in p:
				if myNote.expressions:
					worthContinuing = False 
					break
			p = p.pitches
			np = score[j].getElementsByOffset(nRNoffset + .01, nRNoffset + nRN.duration.quarterLength, includeEndBoundary = False, mustBeginInSpan = False).pitches
			if (len(p) > 0 and len(np) > 0 and RN.key.mode == nRN.key.mode and RN.key.tonic == nRN.key.tonic):
				for k in reversed(range(0, len(p))):
					if p[k].pitchClass in [dummy.pitchClass for dummy in RNpitches]:
						firstPitch = p[k]
						firstChordPitches.append(firstPitch)
						startPos.append(firstPitch.midi)
						firstChordTone = True
						afterPitches = p[k+1:]
						if firstPitch.midi > firstChordMaxNote:
							firstChordMaxNote = firstPitch.midi
							firstChordSoprano = j
						break
				for k in range(0, len(np)):
					if np[k].pitchClass in [dummy.pitchClass for dummy in nRNpitches]:
						secondPitch = np[k]
						endPos.append(secondPitch.midi)
						secondChordTone = True
						prePitches = np[:k]
						if secondPitch.midi > secondChordMaxNote:
							secondChordMaxNote = secondPitch.midi
							secondChordSoprano = j
						break
				if firstChordTone and secondChordTone: 
					path = secondPitch.midi - firstPitch.midi
					allPaths.append(path)	
					middlePitches = afterPitches + prePitches								# multiply a path by 100 if it represents a filled-in
#					print(path, p, np, middlePitches
					if (abs(path) == 3 or abs(path) == 4) and len(middlePitches) == 1:		# third (to measure the obligatoriness of PTs)
						middlePath = secondPitch.midi - middlePitches[0].midi
						if (path < 0 and middlePath > -3 and middlePath < 0) or (path > 0 and middlePath < 3 and middlePath > 0):
							path = path * 100
					voiceLeading.append([firstPitch.pitchClass, path])
				else:
					worthContinuing = False
			else:
				voiceLeading.append(False)
				#worthContinuing = False					# this line gets only VLs where every voice is present
			if not worthContinuing:
				break
		if list(set(allPaths)) == [0] or len(allPaths) <= 1:
			worthContinuing = False
		if worthContinuing:
			if firstChordSoprano == secondChordSoprano and firstChordSoprano != -1:			# THIS CODE IS FOR WHEN OTHER VOICES HAVE THE SOPRANO; 
				if voiceLeading[firstChordSoprano][1] >= 0: 								# NEED ANALOGOUS CODE FOR THE BASS I THINK!
					voiceLeading[firstChordSoprano][1] += .5
				else: 
					voiceLeading[firstChordSoprano][1] -= .5
			voiceLeading = [x for x in voiceLeading if x != False]
			bassVoice = voiceLeading[-1]
			"""Now we normalize everything so that the tonic is C; we sort the upper voices"""
			voiceLeading = sorted([[(x[0] - transpositionOffset) % 12, x[1]] for x in voiceLeading[:-1]]) + [[(bassVoice[0] - transpositionOffset) % 12, bassVoice[1]]]
			voiceLeadingStr = str(voiceLeading)
			voiceLeadingStr = voiceLeadingStr.replace('.5', 'S')
			voiceLeadingStr = voiceLeadingStr.replace('00', 'P')
			print(progStr, voiceLeadingStr)
			OUCHRecord = False
			if len(startPos) == 4 and len(endPos) == 4:
				OUCHRecord = True
				OUCHStr = categorize_voicing(startPos[-2::-1]) + ' -> ' + categorize_voicing(endPos[-2::-1])
			if RN.key.mode == 'major':
				modeIndex = 0
			else:
				modeIndex = 1
			if (not OUCHRecord) and len(voiceLeading) == 4:
				print("PROBLEM", progStr, voiceLeading, startPos, endPos, locList)
			if progStr in progs[modeIndex]:
				if voiceLeadingStr in progs[modeIndex][progStr]:
					progs[modeIndex][progStr][voiceLeadingStr] += 1
					locations[modeIndex][progStr][voiceLeadingStr].append(locList)
					if OUCHRecord and OUCHStr in OUCHReport[modeIndex][progStr][voiceLeadingStr]:
						OUCHReport[modeIndex][progStr][voiceLeadingStr][OUCHStr] += 1
					else:
						if OUCHRecord:
							OUCHReport[modeIndex][progStr][voiceLeadingStr][OUCHStr] = 1
				else:
					progs[modeIndex][progStr][voiceLeadingStr] = 1
					d5progs[modeIndex][progStr][voiceLeadingStr] = 0						# comment out!
					a4progs[modeIndex][progStr][voiceLeadingStr] = 0						# comment out!
					locations[modeIndex][progStr][voiceLeadingStr] = [locList]
					OUCHReport[modeIndex][progStr][voiceLeadingStr] = {}
					if OUCHRecord:
						OUCHReport[modeIndex][progStr][voiceLeadingStr][OUCHStr] = 1
			else:
				progs[modeIndex][progStr] = {}
				d5progs[modeIndex][progStr] = {}
				a4progs[modeIndex][progStr] = {}
				progs[modeIndex][progStr][voiceLeadingStr] = 1
				d5progs[modeIndex][progStr][voiceLeadingStr] = 0
				a4progs[modeIndex][progStr][voiceLeadingStr] = 0
				locations[modeIndex][progStr] = {}
				locations[modeIndex][progStr][voiceLeadingStr] = [locList]
				OUCHReport[modeIndex][progStr] = {}
				OUCHReport[modeIndex][progStr][voiceLeadingStr] = {}
				if OUCHRecord:
					OUCHReport[modeIndex][progStr][voiceLeadingStr][OUCHStr] = 1
			if 'viio6 -> ' in progStr:
				if has_diminished_fifth(firstChordPitches):
					d5progs[modeIndex][progStr][voiceLeadingStr] += 1
				else:
					a4progs[modeIndex][progStr][voiceLeadingStr] += 1
				#print(progStr, [x.nameWithOctave for x in firstChordPitches], has_diminished_fifth(firstChordPitches))
	return		

def OUCHstats(mode = 'major'):
	global OUCHdict, OUCHprogs
	modeInd = int(mode[0:3].upper() == 'MIN')
	OUCHdict = collections.defaultdict(lambda: 0)
	OUCHprogs = collections.defaultdict(lambda: 0)
	for prog in OUCHReport[modeInd]:
		if prog.count('7') > 0 or prog.count('6/5') > 0 or prog.count('4/3') > 0 or prog.count('2') > 0:
			continue
		for vl in OUCHReport[modeInd][prog]:
			for item in OUCHReport[modeInd][prog][vl]:
				OUCHprogs[item] = OUCHprogs[item] + OUCHReport[modeInd][prog][vl][item]
				firstChord = item.split(' -> ')[0]
				OUCHdict[firstChord] = OUCHdict[firstChord] + OUCHReport[modeInd][prog][vl][item]

def OUCHfind(target = 'H -> C', mode = 'major'):
	global tempOut
	modeInd = int(mode[0:3].upper() == 'MIN')
	for prog in OUCHReport[modeInd]:
		if prog.count('7') > 0 or prog.count('6/5') > 0 or prog.count('4/3') > 0 or prog.count('2') > 0:
			continue
		for vl in OUCHReport[modeInd][prog]:
			for item in OUCHReport[modeInd][prog][vl]:
				if item == target:
					print(prog, vl, OUCHReport[modeInd][prog][vl][item])

def big_intervals(maxSize = 4, maxCounts = 1, printIt = False, mode = 'major'):
	global tempOut, tempOut2
	tempOut = {}
	tempOut2 = {}
	modeInd = int(mode[0:3].upper() == 'MIN')
	for prog in OUCHReport[modeInd]:
		if prog.count('7') > 0 or prog.count('6/5') > 0 or prog.count('4/3') > 0 or prog.count('2') > 0: continue
		for myVL in OUCHReport[modeInd][prog]:
			theVL = convert_VLstr(myVL)[:-1]
			theDists = [abs(x[1]) for x in theVL]
			finalDists = [x for x in theDists if x >= maxSize]
			if len(finalDists) >= maxCounts:
				for theForms in OUCHReport[modeInd][prog][myVL]:
					tempOut[theForms] = tempOut.setdefault(theForms, 0) + OUCHReport[modeInd][prog][myVL][theForms]
					if theForms == 'C -> C' or theForms == ['O -> O']:
						newStr = prog + ' ' + str(theVL)
						tempOut2[newStr] = tempOut2.setdefault(newStr, 0) + OUCHReport[modeInd][prog][myVL][theForms]
	denom = sum(tempOut.values())
	num = sum(tempOut2.values())
	if num + denom > 0:
		print(100.*num/(num+ denom))
	else:
		print(0)
	if printIt:
		DT.print_dict(tempOut, pct = True)
		DT.print_dict(tempOut2, pct = True)
		
def report(progStr, mode = 'major', includeBass = True, details = True, percent = False):		# give the voice leadings corresponding to a RN progression
	global progs, newDict, cleanDict
	if mode[0:3].upper() == 'MAJ': 
		modeIndex = 0
	else: 
		modeIndex = 1
	try:
		newDict = copy.deepcopy(progs[modeIndex][progStr])
	except:
		newDict = {}
		print("Not found")
	if not includeBass:
		tempDict = {}
		for address in newDict:
			noBass = trim_VLstr(address)
			tempDict[noBass] = tempDict.setdefault(noBass, 0) + newDict[address]
		newDict = tempDict
		print(newDict)
	cleanDict = {}
	vlAliases = {}
	for pair in newDict:
		vl = pair.replace('P', '').replace('S', '')									# probably a better way to do this [filter(pair.split)
		vl = str(convert_VLstr(vl)[0:-1])
		cleanDict[vl] = cleanDict.setdefault(vl, 0) + newDict[pair]
		if vl != pair and vl in vlAliases:
			vlAliases[vl].append(pair)
		else:
			if vl != pair: vlAliases[vl] = [pair]
	myList = sorted(cleanDict.iteritems(), key=operator.itemgetter(1), reverse = True)
	if percent:
		total = 0
		for name, count in myList:
			total += count
		for i in range(len(myList)):
			myList[i] = (myList[i][0], 100.0 * myList[i][1]/total)
	for thing in myList:
		print(thing)
		if thing[0] in vlAliases:
			aliases = vlAliases[thing[0]]
			for alias in aliases:
				if details: print('     ', alias, newDict[alias])
	return

def show(rnProg, vlString, mode = 'MAJ', RNs = True):				# show the scores containing a particular voice leading
	global output, locNames, globalSource, locations
	output = stream.Score()
	tempOutput = stream.Score()
	modeInd = (mode.upper()[:3] == 'MIN')
	lastChoraleNo = False
	for i in range(0, 4):
		tempOutput.append(stream.Part())
	try:
		locList = locations[modeInd][rnProg][vlString]							# check for key error
	except KeyError:
		print('Not found')
		return
	for instance in locList:
		measureList = instance[1:]
		if len(measureList) == 1:
			measureList = [measureList[0], measureList[0] + 1]
		else:
			measureList[-1] = measureList[-1] + 1
		header = str(locNames[instance[0]])+'m'+str(measureList[0])
		print('getting', locNames[instance[0]], measureList)
		if locNames[instance[0]] != lastChoraleNo:
			choraleNo = locNames[instance[0]]
			lastChoraleNo = choraleNo
			try:
				chorale = converter.parse(DT._PATHS[globalSource][1] + choraleNo + '.xml')
			except:
				chorale = converter.parse(DT._PATHS[globalSource][1] + choraleNo + '.krn')
		if RNs: 
			analyzed_file = converter.parse(DT._PATHS[globalSource][0] + choraleNo + '.txt', format='romantext')
			DT.add_roman(chorale, analyzed_file, measureList[0], measureList[1])
		tempChorale = copy.deepcopy(DT.get_measures(chorale, measureList[0], measureList[1]))
		DT.insert_text(tempChorale.parts[0][0], header, 55, 0)
		output = DT.append(tempChorale, output)
	output = DT.fix_roman_placement(output)
	for p in output.parts:
		for item in p.flat:
			if 'Note' in item.classes: item.lyrics = []
	output.show()
	return output


def kurtosis(mode = 'major'):								# should calculate this correctly; right now it's just the pct. of VLs
	global progs											# taken up by the most popular form
	newProgs = {}
	if mode[0:3].upper() == 'MAJ':
		modeIndex = 0
	else:
		modeIndex = 1
	for progStr in progs[modeIndex]:
		myList = sorted(progs[modeIndex][progStr].iteritems(), key=operator.itemgetter(1), reverse = True)
		total = 0
		for name, count in myList:
			total += count
		for i in range(len(myList)):
			myList[i] = (myList[i][0], 100.0 * myList[i][1]/total)
		if total > 50: 
			"""print(progStr, myList)
			break"""
			newProgs[progStr] = myList[0][1]
	finalProgs = sorted(newProgs.iteritems(), key=operator.itemgetter(1), reverse = True)
	for thing in finalProgs:
		print(thing)
	return

def convert_VLstr(t):			# convert to ints
	t = filter(lambda x: x in '-]SP ' or x.isdigit(), t)
	t = t.replace(']]','').split('] ')
	convert_VLstr.PSlist = []
	output = []
	for u in t:
		PSstr = ''
		if 'P' in u:
			PSstr = 'P'
		if 'S' in u:
			PSstr += 'S'
		u = u.replace('P', '').replace('S', '')
		convert_VLstr.PSlist.append(PSstr)
		u = u.split()
		l = []
		for v in u: l.append(int(v))
		output.append(l)
	return output

nf_progs = [{}, {}]

def convert_to_normal_form():
	for modeInd in [0, 1]:
		for myProg in progs[modeInd]:
			nf_progs[modeInd][myProg] = {}
			for myVL in progs[modeInd][myProg]:
				newVL = convert_VLstr(myVL)
				#if myProg == 'IV -> I': print('     ',  newVL)
				myChord = [x[0] for x in newVL]
				nfChord = DT.normal_form(myChord)
				transp = DT.normal_form.transposition
				#if myProg == 'IV -> I': print('     ',  transp)
				newVL = [[(x[0] + transp) % 12, x[1]] for x in newVL]
				#if myProg == 'IV -> I': print('     ',  newVL)
				for i, x in enumerate(newVL):
					if 'P' in convert_VLstr.PSlist[i]:
						x[1] *= 100
					if 'S' in convert_VLstr.PSlist[i]:
						x[1] += .5
				sortedVL = sorted(newVL[:-1], key = lambda x: x[0]) + newVL[-1:]
				#if myProg == 'IV -> I': print('     ', sortedVL)
				strVL = str(sortedVL)
				strVL = strVL.replace('00', 'P').replace('.5', 'S')
				nf_progs[modeInd][myProg][strVL] = progs[modeInd][myProg][myVL]

def trim_VLstr(t):					# remove the bass
	t = t.replace(']]',']').replace('[[', '[').split('],')
	output = '['
	for u in range(0, len(t) - 1):
		output = output + t[u] + '],'
	return output[:-1] + ']'


def reduce_VL(myList):
	for pair in myList:
		if abs(pair[1]) > 99: pair[1] /= 100
	return myList

def grab(progStr, modeIndex = 0):
	global progs
	includeBass = False
	try:
		newDict = copy.deepcopy(progs[modeIndex][progStr])
	except:
		newDict = {}
		print(progStr, "no voice leadings found !!!")
	if not includeBass:
		tempDict = {}
		for address in newDict:
			noBass = trim_VLstr(address)
			tempDict[noBass] = tempDict.setdefault(noBass, 0) + newDict[address]
		newDict = tempDict
	cleanDict = {}
	vlAliases = {}
	for pair in newDict:
		vl = pair.replace('P', '').replace('S', '')									# probably a better way to do this [filter(pair.split)
		vl = str(convert_VLstr(vl)[0:3])
		cleanDict[vl] = cleanDict.setdefault(vl, 0) + newDict[pair]
		if vl != pair and vl in vlAliases:
			vlAliases[vl].append(pair)
		else:
			if vl != pair: vlAliases[vl] = [pair]
	myList = sorted(cleanDict.iteritems(), key=operator.itemgetter(1), reverse = True)
	if percent:
		total = 0
		for name, count in myList:
			total += count
		for i in range(len(myList)):
			myList[i] = (myList[i][0], 100.0 * myList[i][1]/total)
	for thing in myList:
		print(thing)
		if thing[0] in vlAliases:
			aliases = vlAliases[thing[0]]
			for alias in aliases:
				print('     ', alias, newDict[alias])
	return

def efficient(progStr, mode = 'major', percent = False, completeOnly = True, mostPopular = False, topTwo = True, printOut = True):
	global progs
	if type(mode) is str:
		modeIndex = int(mode[0:3].upper() == 'MIN')
	else:
		modeIndex = mode
	if modeIndex == 0:
		myKey = key.Key('C')
	else:
		myKey = key.Key('c') 
	if progStr not in progs[modeIndex]:
		return (0, 0)
	newDict = copy.deepcopy(progs[modeIndex][progStr])
	if mostPopular:
		temp = DT.sort_dict(newDict)[0]
		newDict = {temp[0]: temp[1]}
	newProgs = progStr.split(' -> ')
	chords = [roman.RomanNumeral(x, myKey).pitches for x in newProgs]
	if len(chords[0]) != len(chords[1]): 
		return (0, 0)
	midi0 = [x.midi for x in chords[0]]
	midi1 = [x.midi for x in chords[1]]
	bestVL = DT.vl_normal_form(DT.minimum_vl(midi0, midi1))			# deal with multiple bests here!
	secondBest = DT.vl_normal_form(DT.minimum_vl.fullList[1][0])
	maxEfficient = 0
	total = 0
	for pair in newDict:
		vl = pair.replace('P', '').replace('S', '')									# probably a better way to do this [filter(pair.split)
		vl = DT.vl_normal_form(convert_VLstr(vl))
		PCs = [x[0] for x in vl]
		incomplete = False
		if completeOnly:
			for myVoice in bestVL:
				if myVoice[0] not in PCs:
					incomplete = True
					break
			if incomplete:
				continue
		total += newDict[pair]
		problem = False
		for myVoice in bestVL:
			if myVoice not in vl:
				problem = True
				break
		if not problem:
			maxEfficient += newDict[pair]
		else:
			if topTwo:
				problem = False
				for myVoice in secondBest:
					if myVoice not in vl:
						problem = True
						break
				if not problem:
					maxEfficient += newDict[pair]
		if problem and printOut:
			print(pair, newDict[pair])
	#print(maxEfficient, total)
	return maxEfficient, total

def count_efficient(mode = 'major', sevenths = False, mostPopular = False, topTwo = False):
	modeIndex = int(mode[0:3].upper() == 'MIN')
	if modeIndex == 0:
		diatonicChords = DT._DIATONICMAJOR
	else:
		diatonicChords = DT._DIATONICMINOR
	efficientCount = 0
	total = 0
	for chord1 in diatonicChords:
		if not sevenths:
			parsed1 = DT.parse_figure(chord1)
			if parsed1[1] in ['7', '6/5', '4/3', '2']:
				continue
		for chord2 in diatonicChords:
			if not sevenths:
				parsed2 = DT.parse_figure(chord2)
				if parsed2[1] in ['7', '6/5', '4/3', '2']:
					continue
			if mostPopular:
				parsed1 = DT.parse_figure(chord1)
				parsed2 = DT.parse_figure(chord2)
				if parsed1[0] == parsed2[0]: 
					continue
			progStr = chord1 + ' -> ' + chord2
			results = efficient(progStr, modeIndex, mostPopular = mostPopular, topTwo = topTwo, printOut = False)
			if not results: continue
			if mostPopular and results[0] == 0:
				print(progStr)
			efficientCount += results[0]
			total += results[1]
	print(efficientCount, total, 100.*efficientCount/total)
	
def scalar_transps(first, second):							# list of integers
	fullList = []
	firstPCs = sorted([p % 12 for p in first])
	secondPCs = sorted([p % 12 for p in second])
	for i in range(0, len(firstPCs)):
		secondPCs = secondPCs[-1:] + secondPCs[:-1]
		newPaths = []
		for i in range(0, len(firstPCs)):
			path = (secondPCs[i] - firstPCs[i]) % 12
			if path > 6: 
				path -= 12
			newPaths.append([firstPCs[i], path])
		size = sum([abs(x[1]) for x in newPaths])		# L1 distance here
		fullList.append([newPaths, size])
	fullList = sorted(fullList, key = operator.itemgetter(1))
	return fullList

def scalar_report(progStr, mode = 'major', includeBass = True, percent = False):		# which scalar transpositions are used
	global progs, results
	modeIndex = int(mode[0:2].upper() == 'MI')
	try:
		newDict = copy.deepcopy(progs[modeIndex][progStr])
	except:
		newDict = {}
		print("Not found")
	if not includeBass:
		tempDict = {}
		for address in newDict:
			noBass = trim_VLstr(address)
			tempDict[noBass] = tempDict.setdefault(noBass, 0) + newDict[address]
		newDict = tempDict
		print(newDict)
	cleanDict = {}
	vlAliases = {}
	for pair in newDict:
		vl = pair.replace('P', '').replace('S', '')									# probably a better way to do this [filter(pair.split)
		vl = str(convert_VLstr(vl)[0:-1])
		cleanDict[vl] = cleanDict.setdefault(vl, 0) + newDict[pair]
		if vl != pair and vl in vlAliases:
			vlAliases[vl].append(pair)
		else:
			if vl != pair: vlAliases[vl] = [pair]
	myList = sorted(cleanDict.iteritems(), key=operator.itemgetter(1), reverse = True)
	if percent:
		total = 0
		for name, count in myList:
			total += count
		for i in range(len(myList)):
			myList[i] = (myList[i][0], 100.0 * myList[i][1]/total)
	results = {}
	violators = 0
	passers = 0
	for thing in myList:
		thePitches = convert_VLstr(thing[0])
		firstChord = list(set([x[0] for x in thePitches]))
		secondChord = list(set([sum(x) % 12 for x in thePitches]))
		if len(firstChord) != 3 or len(secondChord) != 3: continue
		possibilities = scalar_transps(firstChord, secondChord)
		for i, st in enumerate(possibilities):
			st = st[0]
			if st == thePitches:
				myStr = str(st)
				results[myStr] = results.setdefault(myStr, 0) + thing[1]
				if i == 2 and possibilities[0][1] !=0: 
					violators += thing[1]
					print("FOUND ONE!!!!", thing)
				else:
					passers += thing[1]
	#DT.print_dict(results)
	return violators, passers

RNpcs = [{}, {}]
results = {}
crossFactBass = {}
CandH = {}
tempDict = {}

def full_report(progStr, mode = 'major', printOut = True, reset = True, lookFor = "CROSS_FACT_BASS "):										# which voice leadings are used
	global progs, results, RNpcs, tempDict
	modeIndex = int(mode[0:2].upper() == 'MI')
	myKeys = [key.Key('C'), key.Key('c')]
	theSyms = progStr.split(' -> ')
	for myChord in theSyms:
		if myChord not in RNpcs[modeIndex]:
			RNpcs[modeIndex][myChord] = set(roman.RomanNumeral(myChord, myKeys[modeIndex]).pitchClasses)
	try:
		newDict = copy.deepcopy(progs[modeIndex][progStr])
	except:
		newDict = {}
		print("Not found")
	cleanDict = {}
	vlAliases = {}
	for pair in newDict:
		vl = pair.replace('P', '').replace('S', '')									# probably a better way to do this [filter(pair.split)
		vl = str(convert_VLstr(vl))
		cleanDict[vl] = cleanDict.setdefault(vl, 0) + newDict[pair]
	myList = sorted(cleanDict.iteritems(), key=operator.itemgetter(1), reverse = True)
	if reset:
		results = {}
	violators = 0
	passers = 0
	totals = 0
	found = 0
	for thing in myList:
		totals += thing[1]
		thePitches = convert_VLstr(thing[0])
		firstChord = set([x[0] for x in thePitches])
		if len(firstChord) != len(RNpcs[modeIndex][theSyms[0]]): continue
		secondChord = set([sum(x) % 12 for x in thePitches])
		if len(secondChord) != len(RNpcs[modeIndex][theSyms[1]]): continue
		if len(firstChord) != 3 or len(secondChord) != 3 or len(thePitches) != 4: continue					# four-voice triadic VLs only
		myKey = categorize_voice_leading(thePitches)
		results[myKey] = results.setdefault(myKey, 0) + thing[1]
		topPitches = thePitches[:-1]
		myStr = closed_and_open(topPitches)
		CandH[myStr] = CandH.setdefault(myStr, 0) + thing[1]
		if myKey == lookFor:
			crossFactBass[thing[0]] = crossFactBass.setdefault(thing[0], 0) + thing[1]
			tempDict[myStr] = tempDict.setdefault(myStr, 0) + thing[1]
		#print("CROSSINGS", thePitches, thing[1])
	finalResults = {}
	for item in results:
		newKey = item.split()[0]
		finalResults[newKey] = finalResults.setdefault(newKey, 0) + results[item]
	if printOut: DT.print_dict(finalResults, pct = True)
	return

def strongly_crossing_free(myVL):
	tempVL = sorted(myVL, key = operator.itemgetter(0, 1))
	outPCs = [sum(x) for x in tempVL]
	if (outPCs[-1] - outPCs[0]) > 12: return False
	if outPCs != sorted(outPCs): return False
	return True

def vl_search(mode = 'major', thresh = 1, lookFor = "CROSS_FACT_BASS "):						# USE THIS!  searches all the voice leadings in a composer's music
	global progs, results, tempDict
	results = {}
	CandH = {}
	tempDict = {}
	modeIndex = int(mode[0:2].upper() == 'MI')
	for myProg in progs[modeIndex]:
		if sum(progs[0][myProg].values()) > thresh:
			full_report(myProg, mode=mode, printOut = False, reset=False, lookFor = lookFor)
	DT.print_dict(results, pct=True)

def categorize_voice_leading(thePitches):
	topPitches = thePitches[:-1]
	firstChord = set([x[0] for x in thePitches])
	secondChord = set([sum(x) % 12 for x in thePitches])
	if len(firstChord) < 3 or len(secondChord) < 3:
		return "INC "
	elif len(firstChord) > 3 or len(secondChord) > 3:
		return "SEVENTH "
	possibilities = scalar_transps(firstChord, secondChord)
	for i, st in enumerate(possibilities):
		st = st[0]
		if st == topPitches:
			myStr = str(st)
			return "ST " + str(i)										# Scalar Transposition
	thePathSet = set([str(p) for p in thePitches])
	for i in range(3):
		st = set([str(p) for p in possibilities[i][0]])
		if st <= thePathSet:
			return "ST+B " + str(i)									# scalar transposition involving the bass
	#print(thePitches, strongly_crossing_free(thePitches))
	firstChord = set([x[0] for x in topPitches])
	secondChord = set([sum(x) % 12 for x in topPitches])
	if len(firstChord) == 3 and len(secondChord) == 3:
		return "CROSS_FACT_UPPER "											# upper-voice factorizable with crossings
	if strongly_crossing_free(thePitches):
		return "UNFACT "												# four voice unfactorizable
	for i in [1, 2, 3]:
		testPitches = thePitches[:i] + thePitches[i+1:]
		firstChord = set([x[0] for x in testPitches])
		secondChord = set([sum(x) % 12 for x in thePitches])
		if len(firstChord) == 3 and len(secondChord) == 3:
			return "CROSS_FACT_BASS "											# factorizable crossings involving the bass
	return "CROSS "													# unfactorizable crossings

def VL_string_to_chords(vlString):
	return [[x[0] for x in vlString], [sum(x) for x in vlString]]
	
def score_VL(vlString):
	firstChord, secondChord = VL_string_to_chords(vlString)
	theStr = categorize_voicing(firstChord) + ' -> ' + categorize_voicing(secondChord)
	theScore = score_VLstr(theStr)
	return [theStr, theScore]

def closed_and_open(vlString):
	bestVL, bestScore = score_VL(vlString)
	tempVL = copy.deepcopy(vlString)
	for i in range(1, len(vlString)):
		tempVL = tempVL[1:] + [[tempVL[0][0] + 12, tempVL[0][1]]]
		secondVL = [tempVL[0], tempVL[2], [tempVL[1][0] + 12, tempVL[1][1]]]
		for testVL in [tempVL, secondVL]:
			testString, testScore = score_VL(testVL)
			if testScore < bestScore: 
				bestScore = testScore
				bestVL = testString
	return bestVL
	
def categorize_voicing(pitchList):
	if pitchList[0] < pitchList[1] < pitchList[2]:
		if pitchList[2] == pitchList[0] + 12: return 'H'
		elif pitchList[2] - pitchList[0] < 12: return 'C'
		elif pitchList[0] < pitchList[2] - 12 < pitchList[1] and (pitchList[1] - pitchList[0]) < 12: return 'O'
		elif (pitchList[0] + 12 == pitchList[1] or pitchList[1] + 12 == pitchList[2]) and (pitchList[2] - pitchList[0]) < 24: return 'OCT+'
	elif (pitchList[0] == pitchList[1] or pitchList[1] == pitchList[2]) and (pitchList[2] - pitchList[0]) < 12: return 'DI'
	return '?'

def score_VLstr(theStr):
	score = 0
	score += theStr.count("O")
	score += theStr.count("DI") * 5
	score += theStr.count("OCT+") * 5
	score += theStr.count("?") * 100
	return score
	
	
def scalar_search(mode = 'major', thresh = 25):
	global progs, results
	violators = 0
	passers = 0
	results = {}
	modeIndex = int(mode[0:2].upper() == 'MI')
	if modeIndex == 0:
		c = key.Key('C')
	else:
		c = key.Key('c')
	for myProg in progs[modeIndex]:
		if sum(progs[0][myProg].values()) > thresh:
			v, p = scalar_report(myProg, mode = mode)
			if v != 0: print("    ", myProg)
			violators += v
			passers += p
	print(violators, passers)
	DT.print_dict(results)

rnPitchDict = {}

def fix_pitchlist(myPitches):
	while min(myPitches) > 12:
		myPitches = [x - 12 for x in myPitches]
	return myPitches

def generate_voicings(rn, format):
	outList = []
	myKey = key.Key('C')
	if rn in rnPitchDict:
		myPitches = rnPitchDict[rn]
	else:
		myPitches = fix_pitchlist([x.midi for x in roman.RomanNumeral(rn, myKey).pitches])
		rnPitchDict[rn] = myPitches
	myBass = myPitches[0]
	if format == 'H':
		outList.append([myBass] + myPitches[1:3] + [myPitches[1] + 12])
		outList.append([myBass] + [myPitches[2]] + [myPitches[1] + 12] + [myPitches[2] + 12])
		return outList
	if format == 'C':
		outList.append([myBass] + myPitches)
		outList.append([myBass] + myPitches[1:] + [myPitches[0] + 12])
		outList.append([myBass] + [myPitches[2]] + [myPitches[0] + 12] + [myPitches[1] + 12])
		return outList
	if format == 'O':
		for item in generate_voicings(rn, 'C'):
			outList.append(item[0:2] + [item[3], item[2] + 12])
		return outList
	if format == 'OCT+':
		for item in generate_voicings(rn, 'H'):
			outList.append(item[0:2] + [item[1] + 12, item[2] + 12])
			outList.append([item[0]] + [item[2], item[3], item[3] + 12])
		return outList
	if format == 'DI':
		for item in generate_voicings(rn, 'H'):
			outList.append(item[0:2] + [item[1], item[2]])
			outList.append([item[0]] + [item[2], item[3], item[3]])
		return outList

def VLsize(pitchList1, pitchList2):
	minsize = 100000
	if len(pitchList1) != len(pitchList2): return False
	while min(pitchList1) < max(pitchList2):
		pitchList1 = [x + 12 for x in pitchList1]
	while max(pitchList1) > min(pitchList2):
		newsize = sum([abs(pitchList1[x] - pitchList2[x]) for x in range(len(pitchList1))])
		if newsize < minsize: minsize = newsize
		pitchList1 = [x - 12 for x in pitchList1]
	return minsize

def best_VL(rnProg, formatProg, startPos, sopVoice):
	global secondSizes
	outDict = {}
	rn1, rn2 = rnProg.split(' -> ')
	format1, format2 = formatProg.split(' -> ')
	firstList = generate_voicings(rn1, format1)
	outList = []
	if format1 in ['DI', 'H', 'OCT+']:
		for i in reversed(range(len(firstList))):
			offset = firstList[i][0]
			tempList = [(x - offset) % 12 for x in firstList[i]]
			if sorted(tempList[1:]) == sorted(startPos[:-1]):
				outList.append(firstList[i])
		firstList = outList
		#print("  HERE", rnProg, formatProg, firstList, startPos)
	secondList = generate_voicings(rn2, format2)
	c1 = []
	secondSizes = []
	if format1 in ['C', 'O'] and format2 in ['DI', 'H', 'OCT+']:
		newSecondList = generate_voicings(rn2, 'H')
		for c1 in firstList:
			if (c1[0] - c1[-1]) % 12 == sopVoice:
				#print(c1, sopVoice)
				break
		#print("    ", rnProg, formatProg, sopVoice, [x % 12 for x in c1])
		c1 = fix_pitchlist(c1[1:])
		for c2 in newSecondList:
			c2 = fix_pitchlist(c2[1:])
			secondSizes.append(VLsize(c1, c2))
		secondSizes = sorted(secondSizes)									# gotta put something here!!! use only the inversion with the right voice in the top
	for c1 in firstList:
		c1 = fix_pitchlist(c1[1:])
		for c2 in secondList:
			c2 = fix_pitchlist(c2[1:])
			i = VLsize(c1, c2)
			if i in outDict:
				outDict[i].append([c1, c2])
			else:
				outDict[i] = [[c1, c2]]
	return outDict

def check_efficiency(mode = 'major', pct = True):
	global formatEfficiency
	modeInd = int(mode[0:3].upper() == 'MIN')
	formatEfficiency = {}
	OUCHstats()
	for myProg in OUCHReport[modeInd]:
		if myProg.count("7") > 0 or myProg.count("6/5") > 0 or myProg.count("4/3") > 0 or myProg.count("2") > 0: continue
		#if myProg.count("V6") > 0: continue			# GET RID OF THIS!!!!
		test_prog(myProg, mode)
	theKeys = sorted(formatEfficiency.keys(), key = lambda x: -sum(formatEfficiency[x].values()))
	if pct:
		for item in theKeys:
			total = 1.0 * sum(formatEfficiency[item].values())
			for instance in formatEfficiency[item]:
				formatEfficiency[item][instance] = int((100.0 * formatEfficiency[item][instance] / total) + .5)
	for item in theKeys:
		print(item, formatEfficiency[item])

#OUCHstats()

def test_prog(prog = 'V -> I', mode = 'major'):
	global formatEfficiency
	modeInd = int(mode[0:3].upper() == 'MIN')
	for myVL in OUCHReport[modeInd][prog]:
		#print("testing", myVL)
		convertedVL = convert_VLstr(myVL)
		mySize = sum([abs(x[1]) for x in convertedVL[:-1]])
		myCounts = sum(OUCHReport[modeInd][prog][myVL].values())
		myTemplate = ''
		for item in OUCHReport[modeInd][prog][myVL]:
			if item.count('?') == 0:
				myTemplate = item
				break
		if not myTemplate: continue
		startPos = [(x[0] - convertedVL[-1][0]) % 12 for x in convertedVL]
		findSop = myVL.split('],')
		for i in range(0, 4):
			if findSop[i].count("S") > 0:
				break
		sopVoice = (convertedVL[i][0] - convertedVL[-1][0]) % 12
		outDict = best_VL(prog, myTemplate, startPos, sopVoice)
		sizes = sorted(outDict.keys())
		if mySize in sizes:
			howEfficient = sizes.index(mySize) + 1
			for item in OUCHReport[modeInd][prog][myVL]:
				if item.count('?') == 0:
					if item == 'C -> DI' and howEfficient >= 2:
						print(" ", prog, "\t \t", myVL, "\t \t", OUCHReport[modeInd][prog][myVL][item], "\t", sizes)
						if mySize in secondSizes:
							#print(" ", secondSizes.index(mySize) + 1 )
							howEfficient = secondSizes.index(mySize) + 1
					if item not in formatEfficiency:
						formatEfficiency[item] = {}
					formatEfficiency[item][howEfficient] = formatEfficiency[myTemplate].setdefault(howEfficient, 0) + OUCHReport[modeInd][prog][myVL][item]
					"""if item == 'C -> H' and howEfficient == 2:
						print(prog, convertedVL, OUCHReport[modeInd][prog][myVL][item]"""
			#print(convertedVL[:-1], mySize, myCounts, myTemplate, sizes.index(mySize) + 1, sizes

def OUCHtables(trim = True):
	global outDict
	outDict = {}
	for item in OUCHprogs:
		if item.count("?") > 0: continue
		label = item.split(' -> ')[0]
		if label in outDict:
			outDict[label][item] = OUCHprogs[item]
		else:
			outDict[label] = {}
			outDict[label][item] = OUCHprogs[item]
	if trim:
		for item in outDict:
			mySum = sum(outDict[item].values())
			for thing in outDict[item].keys():
				if (100. * outDict[item][thing]) / mySum < 5:
					del outDict[item][thing]
	for item in outDict:
		myMin = float(min(outDict[item].values()))
		for thing in outDict[item].keys():
			outDict[item][thing] = int((outDict[item][thing] / myMin) + .5)
	for item in outDict:
		print("STARTPOS", item)
		DT.print_dict(outDict[item], pct=False)

# def contains(progList, findStr, mode = 'major', printIt = True, percent = True, noS = False):	# check what percentage of voice-leadings for a given progression contains a certain string
# 	global progs													# useful for seeing whether tritones resolve.etc
# 	modeIndex = int(mode[0:3].upper() == 'MIN')
# 	if type(progList) is str: progList = [progList]
# 	foundProgs = 0
# 	total = 0
# 	for i, progStr in enumerate(progList):
# 		if progStr not in progs[modeIndex]: 
# 			if printIt: print(progStr, "not Found"
# 			continue
# 		tempFound = 0
# 		tempTotal = 0
# 		newDict = progs[modeIndex][progStr]
# 		for pair in newDict:
# 			tempTotal += newDict[pair]
# 			if pair.count(findStr) > 0 or (noS and pair.replace('S', '').count(findStr) > 0):
# 				tempFound += newDict[pair]
# 		if printIt: print("     " + progStr +":", tempFound, "out of", tempTotal, "progressions contain", findStr, "(%.1f percent)" % (100. * tempFound/tempTotal)
# 		total += tempTotal
# 		foundProgs += tempFound
# 	if len(progList) > 1 and printIt: print("TOTAL:", foundProgs, "out of", total, "progressions (%.1f percent)" % (100. * foundProgs/total)
# 	return foundProgs, total

# rn_sevenths = {}	

# def canonic_VL(thresh = 4):			# are sevenths prepared?
# 	global results
# 	canonicVL = [[0, -1], [4, -2], [4, 3], [7, 4]]
# 	results = {}
# 	bigCount = 0
# 	misses = 0
# 	for modeIndex in [0, 1]:
# 		for myProg in progs[modeIndex]:
# 			for myVL in progs[modeIndex][myProg]:
# 				theVL = DT.vl_normal_form(convert_VLstr(myVL))
# 				counter = 0
# 				for path in canonicVL:
# 					if path in theVL: 
# 						counter += 1
# 					elif path[1] == -1 and [path[0], -2] in theVL:
# 						counter += 1
# 					elif path[1] == -2 and [path[0], -1] in theVL:
# 						counter += 1
# 					elif path[1] == 3 and [path[0], 4] in theVL:
# 						counter += 1
# 					elif path[1] == 4 and [path[0], 3] in theVL:
# 						counter += 1
# 				if counter >= thresh:
# 					bigCount += progs[modeIndex][myProg][myVL]
# 					print(myProg, myVL, progs[modeIndex][myProg][myVL]
# 				else:
# 					misses += progs[modeIndex][myProg][myVL]
# 	print(" percent canonic VL: %.2f" % (100. * bigCount / (misses + bigCount))


"""myChord can either be a specific string, a list of specific chords, the generic wildcard *, or a chordsymbol plus an inversion wildcard V*

NOTE TO SELF: learn how to use regex for this sort of thing"""

# def prepared_seventh(myChord = 'V7', mode = 'major'):			# are sevenths prepared?
# 	global rn_sevenths, results
# 	if type(myChord) is str:
# 		myChord = [myChord]
# 	newChords = []
# 	for s in myChord:
# 		if len(s) > 1 and s[-1] == '*':
# 			newChords += [s[:-1] + x for x in ['7', '6/5', '4/3', '2']]
# 		else:
# 			newChords.append(s)
# 	myChord = newChords
# 	print(myChord
# 	modeIndex = int(mode[0:3].upper() == 'MIN')
# 	results = {}
# 	for myProg in progs[modeIndex]:
# 		theChords = myProg.split(' -> ')
# 		if (theChords[1] in myChord or (myChord[0] == '*' and DT.parse_figure(theChords[1])[1] in ['7', '6/5', '4/3', '2'])):
# 			if theChords[1] not in rn_sevenths:
# 				rn_sevenths[theChords[1]] = roman.RomanNumeral(theChords[1], 'C').seventh.pitchClass
# 			targetPC = rn_sevenths[theChords[1]]
# 			for myVL in progs[modeIndex][myProg]:
# 				theVL = convert_VLstr(myVL)
# 				for path in theVL:
# 					if sum(path) % 12 == targetPC:
# 						results[path[1]] = results.setdefault(path[1], 0) + progs[modeIndex][myProg][myVL]
# 	print(" percent prepared: %.2f" % (100. * sum([results.setdefault(x, 0) for x in [0, -1, -2, 1, 2]]) / sum(results.values()))
				
# def has_diminished_fifth(p):
# 	theInts = [interval.Interval(x, y).name for x in p for y in p]
# 	if 'd5' in theInts or 'd12' in theInts or 'd19' in theInts:
# 		return True
# 	return False

# UPmotions = ['[0, 4', '[2, 3', '[4, 3', '[5, 4', '[7, 4', '[9, 3', '[11, 3']	
# DOWNmotions = ['[0, -3', '[2, -3', '[4, -4', '[5, -3', '[7, -3', '[9, -4', '[11, -4']

# def filled_in_thirds(mode = 'major'):
# 	global theMotions
# 	rn.load(globalSource)
# 	plt.title('Likelihood for a third to be filled in with a passing tone', fontsize = 24)
# 	plt.ylabel('Percentage', fontsize = 18)
# 	plt.xlabel('Starting scale degree', fontsize = 18)
# 	values = [[], []]
# 	theMotions = {}
# 	totalMotions = UPmotions + DOWNmotions
# 	totalMotions = totalMotions + [x + 'P' for x in totalMotions]
# 	for item in totalMotions:
# 		theMotions[item] = 0
# 	modeIndex = int(mode[0:3].upper() == 'MIN')
# 	for myProg in progs[modeIndex]:
# 		for myVL in progs[modeIndex][myProg]:
# 			for testMotion in totalMotions:
# 				if myVL.count(testMotion) > 0:
# 					theMotions[testMotion] += progs[modeIndex][myProg][myVL]
# 	x = rn.regex("^V(6|6/4)* -> V(7|6/5|4/3|2)$", mode = mode, pcts = False, printIt = False)		#
# 	theMotions['[7, -3P'] += x
# 	theMotions['[7, -3'] += x
# 	for i in range(len(UPmotions)):
# 		#print(UPmotions[i], theMotions[UPmotions[i]], theMotions[UPmotions[i] + 'P'], '\t', DOWNmotions[i], theMotions[DOWNmotions[i]], theMotions[DOWNmotions[i] + 'P']
# 		values[0].append(100. * theMotions[UPmotions[i] + 'P'] / max(theMotions[UPmotions[i]], 1))
# 		values[1].append(100. * theMotions[DOWNmotions[i] + 'P'] / max(theMotions[DOWNmotions[i]], 1))
# 		print(UPmotions[i], theMotions[UPmotions[i]], '%.2f' % values[0][-1], '\t', DOWNmotions[i], '%.2f' % values[1][-1]
# 	plt.plot(values[0], label='Ascending')
# 	plt.plot(values[1], label='Descending')
# 	ticks = range(7)
# 	plt.xticks(ticks, [str(x) for x in range(1, 8)], fontsize = 18)
# 	myLeg = plt.legend(('Ascending', 'Descending'), loc=0)
# 	for i in range(len(myLeg.legendHandles)):
# 		myLeg.legendHandles[i].set_linewidth(2.0)
# 	plt.show()
		
# def renaissance_sevenths(mode = 'MAJOR'):						# the Renaissance seventh idiom
# 	k = key.Key('C')
# 	modeInd = int(mode[0:3].upper() == 'MIN')
# 	thePitches = 'D F A C E G B '
# 	theList = (thePitches * 3).split()
# 	d = 0
# 	u = 0
# 	b = 0
# 	for i in range(7):
# 		startChord = chord.Chord([theList[i] + '3'] + [x + '4' for x in theList[i+1:i+4]])
# 		endChord =  chord.Chord([theList[i] + '3', theList[i+1] + '4'] + [theList[i+6] + '4'])
# 		thePC = startChord.fifth.pitchClass
# 		thePath = -1 * ((startChord.fifth.pitchClass - startChord.third.pitchClass) % 12)
# 		secondPath = (-1 * ((startChord.fifth.pitchClass - endChord.root().pitchClass) % 12)) % 12
# 		theProg = DT.figure_from_chord(startChord, k) + ' -> ' + DT.figure_from_chord(endChord, k)
# 		thing1 = '[' + str(thePC) + ', ' + str(thePath)
# 		thing2 = '[' + str(thePC) + ', ' + str(secondPath)
# 		down = 0
# 		up = 0
# 		both = 0
# 		if theProg not in progs[modeInd]: continue
# 		for theVL in progs[modeInd][theProg]:
# 			count1 = theVL.count(thing1)
# 			count2 = theVL.count(thing2)
# 			if count1 > 0 and count2 == 0:
# 				down += progs[modeInd][theProg][theVL]
# 			elif count1 == 0 and count2 > 0:
# 				up += progs[modeInd][theProg][theVL]
# 			elif count1 > 0 and count2 > 0:
# 				both += progs[modeInd][theProg][theVL]
# 		print(theProg, down, up, both
# 		d += down
# 		u += up
# 		b += both
# 	print("TOTAL", d, u, b