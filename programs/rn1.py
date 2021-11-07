#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import operator
import copy
import time
import pickle
import re
import matplotlib.pyplot as plt
from music21 import *
from scipy.stats.stats import pearsonr
import DT

_BADCHORALES = []
_MODULATIONDEPTH = 3
counts = [{}, {}]
locations = [{}, {}]
symbolDict = [{}, {}]
# inputFile = open (DT._DATAPATH + 'bass_dict.pkl', 'rb')
# symbolDict = pickle.load(inputFile)
# inputFile.close()
"""for modeInd in [0, 1]:
	for item in symbolDict[modeInd]:
		print item, symbolDict[modeInd][item]"""
output = stream.Score()
lastChorale = 0
chorale = stream.Score()
analyzed_file = stream.Score()

"""FORMAT FOR GRAMMAR DICT: 

key = grammarname; [l1, l2, l3] = generally allowable progs, progs allowable only in specific inversions, and i specific progs allowable only in minor

"""

def reset_all_data(skipComposers = ['BACH', 'DALZA', 'MOZART', 'MONTEVERDI']):
	skipComposers = [s.upper() for s in skipComposers]
	for c in DT.comps:
		if c in skipComposers:
			continue
		print "ANALYZING", c
		gather_stats(c)

class GrammarObject():
	
	grammars = 		{'DMITRI': [	['V -> I', 'viio -> vi', 'IV -> viio', 'vi -> viio', 'vi -> V', 'viio -> V', 'I -> IV', 'vi -> IV', 'I -> vi', 
								'IV -> V', 'I -> viio', 'ii -> V', 'V -> vi', 'IV -> I', 'vi -> ii', 'I -> ii', 'viio -> I', 'IV -> ii', 'ii -> viio', 'I -> V'],
							
								['V7 -> IV6', 'vi -> I6', 'ii6 -> I6/4', 'V -> IV6/5', 'vi -> I6/4', 'ii6/5 -> I6/4', 'V6 -> IV6', 'ii -> I6/4', 'V6/5 -> IV6', 
								'viio6 -> IV6', 'V7 -> IV6/5', 'V -> IV6'], 
							
								['V7 -> iv6', 'V -> v', 'VII -> viio', 'iio6 -> i6/4', 'V -> IV6/5', 'VI -> i6/4', 'V6 -> v6', 'V6 -> IV6', 'VI -> i6', 'V6/5 -> IV6', 
								'V7 -> IV6/5', 'V -> iv6', 'VII -> viio7', 'v6 -> IV6', 'V7 -> IV6', 'ii/o4/3 -> i6/4', 'v6 -> iv6', 'V -> iv6/5', 'v -> iv6', 'ii/o6/5 -> i6/4', 
								'III+6 -> i', 'i -> VII', 'i -> VII6', 'V7 -> iv6/5', 'V -> IV6']
							
								],
				
					'RAMEAU': [	['V -> I', 'viio -> vi', 'iii -> vi', 'IV -> viio', 'vi -> viio', 'viio -> V', 'I -> IV', 'vi -> IV', 'I -> vi', 'IV -> V', 'IV -> ii',
						 		'ii -> iii', 'V -> vi', 'viio -> iii', 'iii -> I', 'iii -> IV', 'vi -> ii', 'I -> ii', 'V -> iii', 'ii -> V', 'ii -> viio'],
							
								[],
							
								[]
				
								],
						
					'RIEMANN': [	['IV -> viio', 'viio -> vi', 'iii -> ii', 'V -> vi', 'iii -> I', 'iii -> vi', 'I -> vi', 'ii -> iii', 'vi -> ii', 'vi -> viio', 
									'V -> I', 'IV -> V', 'V -> iii', 'iii -> IV', 'vi -> iii', 'ii -> viio', 'vi -> V', 'I -> IV', 'vi -> IV', 'IV -> iii', 'viio -> iii', 
									'I -> ii', 'viio -> I', 'ii -> V'],
							
								[],
							
								[]
				
								],	
					'RIEMANN2':	[	['viio -> vi', 'IV -> viio', 'vi -> viio', 'vi -> V', 'I -> IV', 'vi -> IV', 'I -> V', 'IV -> V', 'I -> viio', 'V -> vi', 
									'V -> I', 'vi -> ii', 'I -> ii', 'viio -> I', 'ii -> V', 'ii -> viio'],
								
								[],
							
								[]
							
								],
				
					'K&P':	[	['IV -> viio', 'V -> I', 'I -> IV', 'vi -> IV', 'I -> vi', 'IV -> I', 'I -> viio', 'ii -> V', 'V -> vi', 'I -> iii', 'iii -> vi', 
								'iii -> IV', 'vi -> ii', 'I -> ii', 'viio -> I', 'IV -> V', 'IV -> ii', 'ii -> viio', 'I -> V'],
								
								['ii6 -> I6/4', 'ii -> I6/4', 'ii6/5 -> I6/4'],
							
								['iio6 -> i6/4', 'ii/o4/3 -> i6/4', 'ii/o6/5 -> i6/4', 'VI -> i6/4'],
							
								],		
						
					}
							
	minorSubs = {'I': ['i', 'I'], 'ii': ['iio', 'ii'], 'IV': ['iv', 'IV'], 'V': ['V', 'v'], 'vi': ['VI', 'vio'], 'viio': ['viio']}
	
	def __init__(self, **kwargs):
		
		self.attributeDict = {	"mode": 'major',
								"version": 'DMITRI',
								"three": True,
								"seven": True,
								"includeMixolydian": False,
								"modalMixture": False
								}
		
		for key, value in self.attributeDict.items():
			if key in kwargs:
				setattr(self, key, kwargs[key])
			else:
				setattr(self, key, value)
		
		self.modeIndex = int(self.mode.upper().startswith('MI'))
		self.version = self.version.upper()
		
		if self.modeIndex == 0:
			self.allowableProgs, self.iProgs, self.minorProgs = GrammarObject.grammars[self.version]	
			self.myChords = DT._DIATONICMAJOR[:]
			if self.includeMixolydian:
				self.myChords += [x + y for x in ['bVII', 'v', 'iiio'] for y in ['', '6', '6/4']]	#allow bVII, etc to count against the grammar. 
				self.myChords += [x + y for x in ['bVIImaj', 'v', 'iii/o'] for y in ['7', '6/5', '4/3', '2']]
			self.otherMode = DT._DIATONICMINOR
		
		else:
			self.myChords = DT._DIATONICMINOR
			self.otherMode = DT._DIATONICMAJOR
			self.allowableProgs = []
			tempGeneralProgs, junk, self.iProgs = GrammarObject.grammars[self.version]
			
			for tempProg in tempGeneralProgs:
				rn1, rn2 = tempProg.split(' -> ')
				if rn1 in GrammarObject.minorSubs or rn2 in GrammarObject.minorSubs:
					sub1 = GrammarObject.minorSubs.get(rn1, [rn1])
					sub2 = GrammarObject.minorSubs.get(rn2, [rn2])
					for newRN1 in sub1:
						for newRN2 in sub2:
							self.allowableProgs.append(newRN1 + ' -> ' + newRN2)
	
	def grammar_test(self, progStr):
		
		masterChords = progStr.split(' -> ')
		
		for i in range(len(masterChords) - 1):
			
			chords = masterChords[i:i+2]
		
			self.strippedRNs = [[], []]
		
			for i in range(len(chords)):
				if not self.three: chords[i] = self.replace_three(chords[i])
				if not self.seven: chords[i] = replace_flat_seven(chords[i])
			
				self.strippedRNs[i] = DT.parse_figure(chords[i])
				if self.strippedRNs[i][2] or self.strippedRNs[i][3]: 
					return -1
			
				self.strippedRNs[i] = self.strippedRNs[i][0].replace('maj', '').replace('/o', 'o')
			
				if self.strippedRNs[i] not in self.myChords:
					if (not self.modalMixture) or (self.strippedRNs[i] not in self.otherMode):
						return -1
		
			if self.strippedRNs[0] == self.strippedRNs[1]: 
				return -2
			
			self.newProgStr = ' -> '.join(chords)		
			self.bareProgstr = ' -> '.join(self.strippedRNs)
		
			if (self.bareProgstr not in self.allowableProgs) and (self.newProgStr not in self.iProgs):
				return False
			
		return True
		
	def replace_three(self, rn):
		if self.modeIndex == 0 and rn.count('iii') > 0 and rn not in ['iii7', 'iii6/5', 'iii4/3', 'iii2']:
			rn1 = rn.replace('iii6', 'V')
			rn1 = rn1.replace('iii', 'I6')
			rn1 = rn1.replace('66/4', '')
			return rn1
			
		elif self.modeIndex == 1 and rn.count('III') > 0 and rn not in ['III7', 'III6/5', 'III4/3', 'III2']:
			rn1 = rn.replace('III6', 'V')
			rn1 = rn1.replace('III', 'i6')
			rn1 = rn1.replace('66/4', '')
			return rn1
		return rn
	
	def replace_flat_seven(self, rn):
		if self.modeIndex == 0 and rn.count('bVII') > 0:
			rn1 = rn.replace('bVII', 'V6')
			rn1 = rn1.replace('bVII6', 'viio6')
			return rn1
		return rn


"""
Catalogue RN progressions
	1. Remove duplications in the stats generation?
	
TO DO:
	1. RECORD A KEY THAT ASSOCIATES COUNTER WITH FILENAMES; STORE THESE FILENAMES IN THE PICKLED FILE
	1. Gather all lengths from 1 to 5 at once
	2. Make it possible to gather all the files in a directory 
	
	>>> import os
	>>> os.listdir(DT._HUMANBEETHOVEN)
	['.DS_Store', 'sonata01-1.txt', 'sonata16-1.txt', 'sonata16-2.txt', 'sonata16-3.txt']
	>>> import glob
	>>> glob.glob(DT._HUMANBEETHOVEN + '/*.txt')
	
"""

def gather_stats(source='BACH', size = 5, removeProgressionsAcrossPhraseBreaks = True):
	global counts, locations, currentSize, analyzed_file, locNames, modulationProgs, globalRemoveProgressionsAcrossPhraseBreaks
	global quarterChords, eighthEighthChords, globalSource, cPitch, fullChordDict
	globalRemoveProgressionsAcrossPhraseBreaks = removeProgressionsAcrossPhraseBreaks
	quarterChords = 0
	recordResults = False
	eighthEighthChords = 0
	modulationProgs = {}
	counts = [{}, {}]
	locations = [{}, {}]
	locNames = {}
	fullChordDict = {}
	currentSize = size
	startT = time.time()
	fileStr = ''
	cPitch = pitch.Pitch('C')
	globalSource = source.upper()
	if globalSource in DT._PATHS:
		filePath = DT._PATHS[globalSource][0]
		fileStr = globalSource
		files = os.listdir(filePath)
		if globalSource == 'BEETHOVEN QUARTETS':
			files = sorted(files, key = specialsort)
		recordResults = True
		counter = 1
		for myFile in files:
			if myFile[-3:] == 'txt':
				locNames[counter] = myFile[:-4]
				print 'Analyzing', myFile
				analyzed_file = new_parse(filePath + myFile)
				dochorale(counter, size)
				counter += 1
	#print "Quarter-note chords", quarterChords, "(" + str(100*quarterChords/(quarterChords + eighthEighthChords)) + '%)', "Eighth-note + eighth-note pairs", eighthEighthChords
	minutes = (time.time() - startT)/60.
	print 'Total analysis took', int(minutes), 'minutes and', int((minutes - int(minutes)) * 60), 'seconds'
	if recordResults:
		if source == 'BachMechanical': fileStr += 'MACHINE'
		if source == 'BachClean': fileStr += 'CLEANMACHINE'
		outputFile = open (DT._DATAPATH + 'ALL_progressions' + fileStr + '.pkl', 'wb')
		pickle.dump(counts, outputFile)
		pickle.dump(locations, outputFile)
		pickle.dump(locNames, outputFile)			# need to make use of this
		pickle.dump(filePath, outputFile)			# ditto!
		pickle.dump(modulationProgs, outputFile)
		pickle.dump(fullChordDict, outputFile)
		outputFile.close()
	return

def new_parse(fName):
	outList = []
	with open(fName, 'rb') as myFile:
		lastKey = False
		for line in myFile:
			if line[0] != 'm': continue
			lastBeat = 1
			lSplit = line.split()
			mNum = lSplit[0][1:]
			if not all([x.isdigit() for x in mNum]):
				if mNum[-1] == 'a': continue
				mNum = ''.join([x for x in mNum if x.isdigit()])
			lastMeasure = int(mNum)
			for c in lSplit[1:]:
				if c.count('|') > 0: c = c.replace(':', '')		# get rid of some obsolete notation in Bach
				if c[0] == 'b' and c[1].isdigit():
					#print c
					lastBeat = parse_beat(c[1:])
				elif c[-1] == ':':
					lastKey = c.replace(':', '')
				else:
					outList.append([lastMeasure, lastBeat, lastKey, c])
	
	"""strip duplicates"""
	newOutList = []
	lastKey = False
	lastChord = False
	for l in outList:
		if l[2] == lastKey and l[3] == False:
			continue
		lastKey = l[2]
		lastChord = l[3]
		newOutList.append(l)
	return newOutList 
					
def parse_beat(c):
	if c.count('.') == 0:
		return int(c)
	else:
		return int(c.split('.')[0])
		
def specialsort(s):
	strippedS = ''.join([x for x in s if (x.isdigit() or x == '_')])
	sSplit = strippedS.split('_')
	return [int(x) for x in sSplit if x]
	
