from music21 import *
import sys
import re
import pickle
import os
import pprint
import voicing
import progs
import bigScore
import bigVoicing
import bigVL
import bigVLprogs
from fractions import Fraction
import copy



# Very small, simple score I built from scratch sorta as a test.
simpleScore = stream.Score()
	simpleScore.repeatAppend(stream.Part(), 4)
	myPitches = [72, 76, 79, 84]
	index = 3
	for p in simpleScore:
		p.timeSignature = meter.TimeSignature('4/4')
		m = stream.Measure()
		m.append(note.Note(myPitches[index]))
		m.repeatAppend(note.Rest(), 3)
		p.repeatInsert(m, [0, 1, 2, 3, 4, 5])
		index -= 1
	simpleBigScore = bigScore.BigScore(simpleScore, timeSignature = meter.TimeSignature('4/4'), globalKey = key.Key('C'))
	simpleBigScore.movement.show()
	simpleTestBV = BigVoicing(simpleBigScore, 'I', 2, 1, 4, 4)