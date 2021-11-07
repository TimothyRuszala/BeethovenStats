from music21 import *

s = corpus.parse('mozart/k80', 1)
s.id = 'mozartK80'
sExcerpt = s.measures(1, 4)
sExcerpt.id = 'excerpt'
sExcerpt.show()

print(sExcerpt.derivation)