def dochorale(n, size):															# record progressions UP TO size n
	global counts, locations, output, pTreb, pBass, chorale, analyzed_file, anal, modulationProgs
	global quarterChords, eighthEighthChords, globalSource, fullChordDict
	global startOffset, endOffset, ourKey, lastMeasure, cPitch
	anal = analyzed_file
	
	lastMeasure = 0
	startOffset = 0
	endOffset = 0
	lastChordWasAPhraseBreak = False
	fullChordList = []
	lastKey = False
	lastFigure = False
	
	for l in anal:
		theFigure = l[3]
		theKey = l[2]
		if theKey != lastKey:
			lastKey = theKey
			fullChordList.append(theKey)
		if theFigure != lastFigure:
			fullChordList.append(theFigure)
			lastFigure = theFigure
	
	for i in range(len(anal) - size + 1):
		RN = []
		ourKey = []
		progStr = ''
		lastSym = ''
		
		"""Main loop: breaks the recording process if we have a phrase marker ||, an unknown key sign ?: or a key change"""
		
		for j in range(0, size):
			if anal[i+j][3] == '||' and globalRemoveProgressionsAcrossPhraseBreaks: 
				break
			if anal[i+j][3] == '||':
				lastChordWasAPhraseBreak = True
				continue
			elif anal[i+j][3] == '?:':
				break
			if not ourKey:
				theFigure = anal[i+j][3]
				ourKey = anal[i+j][2]
				oldTonic = anal[i+j][2]
				progStr = theFigure
				lastSym = theFigure
				startOffset = anal[i+j][:2]
				endOffset = anal[i+j][:2]
				record(n, progStr)
			else:
				if anal[i+j][2] == ourKey:
					progStr = progStr + ' -> ' + anal[i+j][3]
					lastSym = anal[i+j]
					endOffset = anal[i+j][:2]
					record(n, progStr)
				else:
					if j == 1 or (j ==2 and lastChordWasAPhraseBreak):
						modulationString = ''
						modeInd = int(ourKey[0].islower())
						chordList = anal[max(i - _MODULATIONDEPTH, 0):min(i + j + 1 + _MODULATIONDEPTH, len(anal))]
						t = DT.fix_flats(oldTonic.replace(':', ''))
						transposeInterval = interval.Interval(pitch.Pitch(t), cPitch)
						lastRecordedKeyInKeyString = ''
						for c in chordList:
							if c[3].count('|') > 0: continue
							newKey = DT.transpose_letter(c[2], transposeInterval, fixFlats = True)
							if newKey != lastRecordedKeyInKeyString:
								lastRecordedKeyInKeyString = newKey
								modulationString += newKey + ': '
							modulationString += c[3] + ' -> '
						if len(modulationString) > 4 and modulationString[-4:] == ' -> ': modulationString = modulationString[:-4]
						modulationString = filter_modulation_string(modulationString)
						modulationProgs.setdefault(modulationString, []).append(n)
						break
			lastChordWasAPhraseBreak = False
	fullChordDict.setdefault(n, []).append(fullChordList)
	return



def filter_modulation_string(s):
	outList = []
	sSplit = s.split(' -> ')
	lastChord = ''
	for t in sSplit:
		if t == lastChord and t.count(":") == 0:
			continue
		if t == '||': continue
		outList.append(t)
		if t.count(":") > 0:
			lastChord = t.split(': ')[1]
		else:
			lastChord = t
	return ' -> '.join(outList)

def remove_inversions_from_modulation_strings(separateSixFour = True):
	global modulationProgs
	newDict = {}
	for s in modulationProgs:
		newFig = DT.remove_inversions(s, separateSixFour = separateSixFour)
		tempList = newDict.get(newFig, []) + modulationProgs[s]
		newDict[newFig] = tempList
	modulationProgs = newDict

def trim_modulation_strings(length = 2):
	global modulationProgs
	length = int(length/2. + .5)
	newDict = {}
	for s in modulationProgs:
		sSplit = s.split(' -> ')
		sSplitLen = len(sSplit)
		keyChangeLocations = [x for x in range(sSplitLen) if sSplit[x].count(':') > 0]
		keys = [sSplit[x].split(':')[0] for x in keyChangeLocations]
		firstC = keys[0]
		if s.count(':') <= 2:
			target = keyChangeLocations[-1]
		else:
			foundC = False
			target = -1
			for i, k in enumerate(keys):
				if foundC: 
					target = i
					break
				if k == 'c' or k == 'C':
					firstC = k
					foundC = True
			if target == -1: continue
		finalSplit = sSplit[max(target - length, 0):min(sSplitLen, target + length)]
		if finalSplit[0].count(':') == 0:
			newFig = firstC + ': ' + ' -> '.join (finalSplit)
		else:
			newFig = ' -> '.join (finalSplit)
		#print s, newFig, [max(target - length, 0), min(sSplitLen, target + length)]
		tempList = newDict.get(newFig, []) + modulationProgs[s]
		newDict[newFig] = tempList
	modulationProgs = newDict		

def find_modulations(keyStr = 'C c', printIt = True):
	global output, outputLocations
	output = {}
	outputLocations = {}
	organize_modulations()
	for s in modulations:
		sSplit = s.split(' -> ')
		sSplitLen = len(sSplit)
		keyChangeLocations = [x for x in range(sSplitLen) if sSplit[x].count(':') > 0]
		keys = ' '.join([sSplit[x].split(':')[0] for x in keyChangeLocations])
		if keys == keyStr:
			output[s] = len(modulations[s])
			outputLocations[s] = modulations[s]
	if printIt:
		DT.print_dict(output)

def record(n, progStr):
	
	global counts, locations, output, pTreb, pBass, chorale, analyzed_file
	global startOffset, endOffset, ourKey, lastMeasure, globalSource
	
	mNumber = startOffset[0]				# TIME_SIGNATURE.ratioString
	lastMeasure = mNumber
	nmNumber = endOffset[0]
	
	mList = [n, mNumber]
	if not mNumber == nmNumber: mList.append(nmNumber)
	
	dictIndex = int(ourKey[0].islower())			# 0 for major, 1 for minor
	if progStr in counts[dictIndex]:
		counts[dictIndex][progStr] += 1
		locations[dictIndex][progStr].append(mList)
	else:
		counts[dictIndex][progStr] = 1
		locations[dictIndex][progStr] = [mList]

def load(source = 'BEETHOVEN QUARTETS'):
	global counts, locations, globalSource, locNames, currentSize, working, modulationProgs
	working = [{}, {}]
	currentSize = 5
	if type(source) is not list:
		load_composer_data(source)
		return
	load_composer_data(source[0])
	for i in [0, 1]: normalize_dict(counts[i], len(source))
	permaCounts = copy.deepcopy(counts)
	for s in source[1:]:
		load_composer_data(s)
		for i in [0, 1]: 
			normalize_dict(counts[i], len(source))
			for k in set(permaCounts[i].keys() + counts[i].keys()):
				permaCounts[i][k] = permaCounts[i].get(k, 0) + counts[i].get(k, 0)
	counts = permaCounts
		

def load_composer_data(source):
	global counts, locations, globalSource, locNames, currentSize, working, modulationProgs, fullChordDict
	globalSource = source.upper()
	with open(DT._DATAPATH + 'ALL_progressions' + globalSource + '.pkl', 'rb') as storedFile:
		if not storedFile: 
			print "CAN'T LOAD FILE"
			return
		try:
			counts = pickle.load(storedFile)
			locations = pickle.load(storedFile)
			locNames = pickle.load(storedFile)
			dummy = pickle.load(storedFile)
			modulationProgs = pickle.load(storedFile)
			fullChordDict = pickle.load(storedFile)
		except:
			pass
	
	

def list_items(progStr, mode = 'major'):
	global counts, locations, globalSource, locNames, currentSize, working
	modeInd = (mode[0:3].upper() != 'MAJ')
	for item in locations[modeInd][progStr]:
		print '    ', locNames[item[0]], 'measure', item[1]

load()

def rem_dups(myProg):
	syms = myProg.split(' -> ')
	if len(syms) <= 1: return myProg
	lastSym = syms[0]
	out = syms[0]
	for elem in syms[1:]:
		if elem != lastSym:
			out += ' -> ' + elem
			lastSym = elem
	return out

def remove_duplicates():
	global counts, locations
	newCounts = [{}, {}]
	newLocations = [{}, {}]
	for modeInd in [0,1]:
		for prog in counts[modeInd]:
			newProg = rem_dups(prog)
			if newProg == 'I -> bIII -> IV': print prog, counts[modeInd][prog]
			newCounts[modeInd][newProg] = newCounts[modeInd].setdefault(newProg, 0) + counts[modeInd][prog]
			if newProg in newLocations:
				for oldLoc in locations[modeInd][prog]:
					newLocations[modeInd][newProg].append(oldLoc)
			else:
				newLocations[modeInd][newProg] = locations[modeInd][prog]
	counts = newCounts
	locations = newLocations

def show(rnProg, mode = 'MAJ', rangeList = [-1, -1], RNs = True):
	global output, locNames, globalSource
	output = stream.Score()
	if type(rangeList) is int:
		rangeList = [rangeList, -1]
	elif len(rangeList) is 1:
		rangeList.append(-1)
	tempOutput = stream.Score()
	modeInd = (mode.upper()[:3] == 'MIN')
	lastChoraleNo = False
	try:
		locList = locations[modeInd][rnProg]							# check for key error
	except KeyError:
		print 'Not found'
		return
	if globalSource in ['BILL', 'ROCK']:
		for instance in locList:
			if locNames[instance[0]] != lastChoraleNo:
				choraleNo = locNames[instance[0]]
				print ""
				print "GETTING ",choraleNo
				lastChoraleNo = choraleNo
				myFile = open(DT._PATHS[globalSource][0] + choraleNo + '.txt', 'rb')
				for line in myFile:
					if globalSource == 'ROCK':
						if line[:4].upper() != 'NOTE': 
							continue
						line = line[6:]		
					print "     ", line.rstrip('\n')
				myFile.close()
		return
	for i in range(0, 4):
		tempOutput.append(stream.Part())
	for chordNo, instance in enumerate(locList):
		if chordNo < rangeList[0] or (rangeList[1] != -1 and chordNo > rangeList[1]): continue
		measureList = [int(x) for x in instance[1:]]
		if len(measureList) == 1:
			measureList = [measureList[0], measureList[0] + 1]
		else:
			measureList[-1] = measureList[-1] + 1
		header = str(locNames[instance[0]])+'m'+str(measureList[0])
		print 'getting', locNames[instance[0]], measureList
		if locNames[instance[0]] != lastChoraleNo:
			choraleNo = locNames[instance[0]]
			lastChoraleNo = choraleNo
			try:
				chorale = converter.parse(DT._PATHS[globalSource][1] + choraleNo + '.xml')
			except:
				try:
					chorale = converter.parse(DT._PATHS[globalSource][1] + choraleNo + '.krn')
				except:
					chorale = converter.parse(DT._PATHS[globalSource][1] + choraleNo + '.mxl')
			if RNs: 
				analyzed_file = converter.parse(DT._PATHS[globalSource][0] + choraleNo + '.txt', format='romantext')
			if globalSource == 'MOZART':
				DT.remove_repeats(chorale)
				DT.remove_repeats(analyzed_file)
		if RNs:
			DT.add_roman(chorale, analyzed_file, measureList[0], measureList[1])
		tempChorale = copy.deepcopy(DT.get_measures(chorale, int(measureList[0]), int(measureList[1])))
		DT.insert_text(tempChorale.parts[0][0], header, 55, 0)
		output = DT.append(tempChorale, output)
	if RNs:
		output = DT.fix_roman_placement(output)
	for p in output.parts:
		for item in p.flat:
			if 'Note' in item.classes or 'Chord' in item.classes: item.lyrics = []
	output.show()
	return output

def get_mode(mode = 'major'):
	if type(mode) == str:
		return int(mode.upper().startswith("MI"))
	elif type(mode) == int:
		return mode

def count_pieces():									# count pieces with the occurrence of a progression, not progressions themselves
	for modeInd in [0, 1]:
		for item in locations[modeInd]:
			tempDict = {}
			for locList in locations[modeInd][item]:
				tempDict[locList[0]] = 1
			counts[modeInd][item] = len(tempDict)
			locations[modeInd][item] = []
			for thing in tempDict:
				locations[modeInd][item].append([thing, 1])

def starts(firstChord, mode = 'major', source='', printIt = True, pct = True):
	global working, tempList
	if not source:
		modeInd = get_mode(mode)
		source = working[modeInd]
	results = []										
	for prog in source:
		if prog[0:len(firstChord)] == firstChord:
			results.append([prog, source[prog]])
	tempList = sorted(results, key=operator.itemgetter(1), reverse = True)
	mySum = sum([x[1] for x in tempList])
	tempCounts = 0
	if printIt:
		for pair in tempList: 
			if pct:
				print pair[0], "%.1f" % (100. * pair[1]/mySum)
			else:
				print pair[0], pair[1]
	return mySum

def ends(lastChord, mode = 'major', source='', printIt = True, pct = True):
	global working, tempList
	if not source:
		modeInd = get_mode(mode)
		source = working[modeInd]
	results = []										
	for prog in source:
		if prog[-len(lastChord):] == lastChord:
			results.append([prog, source[prog]])
	tempList = sorted(results, key=operator.itemgetter(1), reverse = True)
	mySum = sum([x[1] for x in tempList])
	tempCounts = 0
	if printIt:
		for pair in tempList: 
			if pct:
				print pair[0], "%.1f" % (100. * pair[1]/mySum)
			else:
				print pair[0], pair[1]
	return mySum


def regex(patternString, mode = 'major', source='', printIt = True, pct = True):
	global tempList
	if not source:
		modeInd = get_mode(mode)
		source = counts[modeInd]
	results = []
	patternString = patternString.replace("CHORD", "[^-]*").replace("INV", "[0-9/]*")
	for prog in source:
		if re.match(patternString, prog):
			#print prog
			results.append([prog, source[prog]])
	tempList = sorted(results, key=operator.itemgetter(1), reverse = True)
	mySum = sum([x[1] for x in tempList])
	if printIt:
		for pair in tempList: 
			if pct:
				print pair[0], "%.1f" % (100. * pair[1]/mySum)
			else:
				print pair[0], pair[1]
	return mySum

def contains(lastChord, mode = 'major'):
	results = []
	modeInd = get_mode(mode)
	for prog in working[modeInd]:
		if prog.count(lastChord) > 0:
			results.append([prog, working[modeInd][prog]])
	tempList = sorted(results, key=operator.itemgetter(1), reverse = True)
	tempCounts = 0
	for pair in tempList: 
		print pair
		tempCounts += pair[1]
	print tempCounts
	return

def strict_filter(mode = 'MAJOR'):
	global working, filteredChords
	filteredChords = 0
	modeInd = get_mode(mode)
	acceptableTriads = [DT._DIATONICMAJOR, DT._DIATONICMINOR][modeInd]
	delList = []
	for item in working[modeInd]:
		tempSplit = item.split(' -> ')
		for myChord in tempSplit:
			if myChord not in acceptableTriads:
				delList.append(item)
				break
	for item in delList:
		filteredChords += working[modeInd][item]
		del working[modeInd][item]
		
def percent_diatonic(mode = 'MAJOR', **kwargs):
	modeInd = get_mode(mode)
	get_size(1, **kwargs)
	totalChords = sum(working[modeInd].values())
	strict_filter(mode)
	return 100.*filteredChords/totalChords

"""TODO: update this for arbitrary lengths"""

