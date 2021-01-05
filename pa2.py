# Written by Payam Azadi, December 2020 - Jan 2021
# A tool that ingests SURE data export and compares each county's ballot count
# to the number of votes tallied for President by NYT (which matches PA's county certification).
# You can use this code for free as long as attribution is provided.

import pandas as pd
import requests
import os
import multiprocessing as mp
from glob import glob
from functools import reduce
import json

# In: full path to a SURE export's county file (FVE, Full Voter Export)
# Out: a tuple of the county name, # registered, # voted (SURE), # voted (NYT), overcount, undercount
def processCounty(fullpath):
	global progressTemplate, nytCountyData
	undercountDiff = 0

	# This turns something like "/path/ALLEGHENY FVE.txt" into "Allegheny", to match NYT's JSON naming
	normalizedName = os.path.split(fullpath)[1].split(" ")[0].capitalize()
	
	# Uses the date last voted column (25) as a heuristic to count the number of ballots for 2020 election
	# This is actually not the proper algorithm. This file should be matched to a list of election identifiers
	# for each county, and the number of non-empty values in that particular column should be counted.
	data = pd.read_csv(fullpath, sep="\t", header=None)[25]
	numVoted = data.str.contains(r"11\/03\/2020").sum()

	numRegistered = len(data)
	numNytVoted = nytCountyData[normalizedName]
	overcountDiff = numNytVoted - numVoted
	
	if overcountDiff < 0:
		undercountDiff = abs(overcountDiff)
		overcountDiff = 0

	overcountDiffPercent = overcountDiff / numNytVoted
	undercountDiffPercent = undercountDiff / numVoted
	
	output = progressTemplate.format(normalizedName, numRegistered, numVoted, numNytVoted, numNytVoted / numRegistered)

	# This is basically a margin of error threshold and you can change it to whatever you want.
	# The diff % matters but for very small counties, even a couple of votes can make a big percentage
	# change. So there's an absolute vote minimum.
	if overcountDiffPercent > .005 and overcountDiff > 2000:
		output += " (Overcount {} {:.2%})".format(overcountDiff, overcountDiffPercent)
		print(output)

	if undercountDiffPercent > .005 and undercountDiff > 2000:
		output += " (Undercount {} {:.2%})".format(undercountDiff, undercountDiffPercent)
		print(output)

	return (normalizedName, numRegistered, numVoted, numNytVoted, overcountDiff, undercountDiff)

def getNytData():
	nytCountyData = json.loads(requests.get("https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/national-map-page/national/president.json").text)
	nytCountyData = {county["name"]: county["results"]["bidenj"] + county["results"]["trumpd"] + county["results"]["jorgensenj"] for county in nytCountyData["data"]["races"][38]["counties"]}
	# Capitalization issue betwen the state export and NYT
	nytCountyData["Mckean"] = nytCountyData["McKean"]
	return nytCountyData

# Main entry point
# 1. Ingest entire NYT dataset (not just PA) 
# 2. Use *map* and multiprocessing to quickly ingest disparate county data into single dataset and marry it to NYT data
# 3. Separate out the overcount from the undercount
# 4. Add up overcounts and undercounts
# 5. Spit out totals
if __name__ == '__main__':
	finalOutput = "Registered:{} Dump:{} NYT:{} Overcount:{}({:.2%}) Undercount:{}({:.2%}) Turnout:{:.2%}"
	progressTemplate = "{} - Registered:{} Dump:{} NYT:{} Turnout:{:.2%}"
	undercountCounties = 0
	overcountCounties = 0

	pool = mp.Pool(mp.cpu_count())
	
	nytCountyData = getNytData()	
	countyResults = pool.map(processCounty, glob("/Users/payamazadi/Downloads/Statewide" + "/* FVE*"))

	# The most pythonic way I could come up with to sum up the 'columns' of this list of tuples
	# Somewhat pedantic, but I like it because it iterates over the combined, summed dataset once,
	# instead of once per entry in tuple.
	(_, totalRegistered, totalVoted, totalNytVoted, totalOvercount, totalUndercount) = reduce(lambda x,y: ("", x[1]+y[1], x[2]+y[2], x[3]+y[3], x[4]+y[4], x[5]+y[5]), countyResults)
	
	overcountDiffPercent = totalOvercount / totalNytVoted
	undercountDiffPercent = totalUndercount / totalVoted

	print("\n\n---TOTAL---\n" + finalOutput.format(totalRegistered, totalVoted, totalNytVoted, totalOvercount, overcountDiffPercent, totalUndercount, undercountDiffPercent, totalVoted / totalRegistered))
	print("({} Counties)".format(len(countyResults)))