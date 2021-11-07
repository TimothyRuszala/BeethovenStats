from music21 import *

coreCorpus = corpus.corpora.CoreCorpus()
predicate = lambda x: 400 < x < 500
fourFour = corpus.search(predicate, 'noteCount')
myPiece = fourFour[1].parse()
print(len(fourFour.getPaths()))