def bass_degrees(degStr, mode = 'major'):										# works but is very slow!
	progSize = degStr.count('>') + 1
	get_size(progSize)
	results = []
	degStr = remove_arrows(degStr)
	modeInd = get_mode(mode)
	if modeInd == 0:
		myKey = key.Key('C')
		keyStr = 'C'
	else:
		myKey = key.Key('c')
		keyStr = 'c'
	firstDeg = degStr[0]
	for prog in working[modeInd]:
		foundMismatch = False
		symbols = remove_arrows(prog)
		for i in range(0, len(symbols)):
			RN = roman.RomanNumeral(symbols[i], keyStr)
			#print RN, symbols
			#print DT.pc_from_scale_degree(degStr[i], myKey)
			if RN.pitches[0].pitchClass != DT.pc_from_scale_degree(degStr[i], myKey):
				foundMismatch = True
				break
		if not foundMismatch:
			results.append([prog, counts[modeInd][prog]])			 
	return sorted(results, key=operator.itemgetter(1), reverse = True)

def remove_arrows(s):
	t = s.split()
	for i in range(0, (len(t)-1)/2):
		t.remove('->')
	return t
	
def getstats(progStr, percent = False):
	global counts, progDict, progDictKey
	myList = sorted(progDict[progDictKey[progStr]].iteritems(), key=operator.itemgetter(1), reverse = True)
	if percent:
		total = 0
		for name, count in myList:
			total += count
		for i in range(len(myList)):
			myList[i] = (myList[i][0], round(100.0 * myList[i][1]/total, 2))
	return myList
	
def fix_half_diminished(progStr):
	progStr = progStr.replace('o7', '/o7')
	progStr = progStr.replace('o6/5', '/o6/5')
	progStr = progStr.replace('o4/3', '/o4/3')
	progStr = progStr.replace('o2', '/o2')
	return progStr

def fix_major(progStr):
	progStr = progStr.replace('o7', '/o7')
	progStr = progStr.replace('o6/5', '/o6/5')
	progStr = progStr.replace('o4/3', '/o4/3')
	progStr = progStr.replace('o2', '/o2')
	return progStr

def reduce(modeStr = 'major', tonicizations = True):
	global reduced_counts
	reduced_counts = {}
	if modeStr[0:3].upper() == 'MAJ': 
		modeIndex = 0
	else:
		modeIndex = 1
	for prog in counts[modeIndex]:
		newprog = reduce_prog(prog, tonicizations)
		reduced_counts[newprog] = reduced_counts.setdefault(newprog, 0) + counts[modeIndex][prog]
		
def all_inversions(progStr, modeInd = 0):
	progList = progStr.split(' -> ')
	totalCounts = 0
	for firstInv in ['', '6', '6/4', '7', '6/5', '4/3', '2']:
		if progList[0] in ['I', 'IV'] and firstInv not in ['', '6', '6/4']:
			firstInv = 'maj' + firstInv 
		for secondInv in ['', '6', '6/4', '7', '6/5', '4/3', '2']:
			if progList[1].isupper() and secondInv not in ['', '6', '6/4']:
				secondInv = 'maj' + secondInv
			tryProg = progList[0] + firstInv + ' -> ' + progList[1] + secondInv
			print tryProg
			if tryProg in counts[0]:
				totalCounts += counts[0][tryProg]
	print totalCounts


def remove_inversions(matchProg = '', three = True, printIt = False, repeats = False, filterDiatonic = False, separateSixFour = True):
	global working, reduced, counts
	if not matchProg: reduced = [{}, {}]
	for modeInd in [0, 1]:
		for item in counts[modeInd]:
			isDiatonic = True
			prog = item.split(' -> ')
			for i in range(len(prog)):
				if prog[i][-1] == '/': prog[i] = prog[i][:-1]
				if not three:
					prog[i] = prog[i].replace('iii6', 'V').replace('iii', 'I6')
				newFig = DT.parse_figure(prog[i])
				if separateSixFour:
					if newFig[1] != '6/4': newFig[1] = ''
				else:
					newFig[1] = ''
				if newFig[2]: 
					isDiatonic = False
					newFig[2] = '/' + newFig[2]
				newFig[0] = newFig[0].replace('maj', '').replace('/o','o')
				prog[i] = ''.join(newFig)
			if filterDiatonic and not isDiatonic:
				continue
			newProg = []
			newProg.append(prog[0])
			for i in range(1, len(prog)):
				if prog[i] != newProg[-1]: newProg.append(prog[i])
			newProg = ' -> '.join(newProg)
			if matchProg:
				if newProg == matchProg:
					print item, counts[modeInd][item]
					#reduced[modeInd][item] = counts[modeInd][item]
			else:
				reduced[modeInd][newProg] = reduced[modeInd].setdefault(newProg, 0) + counts[modeInd][item]
		if filterDiatonic: 
			strict_filter(['major', 'minor'][modeInd])
		if printIt: DT.print_dict(reduced[modeInd], pct = True)
	
def reduce_prog(progStr, secondaries = True, sixFour = True):
	reduced_prog_list = []
	for item in progStr.split(' -> '):
		parsed_figure = DT.parse_figure(item)
		reduced_item = parsed_figure[0].replace('maj','').replace('/o','o')
		if sixFour and parsed_figure[1] == '6/4': reduced_item += '6/4'
		if secondaries and parsed_figure[2]: reduced_item += '/' + parsed_figure[2]
		reduced_prog_list.append(reduced_item)
	return ' -> '.join(reduced_prog_list)

working = [{}, {}]

def get_size(size = 3, fauxbourdon = True, useReduced = False, removeInversions = False, sixFour = True):
	global counts, working, reduced
	if useReduced:
		sourceDict = reduced
	else:
		sourceDict = counts
	working = [{}, {}]
	if fauxbourdon or (size > 2):
		size = size - 1
		for modeInd in [0, 1]:
			for item in sourceDict[modeInd]:
				if item.count(' -> ') == size:
					newItem = item
					if removeInversions: newItem = reduce_prog(item, sixFour)
					working[modeInd][newItem] = working[modeInd].setdefault(newItem, 0) + sourceDict[modeInd][item]
		return
	"ELSE:"
	for modeInd in [0, 1]:
		for item in sourceDict[modeInd]:
			if item.count(' -> ') == 4:
				chords = item.split(' -> ')
				analyses = [DT.parse_figure(x) for x in chords]
				if ((analyses[0][1] in ['6', '6/5'] and analyses[1][1] in ['6', '6/5'] and analyses[2][1] in ['6', '6/5'])
				or (analyses[1][1] in ['6', '6/5'] and analyses[2][1] in ['6', '6/5'] and analyses[3][1] in ['6', '6/5'])
				or (analyses[2][1] in ['6', '6/5'] and analyses[3][1] in ['6', '6/5'] and analyses[4][1] in ['6', '6/5'])):
					continue
				if size == 1: 
					tempChord = chords[2]
				else:
					tempChord = chords[2] + ' -> ' + chords[3]
				#if analyses[2][0] == 'ii' and analyses[3][0] == 'I': print item, sourceDict[modeInd][item]
				newItem = tempChord
				if removeInversions: 
					newItem = reduce_prog(tempChord, sixFour)
				working[modeInd][newItem] = working[modeInd].setdefault(newItem, 0) + sourceDict[modeInd][item]

def cycles(mode = 'major'):
	global sortedDict
	modeInd = int(mode=='minor')
	get_size(3)
	sortedDict = {}
	for item in working[modeInd]:
		chords = item.split(' -> ')
		if chords[0] == 'I' and chords[2] == 'I':
			sortedDict[item] = working[modeInd][item]
	DT.print_dict(sortedDict)

def harmonic_cycles(mode = 'both', printOut = True):
	global cycleDict
	cycleDict = {}
	if mode.upper().startswith('B'):
		modeInd = 2
	else:
		modeInd = get_mode(mode)
	cycleLengths = []
	foundNonTonicChord = False
	precededByDominants = 0
	precededByIV = 0
	otherPreceders = {}
	for n in fullChordDict:
		for l in fullChordDict[n]:
			for i, s in enumerate(l):
				if s.count(':') > 0:
					myKey = s
					currentModeInd = myKey[0].islower()
					lastTonic = -1
				else:
					parsedFig = DT.parse_figure(s)
					if parsedFig[0].upper() == 'I':
						if lastTonic != -1 and (modeInd == 2 or modeInd == currentModeInd) and foundNonTonicChord and parsedFig[1] != '6/4':
							lastFig = DT.parse_figure(l[i - 1])
							if lastFig[0] in ['V', 'viio', 'vii/o'] and not lastFig[2]:
								precededByDominants += 1
							elif lastFig[0].upper() in ['IV'] and not lastFig[2]:
								precededByIV += 1
							else:
								otherPreceders[l[i - 1]] = otherPreceders.get(l[i - 1], 0) + 1
							cycleLengths.append(i - lastTonic)
							newS = ' -> '.join(remove_inversions_from_list(l[lastTonic:i+1]))
							cycleDict[newS] = cycleDict.get(newS, 0) + 1
							lastTonic = i
							foundNonTonicChord = False
						elif parsedFig[1] != '6/4':
							lastTonic = i
							foundNonTonicChord = False
					else:
						foundNonTonicChord = True
	if printOut:
		for i in sorted(otherPreceders.keys(), key = lambda x: -otherPreceders[x]):
			print i, otherPreceders[i]
	return float(sum(cycleLengths))/len(cycleLengths), precededByDominants*100./len(cycleLengths), precededByIV*100./len(cycleLengths)

def remove_inversions_from_list(myList, removeSixFour = False):
	outList = []
	for item in myList:
		if item.count(':') > 0: 
			outList.append(item)
			continue
		parsedItem = DT.parse_figure(item)
		newItem = parsedItem[0].replace('maj', '').replace('/o', 'o')
		if not removeSixFour:
			if parsedItem[1] == '6/4': newItem += '6/4'
		if parsedItem[2]: newItem += '/' + parsedItem[2]
		if (not outList) or (newItem != outList[-1]):
			outList.append(newItem)
	return outList

def get_size2(size = 2, removeInversions = False, removeSixFour = False):
	global working, tempLocations
	working = [{}, {}]
	tempLocations = [{}, {}]
	modeInd = 0
	for n in fullChordDict:
		for l in fullChordDict[n]:
			if removeInversions:
				l = remove_inversions_from_list(l, removeSixFour = removeSixFour)
			maxLen = len(l) - size
			for i, item in enumerate(l):
				if i > maxLen: break
				if item.count(':') > 0:
					if item[0].isupper():
						modeInd = 0
					else:
						modeInd = 1
					continue
				chordProg = ' -> '.join(l[i:i+size])
				if chordProg.count(':') > 0: 
					continue
				working[modeInd][chordProg] = working[modeInd].get(chordProg, 0) + 1
				tempLocations[modeInd].setdefault(chordProg, []).append(n)
				
"""def get_size_noduplicates():
	global counts, working
	for modeInd in [0, 1]:
		for item in counts[modeInd]:
			if item.count(' -> ') == 1:
				chords = item.split(' -> ')
				analyses = [DT.parse_figure(x) for x in chords]
				if analyses[0][0] != analyses[1][0]:
					working[modeInd][chords[1]] = working[modeInd].setdefault(chords[1], 0) + counts[modeInd][item]"""


def is_fauxbourdon(l, i, minLength = 3):
	
	if not(is_first_inversion(l[i])):
		return False
		
	counter = 1
	
	for j in range(1, minLength):
		if (i - j) < 0 or not(is_first_inversion(l[i - j])):
			break
		counter += 1
	
	if counter >= minLength:
		return True
	
	listLen = len(l)
	
	for j in range(1, minLength):
		if (i + j) >= listLen or not(is_first_inversion(l[i + j])):
			break
		counter += 1
		if counter >= minLength:
			return True
	
	return False

def is_first_inversion(fig):
	if DT.parse_figure(fig)[1] in ['6', '6/5']: return True
	return False


def build_matrix(modeStr = 'major'):
	global counts, working, diatonicprogs
	diatonicprogs = {}
	get_size(2)
	totalCounts = 0
	if modeStr[0:3].upper() == 'MAJ': 
		modeIndex = 0
		myChords = DT._DIATONICMAJOR
	else:
		modeIndex = 1
		myChords = DT._DIATONICMINOR
	print "ROW -> COLUMN"
	headerList = []
	header = ''
	for progStr in myChords:
			header = header + progStr + ' '
	print header
	for rn1 in myChords:
			matrixRow = ''
			for rn2 in myChords:
					progStr = rn1 + ' -> ' + rn2
					tempCount = 0
					try:
						tempCount = working[modeIndex][progStr]
					except KeyError:
						pass
					diatonicprogs[progStr] = tempCount
					matrixRow = matrixRow + str(tempCount) + ' '
					totalCounts += tempCount
			outputString = rn1 + ' ' + matrixRow
			print outputString
	print totalCounts, 'out of', sum(working[modeIndex].values()), 100.0 * (totalCounts * 1.0)/DT.sum_dict(working[modeIndex])

def grammar(mode = 'major', printOut = True, fauxbourdon = True, repeats = True, **kwargs):
	
	global counts, working, diatonicprogs, repeatProgs, allowableProgs, myGrammar
	
	repeatProgs = {}
	wrongies = {}
	
	modeIndex = int(mode.upper().startswith('MI'))
	myGrammar = GrammarObject(mode = mode, **kwargs)
		
	if fauxbourdon and repeats:
		get_size(2)
	else:
		get_size(5)
	totalCounts = 0
	falseCounts = 0
	
	for progStr in working[modeIndex]:
		
		if (not fauxbourdon) or (not repeats):
			chords = progStr.split(' -> ')
			analyses = [DT.parse_figure(x) for x in chords]
			
			"""Filter out chains of first inversion triads"""
			if (not fauxbourdon) and ((analyses[0][1] == '6' and analyses[1][1] == '6' and analyses[2][1] == '6') 
			or (analyses[1][1] == '6' and analyses[2][1] == '6' and analyses[3][1] == '6')
			or (analyses[1][2] or analyses[2][2])):
				continue
				
			"""filter out progressions of the form A->B->A->B"""
			if (not repeats) and ((chords[0] == chords[2] and chords[1] == chords[3]) or (chords[1] == chords[3] and chords[2] == chords[4])):
				tempSym = (analyses[1][0].upper() + '   ')
				if analyses[1][0][:3].upper() in ['II', 'IIO', 'II/', 'VII']: 
					newProgStr = chords[1] + ' -> ' + chords[2]
					repeatProgs[newProgStr] = repeatProgs.setdefault(newProgStr, 0) + 1
					continue
			progStr = chords[1] + ' -> ' + chords[2]
		
		theTest = myGrammar.grammar_test(progStr)
		tempCount = working[modeIndex][progStr]
		
		if theTest is True:
			totalCounts += tempCount
		elif theTest is False:
			falseCounts += tempCount
			wrongies[myGrammar.newProgStr] = wrongies.setdefault(myGrammar.newProgStr, 0) + tempCount
	
	result = 100.0 * (totalCounts * 1.0)/max((totalCounts + falseCounts), 1)
	
	if printOut: 
		DT.print_dict(wrongies)
		print totalCounts, 'out of', totalCounts + falseCounts, result
		
	if not kwargs.get('three', True):
		tempCount = 0
		for item in wrongies:
			if item.upper().count('III') > 0:
				tempCount += wrongies[item]
		if printOut:
			print '     WITHOUT iii CHORD:', totalCounts, 'out of', totalCounts + + falseCounts - tempCount, 100.0 * (totalCounts * 1.0)/(totalCounts + falseCounts - tempCount)
	
	return result

