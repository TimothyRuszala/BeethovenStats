from music21 import *
import re
import os
import pprint
import pathlib
import voicing
import progs
import bigScore
import bigVoicing
import bigVL
import bigVLprogs
from fractions import Fraction

# getProgs() is the main function of the application. It takes two arguments:
# the name of a Beethoven String quartet file (e.g. 'op18_no1_mov1'), and a
# boolean which if true, loads previously found chord progression data,
# otherwise the program finds the chord progressions for the file again.


def getProgs(filename, load=True):

    # ~~VARIABLES_AND_DICTIONARIES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    mxlFile = filename + '.mxl'
    print(mxlFile)

    # create a Progs object, which stores local chord progression counts
    progDict = progs.Progs()
    # filename which stores the progressions for a movement
    progsStorage = filename + "_progs"

    # Another Progs object, which stores global progression counts, i.e.
    # among all string quartets
    giantProgDict = progs.Progs()

    # giantProgDictStorageMay13a = str(pathlib.Path(__file__).parents[1]) \
    #     + "/Music/Beethoven Quartets/giantProgDictStorageMay13a"
    # rnFrequencies = {"major": {}, "minor": {}}

# ~~OPEN_FILE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extracting preliminary data from the rntext file
    with open(filename + '.txt', 'r') as rnFile:
        for i in range(4):
            rnFile.readline()
        timeSignatureLine = rnFile.readline().split()
        print(timeSignatureLine)
        timeSignature = meter.TimeSignature(timeSignatureLine[2])
        rnFile.readline()

        # Extracting the string parts
        try:
            movement = converter.parse(mxlFile)
        except RuntimeError:
            print(filename + " could not be opened")
            return

        # Create a BigScore object, which preprocesses the .mxl file
        mvt = bigScore.BigScore(movement, timeSignature, mxlFile=mxlFile)
        print(mvt.getMvtString())

# ~~LOAD_TOGGLE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if load:  # toggles load
            # loads the data in progsStorage into progDict
            progDict.loadProgs(progsStorage)

# ~~GATHER_VL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Gathers the voice-leadings.
        else:
            prevVoicing = None
            prevPrevVoicing = None
            prevBigVoicing = None

# ~~PARSE_BY_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            for line in rnFile:
                # handles special cases in the rntext file
                if line[0] == 'N':  # i.e. "Note: ..."
                    continue
                if line[0] == '\n' or line[0] == ' ':
                    continue
                beatsChordsKeys = line.split()
                if beatsChordsKeys[0][0] == 'T':  # i.e. "Time Signature: 4/4"
                    timeSignature = meter.TimeSignature(beatsChordsKeys[-1])
                    continue
                mmStr = beatsChordsKeys[0]
                mNumb = int(mmStr[1:])
                print(mNumb)
                # in case a measure doesn't actually exist.
                if mvt.violin1.measure(mNumb) is None:
                    continue
                currentBeat = None

# ~~PARSE_THROUGH_LINE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                for i in range(1, len(beatsChordsKeys)):
                    # ~~CHECK_KEY~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Checks for key signature specification
                    keyRE = re.compile('[a-g](b|#)?:', re.IGNORECASE)
                    isKey = keyRE.match(beatsChordsKeys[i])
                    if isKey:
                        keyStr = isKey.group()
                        currentKey = keyStr[0:-1]
                        mvt.globalKey = key.Key(currentKey)
                        print("~~~~~~~~~~~~~~~~~~~~~~~", mvt.globalKey)
                        continue
# ~~CHECK_BEAT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Checks if BEAT
                    beatRE = re.compile('b\\d.?\\d*')
                    isBeat = beatRE.match(beatsChordsKeys[i])
                    if isBeat:
                        beatFlag = 0
                        beatStr = isBeat.group()
                        currentBeat = float(beatStr[1:len(beatStr)])
                        currentBeat = Fraction(
                            currentBeat).limit_denominator(20)
                        continue
