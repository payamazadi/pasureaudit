import pandas as pd
import requests
import os
import warnings
import multiprocessing as mp
from glob import glob
from functools import reduce
import json

warnings.filterwarnings('ignore')
progressTemplate = "{} - Registered:{} Dump:{} NYT:{} Turnout:{:.2%}"

nytData = json.loads(requests.get("https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/national-map-page/national/president.json").text)
nytCountyData = {county["name"]: county["results"]["bidenj"] + county["results"]["trumpd"] + county["results"]["jorgensenj"] for county in nytData["data"]["races"][38]["counties"]}
nytCountyData["Mckean"] = nytCountyData["McKean"]

def processCounty(fullpath):
	global progressTemplate, nytCountyData
	
	# data = pd.Series(np.genfromtxt(fullpath, dtype=str, delimiter="\t", filling_values="", invalid_raise=False)[:,25])
	data = pd.read_csv(fullpath, sep="\t", header=None)[25]
	
	normalizedName = os.path.split(fullpath)[1].split(" ")[0].capitalize()
	numRegistered = len(data)
	numVoted = data.str.contains("11\/03\/2020").sum()
	numNytVoted = nytCountyData[normalizedName]
	overcountDiff = numNytVoted - numVoted
	undercountDiff = 0
	if overcountDiff < 0:
		undercountDiff = abs(overcountDiff)
		overcountDiff = 0

	overcountDiffPercent = overcountDiff / numNytVoted
	undercountDiffPercent = undercountDiff / numVoted
	
	output = progressTemplate.format(normalizedName, numRegistered, numVoted, numNytVoted, numNytVoted / numRegistered)

	if overcountDiffPercent > .005 and overcountDiff > 2000:
		output += " (Overcount {} {:.2%})".format(overcountDiff, overcountDiffPercent)
		print(output)
	# else:
	# 	overcountDiff = 0

	if undercountDiffPercent > .005 and undercountDiff > 2000:
		output += " (Undercount {} {:.2%})".format(undercountDiff, undercountDiffPercent)
		print(output)
	# else:
	# 	undercountDiff = 0

	del data
	# gc.collect()
	
	return (normalizedName, numRegistered, numVoted, numNytVoted, overcountDiff, undercountDiff)

if __name__ == '__main__':
	pool = mp.Pool(mp.cpu_count())
	finalOutput = "Registered:{} Dump:{} NYT:{} Overcount:{}({:.2%}) Undercount:{}({:.2%}) Turnout:{:.2%}"
	undercountCounties = 0
	overcountCounties = 0

	countyResults = pool.map(processCounty, glob("/Users/payamazadi/Downloads/Statewide" + "/* FVE*"))
	(_, totalRegistered, totalVoted, totalNytVoted, totalOvercount, totalUndercount) = reduce(lambda x,y: ("", x[1]+y[1], x[2]+y[2], x[3]+y[3], x[4]+y[4], x[5]+y[5]), countyResults)
	overcountDiffPercent = totalOvercount / totalNytVoted
	undercountDiffPercent = totalUndercount / totalVoted

	print("\n\n---TOTAL---\n" + finalOutput.format(totalRegistered, totalVoted, totalNytVoted, totalOvercount, overcountDiffPercent, totalUndercount, undercountDiffPercent, totalVoted / totalRegistered))
	print("({} Counties)".format(len(countyResults)))
	print(progressTemplate)