def extras(i):
	global working, diatonicprogs
	for item in working[i]:
		if item not in diatonicprogs:
			print item, working[i][item]

pcDict = [{}, {}]

def make_pc_dict():
	global pcDict, working
	myKeys = [key.Key('C'), key.Key('c')]
	keyStrs = ['C', 'c']
	for modeInd in [0, 1]:
		for prog in working[modeInd]:
			symbols = prog.split(' -> ')
			pcs = []
			for sym in symbols:
				if sym not in pcDict[modeInd]:
					pcDict[modeInd][sym] = [x.pitchClass for x in roman.RomanNumeral(sym, keyStrs[modeInd]).pitches]	
	return

bassDict = [{}, {}]

def make_bass_dict():
	global bassDict, symbolDict, working, bassDictCounts
	bassDict = [{}, {}]
	bassDictCounts = [{}, {}]
	myKeys = [key.Key('C'), key.Key('c')]
	keyStrs = ['C', 'c']
	for modeInd in [0, 1]:
		for prog in working[modeInd]:
			symbols = prog.split(' -> ')
			sdProg = ''
			for sym in symbols:
				if sym in symbolDict[modeInd]:
					try:
						sdProg = sdProg + ' -> ' + symbolDict[modeInd][sym]
					except:
						print "ERROR", sdProg, symbolDict[modeInd][sym]
						return
				else:
					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
					degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.pitches[0])
					sdStr = str(degreePair[0])
					if degreePair[1]:
						accidentalSym = '+'
						i = int(degreePair[1].alter)
						if i < 0:
							accidentalSym = '-'
							i = i * -1
						sdStr = (accidentalSym * i) + sdStr
					symbolDict[modeInd][sym] = sdStr
					sdProg = sdProg + ' -> ' + sdStr
			if sdProg[0:4] == ' -> ': sdProg = sdProg[4:]
			if sdProg in bassDict[modeInd]:
				bassDict[modeInd][sdProg][prog] = counts[modeInd][prog]
			else:
				bassDict[modeInd][sdProg] = {prog: counts[modeInd][prog]}
		for item in bassDict[modeInd]:
			bassDictCounts[modeInd][item] = sum(bassDict[modeInd][item].values())		
	return

def make_bass_dict2():							# same as make_bass_dict but filters out repetitions
	global bassDict, bassDictCounts, symbolDict, counts
	bassDict = [{}, {}]
	bassDictCounts = [{}, {}]
	myKeys = [key.Key('C'), key.Key('c')]
	keyStrs = ['C', 'c']
	for modeInd in [0, 1]:
		for prog in counts[modeInd]:
			symbols = prog.split(' -> ')
			sdProg = ''
			lastBass = ''
			for sym in symbols:
				if sym in symbolDict[modeInd]:
					bass = symbolDict[modeInd][sym]
					if bass != lastBass:
						sdProg = sdProg + ' -> ' + bass
						lastBass = bass
				else:
					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
					degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.pitches[0])
					sdStr = str(degreePair[0])
					if degreePair[1]:
						accidentalSym = '+'
						i = int(degreePair[1].alter)
						if i < 0:
							accidentalSym = '-'
							i = i * -1
						sdStr = (accidentalSym * i) + sdStr
					symbolDict[modeInd][sym] = sdStr
					if sdStr != lastBass:
						sdProg = sdProg + ' -> ' + sdStr
						lastBass = sdStr
			if sdProg[0:4] == ' -> ': sdProg = sdProg[4:]
			if sdProg in bassDict[modeInd]:
				bassDict[modeInd][sdProg][prog] = counts[modeInd][prog]
			else:
				bassDict[modeInd][sdProg] = {prog: counts[modeInd][prog]}	
		for item in bassDict[modeInd]:
			bassDictCounts[modeInd][item] = sum(bassDict[modeInd][item].values())
	
	return

def five_six_five(mode = 'Major', printIt = True):					# does the 5-6 motion over the same bass ascend or descend?
	global bassDict, symbolDict, working, ascending, descending, outliers, tempDict
	modeInd = (mode[0:3].upper() == 'MIN')
	get_size(3)
	make_bass_dict()
	ascending = {}
	descending = {}
	outliers = {}
	totals = 0
	neighbors = 0
	totalCount = 0
	for prog in working[modeInd]:
		symbols = prog.split(' -> ')
		sym = [DT.parse_figure(x) for x in symbols]
		if (sym[0][1] == '' and sym[1][1] == '6' and symbolDict[modeInd][symbols[0]] == symbolDict[modeInd][symbols[1]]):
			totalCount += working[modeInd][prog]
			oldBass = abs(int(symbolDict[modeInd][symbols[0]]))
			newBass = abs(int(symbolDict[modeInd][symbols[2]]))
			if sym[2][1] == '' and (newBass - oldBass) % 7 in [1, 6]:
				if (newBass - oldBass) % 7 == 1:
					ascending[prog] = working[modeInd][prog]
				elif (newBass - oldBass) % 7 == 6:
					descending[prog] = working[modeInd][prog]
			else:
				if sym[2][1] == '' and newBass == oldBass:
					neighbors += working[modeInd][prog]
				else:
					outliers[prog] = working[modeInd][prog]
					
	if printIt:
		print "============= Descending ============="
		DT.print_dict(descending)
		print "============= Ascending ============="
		DT.print_dict(ascending)
		print "============= Outliers ============="
		DT.print_dict(outliers)
	return [sum(descending.values()), sum(ascending.values()), neighbors, totalCount]
				
def asymmetry(mode = 'Major'):
	global bassDict, symbolDict, working, ascending, descending, tempDict
	modeInd = (mode[0:3].upper() == 'MIN')
	get_size(2)
	make_bass_dict()
	ascending = {}
	descending = {}
	totals = 0
	descending_count = 0
	for prog in working[modeInd]:
		symbols = prog.split(' -> ')
		sym1 = DT.parse_figure(symbols[0])
		sym2 = DT.parse_figure(symbols[1])
		if (sym1[1] == '' and sym2[1] == '6') or (sym1[1] == '6' and sym2[1] == ''):
			if symbolDict[modeInd][symbols[0]] == symbolDict[modeInd][symbols[1]]:
				totals += working[modeInd][prog]
				if sym2[1] == '6':
					descending[prog] = working[modeInd][prog]
					descending_count += working[modeInd][prog]
				else:
					ascending[prog] = working[modeInd][prog]
	print "=========================", "5 -> 6"
	tempDict = {}
	for item in descending:
		tempList = [descending[item], 0]
		theChords = item.split(' -> ')
		theChords.reverse()
		newKey = ' -> '.join(theChords)
		if newKey in ascending:
			tempList[1] = ascending[newKey]
		tempDict[item] = tempList
	newKeys = sorted(list(tempDict), key = lambda x: -100.0*tempDict[x][0] /sum(tempDict[x]))
	for item in newKeys:
		print item, tempDict[item]
	numerator = sum(x[0] for x in tempDict.values())
	finalSum = sum(x[1] for x in tempDict.values())
	return [numerator, finalSum]
	"""DT.print_dict(descending)	
	print "=========================", "6 -> 5"
	DT.print_dict(ascending)	
	print "=========================", 100.0 * (1.0 * descending_count/totals)"""

def rank_bass_motions(removeDuplicates = True, printIt = True):
	global bassDict, rankedDict
	rankedDict = [{},{}]
	for modeInd in [0]:
		for item in bassDict[modeInd]:
			rankedDict[modeInd][item] = sum(bassDict[modeInd][item].values())
		print ['MAJOR', 'MINOR'][modeInd]
		if removeDuplicates:
			delList = []
			for item in rankedDict[modeInd]:
				s = item.split(' -> ')
				if len(s) > 1:
					deleteFlag = True
					for i in range(1, len(s)):
						if s[i] != s[0]:
							deleteFlag = False
					if deleteFlag:
						delList.append(item)
			for thing in delList:
				del rankedDict[modeInd][thing]
		if printIt: 
			DT.print_dict(rankedDict[modeInd], pct=True)

def bass_dict(size = 1, printResults = False):
	global maxValues
	get_size(size)
	make_bass_dict()
	maxValues = [{}, {}]
	for modeInd in [0, 1]:
		for sdProg in bassDict[modeInd]:
			tempDict = bassDict[modeInd][sdProg]
			maxVal = max(tempDict.iteritems(), key=operator.itemgetter(1))
			maxValues[modeInd][maxVal[0]] = int((100. * maxVal[1]/sum(tempDict.values())) + .5)
	if printResults:
		print 'MAJOR'
		DT.print_dict(maxValues[0])
		print 'MINOR'
		DT.print_dict(maxValues[1])

comps = DT.comps

def degrees(degStr, comp = '', modeInd = 0, diatonic = True):
	global bassDict, comps
	if type(comp) is str:
		if comp:
			comps = [comp]
	for comp in comps:
		load(comp)
		print "COMPOSER:", comp
		get_size(degStr.count('->') + 1)
		make_bass_dict()
		try:
			tempDict = copy.deepcopy(bassDict[modeInd][degStr])
		except:
			continue
		delList = []
		if diatonic:
			for item in tempDict:
				rns = item.split(' -> ')
				cont = True
				for rn in rns:
					if DT.parse_figure(rn)[2]:
						cont = False
						delList.append(item)
						break
				if not cont: continue
			for item in delList:
				del(tempDict[item])
		DT.print_dict(tempDict, pct = True)

# def four_three():
# 	for c in comps:
# 		print c
# 		for modeInd in ['major','minor']:
# 			print "   ", modeInd
# 			modeInd = int(modeInd == 'minor')
# 			load(c)
# 			get_size(1)
# 			contains('4/3', modeInd)

# """def pct(sym, modeInd = 0):
# 	get_size(1)
# 	myCount = 0
# 	for testSym in DT._DIATONICMAJOR:
# 		parsedSym = DT.parse_figure(testSym)
# 		if parsedSym[2]: continue
# 		newSym = parsedSym[0].replace('maj', '').replace('/o', 'o')
# 		if newSym == sym and testSym in working[modeInd]: myCount += working[modeInd][testSym]
# 	return int(0.5 + (100.0 * myCount/DT.sum_dict(working[modeInd])))"""

# with open(DT._DATAPATH + 'MASTERRNROOTDICT', 'rb') as myFile:
# 	rootSymbolDict = pickle.load(myFile)			

# symbolDict = [{}, {}]
# inversionReport = [{}, {}, {}, {}, {}, {}, {}, {}]

# def inversion_report(mode = 'major', useBass = True):
# 	global rootSymbolDict, symbolDict, inversionReport
# 	inversionReport = [{}, {}, {}, {}, {}, {}, {}, {}]
# 	modeInd = int(mode[0:3].upper() == 'MIN')
# 	get_size(2)
# 	if useBass:
# 		myDict = symbolDict
# 		make_bass_dict()
# 	else:
# 		myDict = rootSymbolDict
# 		make_root_dict()
# 	for prog in working[modeInd]:
# 		symbols = prog.split(' -> ')
# 		analyzedSymbols = [DT.parse_figure(x) for x in symbols]
# 		if useBass:
# 			roots = [abs(int(myDict[modeInd][x])) for x in symbols]
# 			rootProg = (roots[1] - roots[0]) % 7
# 		else:
# 			roots = [myDict[modeInd][x][0] for x in symbols]
# 			rootProg = (roots[1] - roots[0]) % 7
# 		if analyzedSymbols[0][1] != '6' and analyzedSymbols[1][1] != '6': continue
# 		#print prog, '\t', working[modeInd][prog], '\t', rootProg
# 		inversionReport[rootProg][prog] = working[modeInd][prog]
# 	for i in range(7):
# 		print "ROOT PROGRESSION", i, sum(inversionReport[i].values())
# 	for i in range(7):
# 		print "ROOT PROGRESSION", i
# 		DT.print_dict(inversionReport[i])

# def scale_degree_root_from_rn(s):
# 	newS = s.upper()
# 	s = s.replace('N', 'II').replace('Ger', 'VI').replace('Fr', 'II').replace('It', 'IV')


# def make_root_dict(bassProgs = False, requireInversions = False):		# requireInversions is a list of required inversions
# 	"""Requireinversions is a list of required inversions ... e.g. ['6', '6'] which gives only first inversion triads, '*' is a wildcard """
# 	global rootDict, rootCounts, rootSymbolDict, working, cleanCounts, tempDict
# 	rootDict = [{}, {}]
# 	rootCounts = [{}, {}]
# 	cleanCounts = [{}, {}]
# 	tempDict = {}
# 	myKeys = [key.Key('C'), key.Key('c')]
# 	keyStrs = ['C', 'c']
# 	for modeInd in [0, 1]:
# 		for prog in working[modeInd]:
# 			symbols = prog.split(' -> ')
# 			parsedSymbols = [DT.parse_figure(x) for x in symbols]
# 			if requireInversions:
# 				breakOff = False
# 				for i in range(len(requireInversions)):
# 					if (requireInversions[i] != '*') and (parsedSymbols[i][1] != requireInversions[i]): 
# 						breakOff = True
# 						break
# 				if breakOff: continue
# 			sdProg = ''
# 			firstSym = -1
# 			for sym in symbols:
# 				if sym in rootSymbolDict[modeInd]:
# 					if firstSym == -1:
# 						firstSym = rootSymbolDict[modeInd][sym] 
# 					newSd = [(rootSymbolDict[modeInd][sym][0] - firstSym[0]) % 7, rootSymbolDict[modeInd][sym][1] - firstSym[1]]
# 					if newSd[1] == 0: newSd = newSd[0]
# 					sdProg = sdProg + ' -> ' + str(newSd)
# 				else:
# 					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
# 					if bassProgs:
# 						degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.pitches[0])
# 					else:
# 						degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.root())
# 					if degreePair[1]:
# 						newDP = [degreePair[0], int(degreePair[1].alter)]
# 						rootSymbolDict[modeInd][sym] = newDP
# 					else:
# 						newDP = [degreePair[0], 0]
# 						rootSymbolDict[modeInd][sym] = newDP
# 						degreePair = [degreePair[0], 0]
# 					if firstSym == -1:
# 						firstSym = newDP
# 					newSd = [(newDP[0] - firstSym[0]) % 7, newDP[1] - firstSym[1]]
# 					if newSd[1] == 0: newSd = newSd[0]
# 					sdProg = sdProg + ' -> ' + str(newSd)
# 			if sdProg[0:4] == ' -> ': sdProg = sdProg[4:]
# 			if sdProg == '0 -> 1' and modeInd == 0:										# get rid of this
# 				tempDict[prog] = counts[modeInd][prog]					# ditto
# 			if sdProg in rootDict[modeInd]:
# 				rootDict[modeInd][sdProg][prog] = counts[modeInd][prog]
# 			else:
# 				rootDict[modeInd][sdProg] = {prog: counts[modeInd][prog]}	
# 	for modeInd in [0, 1]:
# 		for item in rootDict[modeInd]:
# 			rootCounts[modeInd][item] = sum(rootDict[modeInd][item].values())
# 	for modeInd in [0, 1]:
# 		for dest in range(1, 7):
# 			newKey = '0 -> ' + str(dest)
# 			if newKey in rootCounts[modeInd]:
# 				cleanCounts[modeInd][newKey] = rootCounts[modeInd][newKey]
# 			else:
# 				cleanCounts[modeInd][newKey] = 0
# 	DT.print_dict(tempDict)
# 	with open(DT._DATAPATH + 'MASTERRNROOTDICT', 'w+') as myFile:
# 		pickle.dump(rootSymbolDict, myFile)												# ditto
# 	return

