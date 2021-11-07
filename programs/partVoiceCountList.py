from music21 import *

class PartVoiceCountList():

	def __init__(self, bigvoicing):
		pvcl = {'Cello': 0, 'Viola': 0, 'Violin II': 0, 'Violin I': 0}
		for p in bigvoicing.bv.pitches:
			for g in p.groups:
				if g == "Violoncello":
					pvcl['Cello'] += 1
				else:
					pvcl[g] += 1
		


def main():
	print("egg")

if __name__ == "__main__":
	main()