# ~~CHECK_RN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Checks if Roman Numeral. If it is, the program creates a
                        # Voicing object representing that part of the score,
                        # using the specified roman numeral as help. Also
                        # creates a BigVoicing object.
                    chordRE = re.compile(
                        "((Ger|It|Fr|N|b?[iIvV]+o?[+]?)+\
                            (b?#?o?[0-9]?/?)*)+|  ")
                    isChord = chordRE.match(beatsChordsKeys[i])
                    if isChord:
                        chordRN = isChord.group()
                        addRNtoProg(mvt, rnFrequencies, chordRN)
                        # checks if we are at the first beat of a measure,
                        # which in rntext is not explicitly noted
                        if chordRN == "  ":
                            chordRN = "No RN"
                        if currentBeat is None:
                            currentBeat = 1.0
                        # gets voicing for that part of the music
                        currentVoicing = mvt.getVoicingAt(
                            mNumb, currentBeat, chordRN)
                        # Negotiate the beginning/end of the .mxl file
                        if currentVoicing is None:
                            break
                        if prevVoicing is None:
                            prevVoicing = currentVoicing
                            continue
                        if chordRN == prevVoicing.rn:
                            continue
                        else:
                            mvt.update(prevVoicing, mNumb, currentBeat)
                            currentBigVoicing = bigVoicing.BigVoicing(
                                mvt, prevVoicing.rn, prevVoicing.mNumb,
                                prevVoicing.beat, mNumb, currentBeat)
                        if prevPrevVoicing is None:
                            prevPrevVoicing = prevVoicing
                            prevVoicing = currentVoicing
                            prevBigVoicing = currentBigVoicing
                            continue
# ~~ADD_VL_TO_PROGS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        # add discovered voice-leadings to the progs dictionary
                        newVL = voicing.VL(prevPrevVoicing, prevVoicing, mvt)
                        newBVL = bigVL.BigVL(prevBigVoicing, currentBigVoicing)
                        progDict.addToProgs(newVL, newBVL)

                        prevPrevVoicing = prevVoicing
                        prevVoicing = currentVoicing
                        prevBigVoicing = currentBigVoicing

# ~~FURTHER_OPERATIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            # Adds locally discovered progs dictionary to the global progs dict
            giantProgDict.combineProgs(progDict.progs)
            # Store the local data in the local progsStorage
            progDict.dumpProgs(progsStorage)
            # Store the global data in global progsStorage
            giantProgDict.dumpProgs(giantProgDictStorageMay13a)

    pprint.pprint(progDict.progs)
    return progDict.progs

# helper method to update progs


def addRNtoProg(mvt, rnFrequencies, chordRN):
    mode = mvt.globalKey.mode
    if mode == 'major':
        if chordRN in rnFrequencies:
            rnFrequencies[mode][chordRN] += 1
        else:
            rnFrequencies[mode][chordRN] = 1
    elif mode == "minor":
        if chordRN in rnFrequencies:
            rnFrequencies[mode][chordRN] += 1
        else:
            rnFrequencies[mode][chordRN] = 1


def getListOfQuartetFilesWithoutExtensions():
    _MAINPATH = '/Users/truszala/Documents/1JuniorSpring/python!/'
    _MUSICPATH = _MAINPATH + 'Music/Beethoven Quartets/'

    unfilteredFilelist = os.listdir(_MUSICPATH)
    fileList = []
    for file in unfilteredFilelist:
        if file[-1] == 't':  # i.e. '.txt'
            fileList.append(_MUSICPATH + file[0:-4])

    return fileList

# Calls getProgs() on every string quartet file


def getAllProgs():
    fileList = getListOfQuartetFilesWithoutExtensions()
    for file in reversed(fileList):
        print(file)
        getProgs(file, load=False)

# sets up a movement


def load(fullFilename):

    with open(fullFilename + '.txt', 'r') as rnFile:
        for i in range(4):
            rnFile.readline()
        timeSignatureLine = rnFile.readline().split()
        timeSignature = meter.TimeSignature(timeSignatureLine[2])
        rnFile.readline()
        # Extracting the string parts
        movement = converter.parse(fullFilename + '.mxl')
        mvt = bigScore.BigScore(movement, timeSignature, mxlFile=fullFilename)
    return mvt

# MAIN ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def main():

    getProgs(str(pathlib.Path(__file__).parents[1]) +
             "/Music/Beethoven Quartets/op130_no13_mov1", load=False)
    print('finished')


if __name__ == "__main__":
    main()