# def rock_roots(matchProg = ''):
# 	global rootDict, rootCounts, symbolDict, working, cleanCounts, finalCounts
# 	rootDict = [{}, {}]
# 	rootCounts = [{}, {}]
# 	cleanCounts = [{}, {}]
# 	finalCounts = [{}, {}]
# 	symbolDict = [{}, {}]
# 	myKeys = [key.Key('C'), key.Key('c')]
# 	keyStrs = ['C', 'c']
# 	get_size(2)
# 	for modeInd in [0, 1]:
# 		for prog in working[modeInd]:
# 			recordFlag = True
# 			symbols = prog.split(' -> ')
# 			sdProg = ''
# 			firstSym = -1
# 			#print prog
# 			for sym in symbols:
# 				parsedSym = DT.parse_figure(sym)
# 				#print '    ', sym, parsedSym
# 				if (not parsedSym[0].isupper()) or (parsedSym[1] in ['7', '6/5', '4/3', '2']) or parsedSym[0].count('+') > 0:
# 					#print "here!", sym, parsedSym
# 					recordFlag = False
# 					break
# 				if sym in symbolDict[modeInd]:
# 					sdProg = sdProg + ' -> ' + str(symbolDict[modeInd][sym])
# 				else:
# 					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
# 					myRoot = RN.root().pitchClass
# 					symbolDict[modeInd][sym] = myRoot
# 					sdProg = sdProg + ' -> ' + str(myRoot)
# 			if recordFlag:
# 				if sdProg[0:4] == ' -> ': sdProg = sdProg[4:]
# 				if sdProg == matchProg: print prog, counts[modeInd][prog]
# 				if sdProg in rootDict[modeInd]:
# 					rootDict[modeInd][sdProg] += counts[modeInd][prog]
# 				else:
# 					rootDict[modeInd][sdProg] = counts[modeInd][prog]	
# 	for modeInd in [0, 1]:
# 		for item in rootDict[modeInd]:
# 			ints = [int(x) for x in item.split(' -> ')]
# 			interval = (ints[1] - ints[0]) % 12
# 			cleanCounts[modeInd][interval] = cleanCounts[modeInd].setdefault(interval, 0) + rootDict[modeInd][item]
# 	for modeInd in [0, 1]:
# 		finalCounts[modeInd][1] = cleanCounts[modeInd].setdefault(1, 0) + cleanCounts[modeInd].setdefault(11, 0)
# 		finalCounts[modeInd][2] = cleanCounts[modeInd].setdefault(2, 0) + cleanCounts[modeInd].setdefault(10, 0)
# 		finalCounts[modeInd][3] = cleanCounts[modeInd].setdefault(3, 0) + cleanCounts[modeInd].setdefault(9, 0)
# 		finalCounts[modeInd][4] = cleanCounts[modeInd].setdefault(4, 0) + cleanCounts[modeInd].setdefault(8, 0)
# 		finalCounts[modeInd][5] = cleanCounts[modeInd].setdefault(5, 0) + cleanCounts[modeInd].setdefault(7, 0)
# 		finalCounts[modeInd][6] = cleanCounts[modeInd].setdefault(6, 0)
# 	print "MAJOR", DT.sort_dict(finalCounts[0])
# 	print "MINOR", DT.sort_dict(finalCounts[1])
# 	combinedCounts = {}
# 	for item in finalCounts[0]:
# 		combinedCounts[item] = finalCounts[0][item] +  finalCounts[1][item]
# 	print "COMBINED", DT.sort_dict(combinedCounts)
# 	return

# def nondiatonic():
# 	global rootDict, rootCounts, symbolDict, working, cleanCounts, finalCounts
# 	rootDict = [{}, {}]
# 	rootCounts = [{}, {}]
# 	cleanCounts = [{}, {}]
# 	finalCounts = [{}, {}]
# 	symbolDict = [{}, {}]
# 	myKeys = [key.Key('C'), key.Key('c')]
# 	keyStrs = ['C', 'c']
# 	get_size(2)
# 	for modeInd in [0, 1]:
# 		keyPCs = set([x.pitchClass for x in myKeys[modeInd].pitches])
# 		for prog in working[modeInd]:
# 			recordFlag = False
# 			symbols = prog.split(' -> ')
# 			sdProg = ''
# 			firstSym = -1
# 			for sym in symbols:
# 				"""parsedSym = DT.parse_figure(sym)
# 				if (not parsedSym[0].isupper()) or (parsedSym[1] in ['7', '6/5', '4/3', '2']) or parsedSym[0].count('+') > 0:
# 					recordFlag = False
# 					break"""
# 				if sym in symbolDict[modeInd]:
# 					if (symbolDict[modeInd][sym]): 							# true if nondiatonic, false if diatonic
# 						recordFlag = True
# 				else:
# 					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
# 					myPCs = set(RN.pitchClasses)
# 					if len(myPCs & keyPCs) < len(myPCs):
# 						symbolDict[modeInd][sym] = True
# 						recordFlag = True
# 					else:
# 						symbolDict[modeInd][sym] = False
# 			if recordFlag:
# 				rootDict[modeInd][prog] = counts[modeInd][prog]	
# 	return

# def consecutive_inversions(modeInd = 0):
# 	global results
# 	results = {}
# 	get_size(4)
# 	for item in working[modeInd]:
# 		figures = item.split(' -> ')
# 		if figures.count('V/') > 0: 
# 			continue
# 		#print figures, figures.count('V/')
# 		for i in range(len(figures)):
# 			figures[i] = DT.parse_figure(figures[i])
# 		if figures[0][1] != '6' and figures[3][1] != '6' and figures[1][1] == '6' and figures[2][1] == '6':
# 			results[item] = working[modeInd][item]
# 	DT.print_dict(results)

# def approaching_interval(modeInd = 0, index = 1):
# 	global results, working
# 	results = {'5/3': {}, '6': {}, '6/4': {}}
# 	get_size(2)
# 	make_bass_dict()
# 	for item in working[modeInd]:
# 		figures = item.split(' -> ')
# 		if figures[0] == figures[1]:
# 			continue
# 		if figures.count('V/') > 0: 
# 			continue
# 		sd1 = int(symbolDict[modeInd][figures[0]].lstrip('+-'))
# 		sd2 = int(symbolDict[modeInd][figures[1]].lstrip('+-'))
# 		myInt = (sd2 - sd1) % 7
# 		inv = DT.parse_figure(figures[index])[1]
# 		if inv == '':
# 			inv = '5/3'
# 		elif inv != '6' and inv != '6/4':
# 			continue
# 		if inv == '6' and (myInt == 3 or myInt == 4):
# 			if myInt == 3:
# 				print '     ', item, working[modeInd][item]
# 			else:
# 				print item, working[modeInd][item]
# 		results[inv][myInt] = results[inv].setdefault(myInt, 0) + working[modeInd][item]
# 	return results

# def approached_and_left_by_leap(modeInd = 0):
# 	global results, working
# 	results = {}
# 	get_size(3)
# 	make_bass_dict()
# 	for item in working[modeInd]:
# 		figures = item.split(' -> ')
# 		if figures[0] == figures[1] or figures[1] == figures[2]:
# 			continue
# 		if figures.count('V/') > 0: 
# 			continue
# 		sd1 = int(symbolDict[modeInd][figures[0]].lstrip('+-'))
# 		sd2 = int(symbolDict[modeInd][figures[1]].lstrip('+-'))
# 		sd3 = int(symbolDict[modeInd][figures[2]].lstrip('+-'))
# 		myInt1 = (sd2 - sd1) % 7
# 		myInt2 = (sd3 - sd2) % 7
# 		inv = DT.parse_figure(figures[1])[1]
# 		if inv != '6' and inv != '6/4':
# 			continue
# 		if myInt1 in [0, 1, 5, 6] or myInt2 in [0, 1, 5, 6]:
# 			continue
# 		results[item] = results.setdefault(item, 0) + working[modeInd][item]
# 	DT.print_dict(results)
# 	return

# def count_all():
# 	counter = 0
# 	for c in comps:
# 		load(c)
# 		get_size(1)
# 		i, j, k = count()
# 		counter += k
# 	print counter

# def count_chords(composerName = '', mode = ''):
# 	if composerName: load(composerName)
# 	get_size(1, fauxbourdon = True)
# 	if mode:
# 		modeInd = int(mode[0:2].upper() == 'MI')
# 		return sum(working[modeInd].values())
# 	return sum(working[0].values()) + sum(working[1].values())

# def count():
# 	return DT.sum_dict(working[0]), DT.sum_dict(working[1]), DT.sum_dict(working[0]) + DT.sum_dict(working[1])

# """def pct(myStr, modeInd = 0):
# 	totals = DT.sum_dict(working[modeInd])
# 	pct = '%.1f' % ((working[modeInd][myStr] * 100.)/totals)
# 	return pct"""
	

# def graph(myInts = -1, modeInd = 0):
# 	global bassDictCounts
# 	if myInts == -1:
# 		myInts = [1, 2, 3]
# 	else:
# 		myInts = [myInts]
# 	intLabels = ['unison', 'second', 'third', 'fourth']
# 	plt.xlabel('Starting Degree')
# 	plt.ylabel('Intervals of step size X')
# 	plt.title('Proportion of melodic degrees')
# 	labels = []
# 	for myInt in myInts:
# 		for j in [-1, 1]:
# 			values = []
# 			if j == -1:
# 				myLabel = 'descending ' + intLabels[myInt]
# 			else:
# 				myLabel = 'ascending ' + intLabels[myInt]
# 			labels.append(myLabel)
# 			for i in range(1, 8):
# 				myKey = str(i) + ' -> ' + str((((i - 1) + (j * myInt)) % 7) + 1)
# 				if myKey in bassDictCounts[modeInd]:
# 					values.append(bassDictCounts[modeInd][myKey])
# 				else:
# 					values.append(0)
# 			plt.plot(values, label = myLabel)
# 	ticks = range(0, 7)
# 	myLeg = plt.legend(tuple(labels), loc=0)
# 	for i in range(len(myLeg.legendHandles)):
# 		myLeg.legendHandles[i].set_linewidth(2.0)
# 	plt.xticks(ticks, [x + 1 for x in ticks])
# 	plt.show()
	

# def ascending_fifths(bassProgs = False, descendingSteps = False):
# 	global rootDict, rootCounts, symbolDict, working, cleanCounts
# 	tempPct = []
# 	rootDict = [{}, {}]
# 	rootCounts = [{}, {}]
# 	cleanCounts = [{}, {}]
# 	symbolDict = [{}, {}]
# 	myKeys = [key.Key('C'), key.Key('c')]
# 	keyStrs = ['C', 'c']
# 	remove_inversions(printIt = False, separateSixFour = False)
# 	get_size(2)
# 	for modeInd in [0, 1]:
# 		for prog in reduced[modeInd]:
# 			symbols = prog.split(' -> ')
# 			sdProg = ''
# 			firstSym = -1
# 			for sym in symbols:
# 				if sym in symbolDict[modeInd]:
# 					if firstSym == -1:
# 						firstSym = symbolDict[modeInd][sym] 
# 					newSd = [(symbolDict[modeInd][sym][0] - firstSym[0]) % 7, symbolDict[modeInd][sym][1] - firstSym[1]]
# 					if newSd[1] == 0: newSd = newSd[0]
# 					sdProg = sdProg + ' -> ' + str(newSd)
# 				else:
# 					RN = roman.RomanNumeral(sym, keyStrs[modeInd])
# 					if bassProgs:
# 						degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.pitches[0])
# 					else:
# 						degreePair = myKeys[modeInd].getScaleDegreeAndAccidentalFromPitch(RN.root())
# 					if degreePair[1]:
# 						newDP = [degreePair[0], int(degreePair[1].alter)]
# 						symbolDict[modeInd][sym] = newDP
# 					else:
# 						newDP = [degreePair[0], 0]
# 						symbolDict[modeInd][sym] = newDP
# 						degreePair = [degreePair[0], 0]
# 					if firstSym == -1:
# 						firstSym = newDP
# 					newSd = [(newDP[0] - firstSym[0]) % 7, newDP[1] - firstSym[1]]
# 					if newSd[1] == 0: newSd = newSd[0]
# 					sdProg = sdProg + ' -> ' + str(newSd)
# 			if sdProg[0:4] == ' -> ': sdProg = sdProg[4:]
# 			if (not descendingSteps and sdProg == '0 -> 4') or (descendingSteps and sdProg == '0 -> 6'):
# 				rootDict[modeInd][prog] = reduced[modeInd][prog]	
# 	for modeInd in [0, 1]:
# 		#DT.print_dict(rootDict[modeInd])
# 		print ['Major','Minor'][modeInd]
# 		clean = 0 
# 		for item in rootDict[modeInd]:
# 			tempVar = rootDict[modeInd][item]
# 			item = item.upper().replace('MAJ', '').replace('/O', '').replace('O', '')
# 			if (not descendingSteps and item in ['IV -> I', 'I -> V']) or (descendingSteps and item in ['VI -> V', 'I -> VII']):
# 				#print "here"
# 				clean += tempVar
# 		try:
# 			tempPct.append(100.0 * clean/sum(rootDict[modeInd].values()))
# 		except:
# 			tempPct.append(0)		
# 	#print tempPct
# 	return tempPct

