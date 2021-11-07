



def exportDict(dic, filename, headers = []):

	csvDir = filename
	with open(csvDir, 'w') as output:

		columnTitleRow = ""
		for item in headers:
			columnTitleRow += item
			columnTitleRow += ','
		columnTitleRow += '\n'
		output.write(columnTitleRow)

		for key in dic:
			name = key
			val = dic[key]
			row = str(name) + "," + str(val) + '\n'
			output.write(row)


def exportList(listy, filename, headers = []):

	csvDir = filename
	with open(csvDir, 'w') as output:

		columnTitleRow = ""
		for item in headers:
			columnTitleRow += item
			columnTitleRow += ','
		columnTitleRow += '\n'
		output.write(columnTitleRow)

		for item in listy:
			name = item[0]
			val = item[1]
			row = str(name) + "," + str(val) + '\n'
			output.write(row)

# for use with tuples, changes the delimiter
def exportListTup(listy, filename, headers = []):

	csvDir = filename
	with open(csvDir, 'w') as output:

		columnTitleRow = ""
		for item in headers:
			columnTitleRow += item
			columnTitleRow += ','
		columnTitleRow += '\n'
		output.write(columnTitleRow)

		for item in listy:
			name = item[0]
			val = item[1]
			row = str(name) + "," + str(val) + '\n'
			output.write(row)


def main():

	# testDict = {1:2, 3:4, 5:6}
	# export(testDict, 'test.csv', headers = ['key', 'val'])

	st = 'ii6/5'
	print(st.replace('/', ''))

	giantProgDict = progs.Progs()
	giantProgDict.loadProgs("/Users/truszala/Documents/1JuniorSpring/python!/Music/Beethoven Quartets/giantProgDictStorage")
	gp = giantProgDict.progs
	print("gp loaded")


	





if __name__ == "__main__":
	main()



