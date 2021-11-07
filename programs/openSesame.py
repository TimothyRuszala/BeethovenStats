from music21 import *
c = converter.parse("Music/Beethoven Quartets/op59_no7_mov1.txt", format = "romantext")





import rn # will produce an error because of load()
rn.gather_stats() # wait a minute or two
rn.regex("^V -> IV$")


 rn.regex("^V -> IV$")
 rn.regex("^V -> IVINV$") # I added INV as a shorthand for INVERSION
 rn.regex("IV6 -> CHORD$") # same with CHORD, 429 of these
 rn.show("V -> IV") # should make a score for you