# def pct(chords = [], mode = 'major'):
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	if not chords:
# 		chords = DT._DIATONICMAJOR
# 	get_size(1)
# 	toDelete = []
# 	for item in working[modeInd]:
# 		parsedFig = DT.parse_figure(item)
# 		if parsedFig[2]:
# 			toDelete.append(item)
# 	for item in toDelete:
# 		del working[modeInd][item]
# 	totalSum = DT.sum_dict(working[modeInd])
# 	totalPCT = 0
# 	finalDict = {}
# 	for i in range(7):
# 		#if i == 2: continue
# 		for j in [0, 1, 2]:
# 			#if i == 5 and j == 1: continue
# 			#if i == 6 and j == 0: continue
# 			tempSum = 0
# 			for theChord in [chords[(i*7) + j], chords[(i*7) + j + 3]]:
# 				if theChord in working[modeInd]:
# 					tempSum += working[modeInd][theChord]
# 			finalDict[chords[i*7 + j]] = tempSum
# 			totalPCT += tempSum
# 	for item in finalDict:
# 		print item, finalDict[item] * 100./totalPCT

# def chord_histogram(mode='major', inversions = True, addChords = []):
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	myChords = DT._DIATONIC[modeInd] + addChords
# 	get_size(1)
# 	tempDict = working[modeInd]
# 	outDict = {}
# 	totals = 0
# 	if inversions:
# 		firstList = [0, 1]			# split out root pos and first inversion
# 		secondList = [0, 3]
# 	else:
# 		firstList = [0]
# 		secondList = [0, 1, 2, 3, 4, 5, 6]
# 	for i in range(len(myChords)):
# 		if (i % 7) in firstList:
# 			myCount = 0
# 			for j in secondList:
# 				if i + j > len(myChords) - 1:
# 					continue
# 				item = myChords[i + j]
# 				if item in tempDict:
# 					totals += tempDict[item]
# 					myCount += tempDict[item]
# 			outDict[myChords[i]] = myCount
# 	for item in outDict:
# 		outDict[item] = 100.*outDict[item]/totals
# 	return DT.sort_dict(outDict)
	

# def reversible(mode='major', inversions = True, thresh = 1.0):
# 	global outDict
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	if not inversions:
# 		remove_inversions()
# 	get_size(2)
# 	tempDict = copy.deepcopy(working[modeInd])
# 	totalSum = DT.sum_dict(tempDict)
# 	outDict = {}
# 	for item in tempDict:
# 		myChords = item.split(" -> ")
# 		reversedItem = myChords[1] + ' -> ' + myChords[0]
# 		if reversedItem in outDict or item in outDict: continue
# 		if reversedItem not in tempDict:
# 			if 100.0*tempDict[item]/totalSum < thresh: continue
# 			ratio = 100.0
# 		else:
# 			if 100.0 * (tempDict[item] + tempDict[reversedItem])/totalSum < thresh: continue
# 			ratio = 100.0 * tempDict[item]/(tempDict[item] + tempDict[reversedItem])
# 		if ratio >= 50:
# 			outDict[item] = ratio
# 		else:
# 			outDict[reversedItem] = 100 - ratio
# 	outDict = DT.sort_dict(outDict)
# 	for item in outDict: print item

# def replace_values_with_percentages(myDict):
# 	theSum = sum(myDict.values())
# 	for myChord in myDict:
# 		myDict[myChord] = 100.*myDict[myChord]/theSum

# def propensity(progStr = 'IV -> ', mode='major', removeInversions = True, separateSixFour = False, printDeltas = False):
# 	global deltas
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	theChords = progStr.split(' -> ')
# 	if theChords[0] == '':
# 		penult = 1
# 	else:
# 		penult = -2
# 	if removeInversions:
# 		remove_inversions(separateSixFour = separateSixFour)	
# 	get_size(1, useReduced=removeInversions)
# 	chordCounts = {}
# 	for myChord in working[modeInd]:
# 		if myChord != theChords[penult]:												# peel off chord repeats
# 			chordCounts[myChord] = working[modeInd][myChord]
# 	replace_values_with_percentages(chordCounts)
# 	#DT.print_dict(chordCounts)
# 	get_size(progStr.count('->') + 1, useReduced = removeInversions)
# 	tempCounts = {}
# 	for item in working[modeInd]:
# 		if penult == 1:
# 			if item[-1 * len(progStr):] != progStr: continue
# 		else:
# 			if item[:len(progStr)] != progStr: continue							
# 		tempCounts[item.replace(progStr, '')] = working[modeInd][item]
# 	replace_values_with_percentages(tempCounts)
# 	#DT.print_dict(tempCounts)
# 	deltas = {}
# 	for item in chordCounts:
# 		if item in tempCounts:
# 			deltas[item] = tempCounts[item] - chordCounts[item]
# 		else:
# 			deltas[item] = -1 * chordCounts[item]
# 	if printDeltas: DT.print_dict(deltas)
# 	maxVal = max(deltas.values())
# 	minVal = min(deltas.values())
# 	maxKey = 0
# 	minKey = 0
# 	for item in deltas:
# 		if deltas[item] == maxVal: maxKey = item
# 		elif deltas[item] == minVal: minKey = item
# 	return [[maxKey, maxVal], [minKey, minVal]]
	
# def survey_propensities(progStr, mode='major', printDeltas=True):
# 	for c in DT.comps:
# 		print c
# 		load(c)
# 		x = propensity(progStr, mode, printDeltas = printDeltas)	
# 		for chord in x: print chord

# def listall(s, mode='major', removeInversions = True, fauxbourdon = False, separateSixFour = False, delete = []):
# 	modeInd = int(mode[:2].upper() == 'MI')
# 	for c in DT.comps:
# 		print c
# 		load(c)
# 		remove_inversions(separateSixFour = separateSixFour)
# 		get_size(s.count('->') + 1, fauxbourdon = fauxbourdon, useReduced=removeInversions)				#get fauxbourdon out of here somehow
# 		for item in delete:
# 			if item in working[modeInd]:
# 				del working[modeInd][item]
# 		if s[-3:] == '-> ':
# 			starts(s, mode=mode, pct = True)
# 		else:
# 			ends(s, mode=mode, pct = True)

# def major_and_minor(mode = 'MAJOR'):
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	get_size(1)
# 	majorTriads = 0
# 	minorTriads = 0
# 	for sym in working[modeInd]:
# 		parsedSym = DT.parse_figure(sym)
# 		if (parsedSym[1] in ['7', '6/5', '4/3', '2']) or parsedSym[3] or parsedSym[0].count('+') > 0 or parsedSym[0].count('o') > 0:
# 			continue
# 		testSym = parsedSym[0].replace('b', '')
# 		if testSym.isupper():
# 			majorTriads += working[modeInd][sym]
# 		elif testSym.islower():
# 			minorTriads += working[modeInd][sym]
# 	if majorTriads + minorTriads != 0:
# 		return 100.*majorTriads/(majorTriads + minorTriads)
# 	else:
# 		return 0
		
# def entropy(mode = 'MAJOR', removeInversions = True, killSixFour = True, forward = True, filterRare = True, filterDiatonic = True):
# 	global entropies
# 	modeInd = int(mode[0:2].upper()=='MI')
# 	if removeInversions:
# 		remove_inversions(filterDiatonic = filterDiatonic)
# 		if killSixFour:
# 			kill_64()
# 	get_size(1, useReduced = removeInversions)
# 	mySyms = copy.deepcopy(working[modeInd])
# 	entropies = {}
# 	for mySym in mySyms:
# 		get_size(2, useReduced = removeInversions)
# 		if killSixFour:
# 			kill_64()
# 		if forward:
# 			starts(mySym + ' ->', source=working[modeInd], printIt = False, pct = True)
# 		else:
# 			ends('-> ' + mySym, source=working[modeInd], printIt = False, pct = True)
# 		entropies[mySym] = DT.dict_entropy(tempList)
# 	if filterRare:
# 		k = sorted([x for x in entropies.keys() if entropies[x] > .001], key = lambda x: entropies[x])
# 		for i in k:
# 			print i, entropies[i]
# 	else:
# 		DT.print_dict(entropies)

# def kill_64():
# 	for modeInd in [0, 1]:
# 		delList = []
# 		for item in reduced[modeInd]:
# 			if item.count('6/4') > 0:
# 				delList.append(item)
# 		for item in delList:
# 			del reduced[modeInd][item]

# def group_V():
# 	global counts
# 	outDicts = [{}, {}]
# 	for modeInd in [0, 1]:
# 		for item in counts[modeInd]:
# 			out = []
# 			mySyms = item.split(' -> ')
# 			i = -1
# 			for i in range(0, len(mySyms) - 1):
# 				if (mySyms[i] == 'V' and mySyms[i + 1] == 'V7') or (mySyms[i] == 'V6' and mySyms[i + 1] == 'V6/5') or (mySyms[i] == 'V6/4' and mySyms[i + 1] == 'V4/3') or (mySyms[i] == 'V' and mySyms[i + 1] == 'V2'):
# 					pass
# 				else:
# 					out.append(mySyms[i])
# 			out.append(mySyms[i + 1])
# 			newKey = ' -> '.join(out)
# 			outDicts[modeInd][newKey] = outDicts[modeInd].setdefault(newKey, 0) + counts[modeInd][item]
# 	counts = outDicts


# def fix_all_V7():
# 	for i in [0, 1]:
# 		for c in counts[i].keys():
# 			if c.count('V -> V7') == 0 and c.count('V6 -> V6/5') == 0: continue
# 			newC = c.replace('V -> V7', 'V7').replace('V6 -> V6/5', 'V6/5')
# 			print c, newC, counts[i].get(newC, 0), counts[i][c]
# 			counts[i][newC] = counts[i].get(newC, 0) + counts[i][c]
# 			del counts[i][c]
		
		
# def tendency(progLen = 2, modeInd = 0, orderParam = 1, printPct = 3, useReduced = False, filterGrammar = False):			#compares simulated probabiities to actual
# 	"""Updated this to use percentages, so you can compare different composers"""
# 	global results
# 	if useReduced:
# 		remove_inversions()
# 	results = {}
# 	rawString = []
	
# 	get_size(progLen, useReduced = useReduced)
# 	tempColl = normalize_dict(working[modeInd])
	
# 	get_size(progLen - orderParam, useReduced = useReduced)
# 	firstColl = normalize_dict(working[modeInd])
	
# 	get_size(orderParam, useReduced = useReduced)
# 	secondColl = normalize_dict(working[modeInd])										# how many of the first-order lengths are there?
	
# 	#print sum(firstColl.values()), sum(secondColl.values()), sum(tempColl.values())
	
# 	expectedSum = 0.
# 	actualSum = 0
# 	for s in tempColl:
# 		expected = calcstring(s, orderParam, firstColl, secondColl)
# 		expectedSum += expected
	
# 	print expectedSum
	
# 	newExpectedSum = 0
# 	for s in tempColl:
# 		expected = calcstring(s, orderParam, firstColl, secondColl) / expectedSum
# 		newExpectedSum += expected
# 		actual = tempColl[s]
# 		actualSum += actual
# 		"""NEED TO FIX THIS HERE"""
# 		print(s, round(actual, 2), round(expected, 2))
# 		results[s] = (actual - expected)
# 		#results[s] = (actual - expected)/max(float(expected), .0000001)
# 	resultsKeys = sorted(results.keys(), key = lambda x: -results[x])
# 	resultsLen = int(len(resultsKeys) * printPct / 200.)
# 	if resultsLen > len(resultsKeys) / 2.: resultsLen = len(resultsKeys) / 2
# 	if filterGrammar:
# 		myGrammar = GrammarObject()
# 		for s in resultsKeys[:resultsLen] + resultsKeys[-resultsLen:]:
# 			theTest = myGrammar.grammar_test(s)
# 			if (theTest is not False):						# want to see non grammatical progressions that are positive
# 				print s, '%.2f' % (100.*results[s])
# 	else:
# 		for s in resultsKeys[:resultsLen] + resultsKeys[-resultsLen:]:
# 			print s, '%.2f' % (100.*results[s])
# 	print "EXCPECTED SUM", newExpectedSum, "ACTUAL SUM", actualSum

# def calcstring(inStr, orderParam = 1, firstColl = None, secondColl = None):
# 	s = inStr.split(' -> ')
# 	firstSym = ' -> '.join(s[0:-orderParam])
# 	secondSym = ' -> '.join(s[-orderParam:])
# 	return firstColl.get(firstSym, 0) * secondColl.get(secondSym, 0)

# def rock_and_classical(c1 = 'Rock', c2 = 'Mozart', mode = 'major', size = 2, printPct = 33):
# 	global results
# 	results = {}
# 	modeInd = (mode.upper()[:3] == 'MIN')
# 	load(c1)
# 	remove_inversions()
# 	get_size(size, useReduced = True)
# 	tempColl = copy.deepcopy(working[modeInd])
# 	t1 = sum(tempColl.values()) / 100.
# 	load(c2)
# 	remove_inversions()
# 	get_size(size, useReduced = True)
# 	t2 = sum(working[modeInd].values()) / 100.
# 	for item in working[modeInd]:
# 		if item in tempColl:
# 			results[item] = working[modeInd][item]/t2 - tempColl[item]/t1
# 		else:
# 			results[item] = working[modeInd][item]/t2
# 	resultsKeys = sorted(results.keys(), key = lambda x: -results[x])
# 	resultsLen = int(len(resultsKeys) * printPct / 200.)
# 	if resultsLen > len(resultsKeys) / 2.: resultsLen = len(resultsKeys) / 2
# 	for s in resultsKeys[:resultsLen] + resultsKeys[-resultsLen:]:
# 		print s, "%.2f" % results[s]
	
# def rank(myProg, mode = 'major'):
# 	get_size(myProg.count("->") + 1)
# 	modeInd = (mode.upper()[:3] == 'MIN')
# 	theCount = working[modeInd][myProg]
# 	print myProg, "is number", sorted(working[modeInd].values(), reverse = True).index(theCount) + 1, "out of", len(working[modeInd].values()), "progressions"

# theTriads = ['I', 'iii', 'V', 'viio', 'ii', 'IV', 'vi']

