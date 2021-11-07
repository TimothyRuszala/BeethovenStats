from music21 import *


cMinor = chord.Chord("C G E D D- F")
cMinor.duration.type = "half"
cMinor.add("B")

print(cMinor.commonName)

cMinor = cMinor.semiClosedPosition()
cMinor.show()

url = 'http://kern.ccarh.org/cgi-bin/ksdata?l=cc/bach/cello&file=bwv1007-01.krn&f=xml'
sAlt = converter.parse(url)
sAlt.show()