# def root_function(correlateChord = 'IV', comparisonChord = '', mode = 'major'):
# 	theTriads = ['I', 'iii', 'V', 'viio', 'ii', 'IV', 'vi']
# 	rootVec = [0] * len(theTriads)
# 	firstInversionVec = [0] * len(theTriads)
# 	get_size(2)
# 	modeInd = (mode.upper()[:3] == 'MIN')
# 	if not comparisonChord: comparisonChord = correlateChord + '6'
# 	for p in working[modeInd]:
# 		theCount = working[modeInd][p]
# 		p = p.replace('/o', 'o')
# 		if p.count('/') > 0: continue
# 		pSplit = p.split(' -> ')
# 		pParsed = [DT.parse_figure(x) for x in pSplit]
# 		#print p, pParsed
# 		if pSplit[0] in [correlateChord, comparisonChord]:
# 			if pParsed[1][0] in theTriads:
# 				if pSplit[0] == comparisonChord:
# 					firstInversionVec[theTriads.index(pParsed[1][0])] += theCount
# 				elif pSplit[0] == correlateChord:
# 					rootVec[theTriads.index(pParsed[1][0])] += theCount
# 	#print rootVec, firstInversionVec
# 	return pearsonr(rootVec, firstInversionVec)

# def rf_matrix():
# 	results = {}
# 	for s in theTriads:
# 		for t in theTriads:	
# 			t = t + '6'
# 			results[s + ', ' + t] = root_function(s, t)[0]
# 	for k in sorted(results.keys(), key = lambda x: -results[x]):
# 		print k, results[k]

# def percentage_of_all_chords(composer = 'Bach', targetChords = ['I', 'I6', 'V', 'V7'], mode = 'major'):
# 	global tempList, tempDict
# 	load(composer)
# 	regex('^[^-]*$', mode = mode, printIt = False)
# 	tempDict = {x[0]:x[1] for x in tempList}
# 	mySum = sum([x[1] for x in tempList])
# 	tempResults = []
# 	for c in targetChords:
# 		value = tempDict.get(c, 0) 
# 		print c, "%.1f" % (100. * value/mySum)
# 		tempResults.append(value)
# 	print "TOTAL SUM %.1f" % (100. * sum(tempResults)/mySum)

# def diatonic_percentages(compList = ['Josquin', 'Palestrina', 'Bach', 'Beethoven']):
# 	global output, ax
# 	"""groupChords = [['I', 'Imaj7'], ['I6', 'Imaj6/5'], ['I6/4', 'Imaj4/3', 'Imaj2'], ['ii', 'ii7'], ['ii6', 'ii6/5'], ['ii6/4', 'ii4/3', 'ii2'], 
# 					['iii', 'iii7'], ['iii6', 'iii6/5'], ['iii6/4', 'iii4/3', 'iii2'], ['IV', 'IVmaj7'], ['IV6', 'IVmaj6/5'], ['IV6/4', 'IVmaj4/3', 'IVmaj2'],
# 					['V', 'V7'], ['V6', 'V6/5'], ['V6/4', 'V4/3', 'V2'], ['vi', 'vi7'], ['vi6', 'vi6/5'], ['vi6/4', 'vi6/4', 'vi2'], 
# 					['viio', 'vii/o7'], ['viio6', 'vii/o6/5'], ['viio6/4', 'viio4/3', 'vii/o2']]"""
					
# 	"""groupChords = [['I', 'Imaj7', 'I6', 'Imaj6/5', 'I6/4', 'Imaj4/3', 'Imaj2'], ['ii', 'ii7', 'ii6', 'ii6/5', 'ii6/4', 'ii4/3', 'ii2'], 
# 					['iii', 'iii7', 'iii6', 'iii6/5', 'iii6/4', 'iii4/3', 'iii2'], ['IV', 'IVmaj7', 'IV6', 'IVmaj6/5', 'IV6/4', 'IVmaj4/3', 'IVmaj2'],
# 					['V', 'V7', 'V6', 'V6/5', 'V6/4', 'V4/3', 'V2'], ['vi', 'vi7', 'vi6', 'vi6/5', 'vi6/4', 'vi6/4', 'vi2'], 
# 					['viio', 'vii/o7', 'viio6', 'vii/o6/5', 'viio6/4', 'vii/o4/3', 'vii/o2', 'viio7', 'viio6/5', 'viio4/3', 'viio2']]"""
					
# 	groupChords = [[x] for x in 'I', 'ii', 'iii', 'IV', 'V', 'vi'] + [['viio', 'viio6']]
					
# 	xyBoundaries = [[0, 12], [0, 12]]
# 	fig, ax = plt.subplots()
# 	#fig.set_size_inches(6, 6)
# 	ax.axes.get_xaxis().set_visible(False)
# 	ax.axes.get_yaxis().set_visible(False)
# 	ax.set_xlim(xyBoundaries[0][0], xyBoundaries[0][1])
# 	ax.set_ylim(xyBoundaries[1][0], xyBoundaries[1][1])
# 	ax.set_title('chord size is proportional to occurrence frequency')
	
# 	for compNumber, composer in enumerate(compList): 
# 		load(composer)
# 		output = {}
# 		for g in groupChords:
# 			for c in g:
# 				output[g[0]] = output.get(g[0], 0) + counts[0].get(c, 0)
	
# 		totals = float(sum(output.values()))
# 		output = {s:100. * output[s] / totals for s in output}
			
# 		#DT.print_dict(output, pct = True)
# 		y = 2 + 2.5 * compNumber

# 		for i, s in enumerate(['I', 'ii', 'iii', 'IV', 'V', 'vi', 'viio']):
# 			x = i * (8. / 7) + 1
# 			if s == 'viio':
# 				displayS = u'vii°'
# 			else:
# 				displayS = s
# 			ax.text(x, y, displayS, horizontalalignment = 'center', verticalalignment = 'center', fontsize = 2. * output[s], fontname = 'Times')
# 		ax.text(9, y, composer, horizontalalignment = 'left', verticalalignment = 'center', fontsize = 16, fontname = 'Times')
# 	fig.canvas.draw()
# 	plt.ion()
# 	plt.show()

# def diatonic_percentages2(fauxbourdon = True):
# 	global output, ax
# 	groupChords = [['I', 'Imaj7'], ['I6', 'Imaj6/5'], ['I6/4', 'Imaj4/3', 'Imaj2'], ['ii', 'ii7'], ['ii6', 'ii6/5'], ['ii6/4', 'ii4/3', 'ii2'], 
# 					['iii', 'iii7'], ['iii6', 'iii6/5'], ['iii6/4', 'iii4/3', 'iii2'], ['IV', 'IVmaj7'], ['IV6', 'IVmaj6/5'], ['IV6/4', 'IVmaj4/3', 'IVmaj2'],
# 					['V', 'V7'], ['V6', 'V6/5'], ['V6/4', 'V4/3', 'V2'], ['vi', 'vi7'], ['vi6', 'vi6/5'], ['vi6/4', 'vi6/4', 'vi2'], 
# 					['viio', 'vii/o7'], ['viio6', 'vii/o6/5'], ['viio6/4', 'viio4/3', 'vii/o2']]
					
# 	groupChords = [['I', 'Imaj7', 'I6', 'Imaj6/5', 'I6/4', 'Imaj4/3', 'Imaj2'], ['ii', 'ii7', 'ii6', 'ii6/5', 'ii6/4', 'ii4/3', 'ii2'], 
# 					['iii', 'iii7', 'iii6', 'iii6/5', 'iii6/4', 'iii4/3', 'iii2'], ['IV', 'IVmaj7', 'IV6', 'IVmaj6/5', 'IV6/4', 'IVmaj4/3', 'IVmaj2'],
# 					['V', 'V7', 'V6', 'V6/5', 'V6/4', 'V4/3', 'V2'], ['vi', 'vi7', 'vi6', 'vi6/5', 'vi6/4', 'vi6/4', 'vi2'], 
# 					['viio', 'vii/o7', 'viio6', 'vii/o6/5', 'viio6/4', 'vii/o4/3', 'vii/o2', 'viio7', 'viio6/5', 'viio4/3', 'viio2']]
					
# 	groupChords = [[x] for x in 'I', 'ii', 'iii', 'IV', 'V', 'vi'] + [['viio', 'viio6']]
	
# 	get_size(1, fauxbourdon = fauxbourdon)
					
# 	xyBoundaries = [[0, 12], [0, 12]]
# 	fig, ax = plt.subplots()
# 	#fig.set_size_inches(6, 6)
# 	ax.axes.get_xaxis().set_visible(False)
# 	ax.axes.get_yaxis().set_visible(False)
# 	ax.set_xlim(xyBoundaries[0][0], xyBoundaries[0][1])
# 	ax.set_ylim(xyBoundaries[1][0], xyBoundaries[1][1])
# 	ax.set_title('chord size is proportional to occurrence frequency')
	
# 	output = {}
# 	for g in groupChords:
# 		for c in g:
# 			#print c, g[0], output.get(g[0], 0), counts[0].get(c, 0)
# 			output[g[0]] = output.get(g[0], 0) + working[0].get(c, 0)

# 	totals = float(sum(output.values()))
# 	output = {s:100. * output[s] / totals for s in output}
		
# 	#DT.print_dict(output, pct = True)
	

# 	for i, s in enumerate(['I', 'ii', 'iii', 'IV', 'V', 'vi', 'viio']):
# 		x = i * (9. / 7) + 1
# 		if s == 'viio':
# 			displayS = u'vii°'
# 		else:
# 			displayS = s
# 		y = 2
# 		ax.text(x, y, displayS, horizontalalignment = 'center', verticalalignment = 'center', fontsize = 0.01 + 4. * output.get(s, 0.01), fontname = 'Times')
# 		ax.text(10, y, 'root', horizontalalignment = 'left', verticalalignment = 'center', fontsize = 16, fontname = 'Times')
# 		y+=4
# 		ax.text(x, y, displayS, horizontalalignment = 'center', verticalalignment = 'center', fontsize = 0.01 + 4. * output.get(s+'6', 0.01), fontname = 'Times')
# 		ax.text(10, y, 'third', horizontalalignment = 'left', verticalalignment = 'center', fontsize = 16, fontname = 'Times')
# 		y+=4
# 		ax.text(x, y, displayS, horizontalalignment = 'center', verticalalignment = 'center', fontsize = 0.01 + 4. * output.get(s+'6/4',0.01), fontname = 'Times')
# 		ax.text(10, y, 'other', horizontalalignment = 'left', verticalalignment = 'center', fontsize = 16, fontname = 'Times')
# 	fig.canvas.draw()
# 	plt.ion()
# 	plt.show()

# def organize_modulations():
# 	global modulations, modulationProgs
# 	modulations = {}
# 	pitchC = pitch.Pitch('C')
# 	for p in modulationProgs:
# 		pSplit = p.split()
# 		intervalToC = interval.Interval(pitch.Pitch(fix_letter(pSplit[0])), pitchC)
# 		outStr = ['C: ', 'c: '][int(pSplit[0][0].islower())]
# 		for s in pSplit[1:]:
# 			if s.count(':') > 0:
# 				s = s[:-1]
# 				if len(s) > 1 and s[-1] == 'b':
# 					s = s[:-1] + '-'
# 				s = DT.transpose_letter(s, intervalToC)
# 				if s[-1] == '-':
# 					s = s[:-1] + 'b'
# 				s += ':'
# 			outStr += s
# 			outStr += ' '
# 		outStr = outStr[:-1]
# 		tempList = modulations.get(outStr, []) + modulationProgs[p]
# 		modulations[outStr] = tempList
# 		#print p, "\t|||\t", outStr

# def fix_letter(s):
# 	if s[-1] == ':':
# 		s = s[:-1]
# 	if len(s) > 1 and s[-1] == 'b':
# 		s = s[:-1] + '-'
# 	return s	

# def vii_V_asymmetry(compList = ['Corelli', 'Bach', 'Haydn', 'Mozart', 'Beethoven'], mode = 'MAJOR'):
	
# 	"""2017. Compare V -> viio progressions to viio -> V progressions.  Is one, the other, or both grammatical?  """
	
# 	modeInd = int(mode.upper().startswith('MI'))
# 	for c in compList:	
# 		load(c)
# 		remove_inversions()
# 		get_size(2, useReduced = True)
# 		a = working[modeInd].get('viio -> V', 0)
# 		a1 = sum([x[1] for x in working[modeInd].items() if x[0].startswith('viio -> ')])
# 		b = working[modeInd].get('V -> viio', 0)
# 		b1 = sum([x[1] for x in working[modeInd].items() if x[0].startswith('V -> ')])
# 		print c, round(a * 100./max(a1, 1), 1), round(b*100./max(b1, 1), 1), a, b, round((a * 100./max(a1, 1))/max(b*100./max(b1, 1), .000001), 1)

# def compare_modes(progLen = 2, printPct = 3, useReduced = False, filterGrammar = False):	
			
# 	"""2017. Compares minor mode to major: which chords or progressions happen preferentially in one mode or in the other?"""

# 	global results, majorDict, minorDict
	
# 	if useReduced:
# 		remove_inversions()
# 	results = {}
	
# 	get_size(progLen, useReduced = useReduced)
	
# 	majorDict = normalize_dict(clean_dict(working[0]))
# 	minorDict = normalize_dict(clean_dict(working[1]))
	
# 	totalKeys = set(majorDict.keys() + minorDict.keys())
	
# 	for s in totalKeys:
# 		results[s] = majorDict.get(s, 0) - minorDict.get(s, 0)
		
# 	resultsKeys = sorted(results.keys(), key = lambda x: -results[x])
# 	resultsLen = int(len(resultsKeys) * printPct / 200.)
# 	if resultsLen > len(resultsKeys) / 2.: resultsLen = len(resultsKeys) / 2
# 	if filterGrammar:
# 		myGrammar = GrammarObject()
# 		for s in resultsKeys[:resultsLen] + resultsKeys[-resultsLen:]:
# 			theTest = myGrammar.grammar_test(s)
# 			if (theTest is not False):						# want to see non grammatical progressions that are positive
# 				print s, '%.2f' % (100.*results[s])
# 	else:
# 		for s in resultsKeys[:resultsLen] + resultsKeys[-resultsLen:]:
# 			print s, '%.2f' % (100.*results[s])

# def normalize_dict(myDict, factor = 1.):
# 	s = float(sum(myDict.values()))
# 	return {x[0]:x[1]/(s * factor) for x in myDict.items()}
	
# def clean_dict(myDict):
# 	outDict = {}
# 	for x in myDict.items():
# 		c = clean_symbol(x[0])
# 		outDict[c] = outDict.get(c, 0) + x[1]
# 	return outDict

# def clean_symbol(sym):
# 	symSplit = sym.split(' -> ')
# 	for i, s in enumerate(symSplit):
# 		symSplit[i] = s.replace('/o', '').replace('b9', '').replace('maj', '').replace('o', '').upper().replace("B", 'b').replace('7', '').replace('6/5', '6').replace('4/3', '6/4').replace('2', '')
# 	return ' -> '.join(symSplit)

# standardModel1 = ['I -> II', 'I -> IV','I -> V','I -> VI','I -> VII', 'II -> V','II -> VII', 'IV -> I', 
# 				'IV -> II', 'IV -> V', 'IV -> VII', 'V -> I', 'V -> IV','V -> VI', 'VI -> I', 'VI -> II', 'VI -> IV','VI -> V','VI -> VII',
# 				'VII -> V','VII -> I']
				
# standardModel2 = ['I -> II', 'I -> IV','I -> V','I -> VI', 'II -> V','II -> VII', 'IV -> I', 
# 				'IV -> II', 'IV -> V', 'IV -> VII', 'V -> I', 'V -> VI', 'VI -> II', 'VI -> IV','VI -> V','VI -> VII',
# 				'VII -> V', 'VII -> I']	

# globalISpecificProgs = ['V -> IV6', 'VI -> I6', 'I -> VII6']

# standardModel3 = [	'I -> I6', 'I6 -> I', 'I -> II', 'I6 -> II', 'I6 -> II6', 'I -> II6', 'I -> IV', 'I6 -> IV', 'I6 -> IV6', 'I -> IV6', 'I -> V', 'I6 -> V', 
# 					'I6 -> V6', 'I -> V6', 'I -> VI', 'I6 -> VI', 'I6 -> VII6', 'I -> VII6', 
# 					'II -> II6', 'II6 -> II', 'II -> V', 'II6 -> V', 'II6 -> V6', 'II -> V6', 'II6 -> VII6', 'II -> VII6', 
# 					'IV -> IV6', 'IV6 -> IV', 'IV -> I', 'IV6 -> I', 
# 					'IV6 -> I6', 'IV -> I6', 'IV -> II', 'IV6 -> II', 'IV6 -> II6', 'IV -> II6', 'IV -> V', 'IV6 -> V', 'IV6 -> V6', 'IV -> V6', 
# 					'IV6 -> VII6', 'IV -> VII6', 
# 					'V -> I', 'V -> V6', 'V6 -> V', 'V6 -> I', 'V6 -> I6', 'V -> I6', 
# 					'V6 -> IV6', 'V -> IV6', 'V -> VI', 'V6 -> VI', 'VI -> I6', 
# 					'VI -> II', 'VI -> II6', 'VI -> IV', 'VI -> IV6', 'VI -> V', 
# 					'VI -> V6', 'VI -> VII6', 'VII6 -> V', 'VII6 -> V6', 
# 					'VII6 -> VI', 'VII6 -> I', 'VII6 -> I6']

# def make_acceptable_model():
# 	output = []
# 	for i in standardModel:
# 		iSplit = i.split(' -> ')
# 		output.append(i)
# 		output.append(iSplit[0] + '6 -> ' + iSplit[1])
# 		output.append(iSplit[0] + '6 -> ' + iSplit[1] + '6')
# 		output.append(iSplit[0] + ' -> ' + iSplit[1] + '6')
# 	return output

# def is_diatonic(s):
# 	if all([is_diatonic_chord(x) for x in s.split(' -> ')]): 
# 		return True
# 	return False
	
# def is_diatonic_chord(s):
# 	s = DT.parse_figure(s)
# 	if not s[2] and not s[3] and (s[0].count('b') + s[0].count('#')) == 0: return True 


# def grammar_model(mode = 'major', chordThresh = 2, progThresh = 2, filterDiatonic = True, sixFour = False, removeInversions = True, fauxbourdon = False):
# 	"""FOR CHAPTER 5 OF TAOM: DECLARES GRAMMATICAL ALL CHORD PROGS ABOVE A CERTAIN THRESHOLD"""
# 	global results, chordDict, progDict, iErrors
	
# 	if not removeInversions:
# 		standardModel = standardModel3
# 	else:
# 		standardModel = standardModel1
	
# 	chordThresh = chordThresh / 100.
# 	progThresh = progThresh/100.
	
# 	if mode.upper().startswith('BO'):
# 		modeIndices = [0, 1]
# 	else:
# 		modeIndices = [get_mode(mode)]
	
# 	"""if useReduced:
# 		remove_inversions()"""
	
# 	results = []
	
# 	for modeInd in modeIndices:
		
# 		get_size(1, removeInversions = removeInversions, fauxbourdon = fauxbourdon)
# 		tempDict = {x[0]:x[1] for x in working[modeInd].items() if is_diatonic(x[0]) and (sixFour or x[0].count('6/4') == 0)}
# 		chordDict = normalize_dict(clean_dict(tempDict), factor = float(len(modeIndices)))
	
# 		get_size(2, removeInversions = removeInversions, fauxbourdon = fauxbourdon)
# 		tempDict = {x[0]:x[1] for x in working[modeInd].items() if is_diatonic(x[0]) and (sixFour or x[0].count('6/4') == 0)}
# 		print "TOTAL PROGRESSIONS", sum(tempDict.values())
# 		progDict = clean_dict(tempDict)
	
# 		for c, theCount in chordDict.items():
# 			if theCount < chordThresh: continue
# 			#print "chord", c
# 			cSpace = c + ' '
# 			startingProgs = {x[0]:x[1] for x in progDict.items() if x[0].startswith(cSpace)}
# 			print "chord", c, sum(startingProgs.values()), "progressions"
# 			tempDict = normalize_dict(startingProgs)
# 			for p, pCount in tempDict.items():
# 				if filterDiatonic and ((p.count('/') > p.count('6/4') + p.count('/o') + p.count('6/5') + p.count('4/3')) or p.count("IT") > 0 or p.count("GER") > 0): continue
# 				pSplit = p.split(' -> ')
# 				if pSplit[0] == pSplit[1] or chordDict.get(pSplit[1], 0) < chordThresh: continue
# 				if pCount >= progThresh: 
# 					results.append(p)
					
# 	results = sorted(results)
	
# 	missingProgs = []
# 	extraProgs = []
	
# 	for s in results: 
# 		if s not in standardModel and s not in extraProgs:
# 			extraProgs.append(s)
		
# 	for s in standardModel:
# 		if s not in results and s not in missingProgs:
# 			missingProgs.append(s)
	
# 	print "NONGRAMMATICAL PROGS:"
# 	for s in extraProgs:
# 		print " ", s
	
# 	print "UNUSED PROGS:"
# 	for s in missingProgs:
# 		print " ", s
		
# 	iSpecificProgs = {'VI -> I': [], 'V -> IV': []}
# 	get_size(2, removeInversions = False, fauxbourdon = True)
	
# 	for modeInd in modeIndices:
# 		for p, count in working[modeInd].items():
# 			cleanP = clean_symbol(reduce_prog(p))
# 			if cleanP in iSpecificProgs:
# 				#print cleanP, p, count
# 				iSpecificProgs[cleanP].append([p, count])
	
# 	iErrors = []
# 	sixOne = [0, 0]
	
# 	for p, c in iSpecificProgs['VI -> I']:
# 		pSplit = [DT.parse_figure(x) for x in p.split(' -> ')]
# 		if pSplit[1][1] == '6':
# 			sixOne[0] += c
# 		else:
# 			sixOne[1] += c
# 			iErrors.append([p, c])
	
# 	print "PERCENTAGE OF I-SPECIFIC PROGS CONFORMING TO THE MODEL:"
			
# 	if 'VI -> I' in results:
# 		print "  VI -> I", round(sixOne[0]*100./max(sum(sixOne), .01), 1)
			
# 	fiveFour = [0, 0]
	
# 	for p, c in iSpecificProgs['V -> IV']:
# 		pSplit = [DT.parse_figure(x) for x in p.split(' -> ')]
# 		if pSplit[1][1] in ['6', '6/5', '6/4']:
# 			fiveFour[0] += c
# 		else:
# 			fiveFour[1] += c
# 			iErrors.append([p, c])
			
# 	if 'V -> IV' in results:
# 		print "  V -> IV", round(fiveFour[0]*100./max(sum(fiveFour), .01), 1)
		
# def inversions_on_degrees(mode = 'major'):
# 	"""2017. record the % of first inversion chords vs. root position chords on each degree
# 	Believe this duplicates routines found elsewhere but ...
# 	"""
# 	print "Percentage of root-position chords by scale degree: "
# 	modeInd = get_mode(mode)
# 	theChords = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'viio']
# 	countsDict = [[0, 0]] * 7
# 	pcts = [0] * 7
# 	for i in range(len(theChords)):
# 		countsDict[i][0] = counts[modeInd].get(theChords[i], 0)
# 		countsDict[i][1] = counts[modeInd].get(theChords[(i - 2) % len(theChords)] + '6', 0)
# 		pcts[i] = round(countsDict[i][0] * 100./max(0, sum(countsDict[i])), 1)
# 	rangeList = sorted(range(len(theChords)), key = lambda x: -pcts[x])
# 	for i in rangeList:
# 		print "Scale degree ", i+1, pcts[i]

# def percentage(species = "vi7* -> V7*$", genus = "vi7* -> CHORD$"):
# 	return round(100.*regex(species, printIt = False)/float(regex(genus, printIt = False)), 0)

# def passing_six_four(mode = 'major'):
# 	global output, output2
# 	modeInd = get_mode(mode)
# 	get_size(3)
# 	make_bass_dict()
# 	output = {}
# 	output2 = {}
# 	for s in bassDict[modeInd].keys():
# 		if consec_bass(s):
# 			for prog, count in bassDict[modeInd][s].items():
# 				progSplit = prog.split(' -> ')
# 				if progSplit[1].startswith('viio'): continue
# 				progSplitParse = [DT.parse_figure(x) for x in progSplit]
# 				if progSplitParse[1][1] == '6/4':
# 					output[prog] = count
# 					output2[progSplit[1]] = output2.get(progSplit[1], 0) + count
# 	DT.print_dict(output, pct = True)
# 	DT.print_dict(output2, pct = True)
			
	
# def consec_bass(s):
# 	newS = s.replace(' -> ', 'X').replace('+', '').replace('-', '')
# 	sSplit = [(int(x) - 1) % 7 for x in newS.split('X')]
# 	ints = [(sSplit[x+1] - sSplit[x]) % 7 for x in [0, 1]]
# 	if ints == [1, 1] or ints == [6, 6]: return True
# 	return False

# def transition_asymmetry():
# 	global newOutput, tempList
# 	newOutput = {}
# 	get_size(2, removeInversions = True)
# 	syms = ["I", "ii", "iii", "IV", "V", "vi", "viio"]
# 	for i, sym1 in enumerate(syms):
# 		for j, sym2 in enumerate(syms):
# 			if i == j: continue
# 			theSum = starts(sym1 + ' -> ', printIt = False)
# 			if not theSum: continue
# 			tempDict = {x[0]:x[1]*100./theSum for x in tempList}
# 			val1 = tempDict.get(sym1 + ' -> ' + sym2, 0)
# 			theSum = ends(' -> ' + sym2, printIt = False)
# 			if not theSum: continue
# 			tempDict = {x[0]:x[1]*100./theSum for x in tempList}
# 			val2 = tempDict.get(sym1 + ' -> ' + sym2, 0)
# 			newOutput[sym1 + ' -> ' + sym2] = val1 - val2
# 			print sym1, sym2, val1, val2
# 	DT.print_dict(newOutput, pct = False)


# def new_modulations(modeInd = 0, stripInversions = True, length = 4):
# 	global modulationProgs
# 	length = int(length/2. + .5)
# 	newDict = {}
# 	for i in fullChordDict:
# 		chordList = calculate_modulations(fullChordDict[i][0]).split()
# 		chordListLen = len(chordList)
# 		keyChangeLocations = [x for x in range(chordListLen) if chordList[x].count(':') > 0]
# 		mode = chordList[0][0].islower()
# 		if mode != modeInd:
# 			continue
# 		#print chordList
# 		#print keyChangeLocations
# 		if len(keyChangeLocations) == 1:
# 			continue
# 		for i, keyChange in enumerate(keyChangeLocations[1:]):
# 			prevKey = chordList[keyChangeLocations[i]]
# 			finalSplit = chordList[max(keyChange - length, 0):min(chordListLen, keyChange + length + 1)]
# 			#print "  ", i, keyChange, len(chordList), length, max(keyChange - length, 0), min(chordListLen, keyChange + length), finalSplit
# 			if stripInversions:
# 				inversionFreeList = []
# 				for c in finalSplit:
# 					if c.count(':') > 0:
# 						inversionFreeList.append(c)
# 					else:
# 						newChord = DT.parse_figure(c)
# 						if newChord[2]:
# 							newChord = newChord[0] + '/' + newChord[2]
# 						else:
# 							newChord = newChord[0]
# 						inversionFreeList.append(newChord)
# 				finalSplit = inversionFreeList
# 			newFig = prevKey + ' ' + ' -> '.join (finalSplit)
# 			newFig = newFig.replace(': -> ', ': ')
# 			modulationType = (prevKey + ' ' + chordList[keyChange]).replace(':', '')
# 			#print modulationType
# 			if modulationType not in newDict:
# 				newDict[modulationType] = {}
# 			newDict[modulationType][newFig] = newDict[modulationType].get(newFig, 0) + 1
# 	modulationProgs = newDict
# 	modulations = sorted(modulationProgs.keys(), key = lambda x: -sum(modulationProgs[x].values()))
# 	for m in modulations:
# 		print m, sum(modulationProgs[m].values())
# 		specificModulations = sorted(modulationProgs[m].keys(), key = lambda x: -modulationProgs[m][x])
# 		for s in specificModulations:
# 			print "  ", s, modulationProgs[m][s]
			

# def calculate_modulations(chordString):
# 	modulations = [x.replace(":", '') for x in chordString if x.count(':')]
# 	"""if modulations[0] != modulations[-1]:
# 		print "STARTS AND ENDS IN DIFFERENT KEYS", modulations"""
# 	homeKey = key.Key(clean_accidental(modulations[0]))
# 	outDict = {}
# 	for m in modulations:
# 		c = construct_chord(m)
# 		figure = DT.figure_from_chord(c, homeKey)
# 		newFig = DT.parse_figure(figure)[0]
# 		outDict[m + ':'] = newFig + ':'
# 	newChordString = ' '.join([outDict.get(x, x) for x in chordString])
# 	return newChordString
			
# def construct_chord(s):
# 	s = clean_accidental(s)
# 	p1 = pitch.Pitch(s)
# 	p3 = p1.transpose('P5')
# 	if s[0].isupper():
# 		p2 = p1.transpose('M3')
# 	else:
# 		p2 = p1.transpose('m3')
# 	return [p1, p2, p3]

# def clean_accidental(s):
# 	if len(s) > 1 and s[-1] == 'b':
# 		s = s[:-1] + '-'
# 	return s

# 	