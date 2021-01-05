# PA Sure Vote Auditor
On December 28, Pennsylania GOP lawmakers wrote [a letter](http://www.repfrankryan.com/News/18754/Latest-News/PA-Lawmakers-Numbers-Don%E2%80%99t-Add-Up,-Certification-of-Presidential-Results-Premature-and-In-Error) saying that more than 200,000 people voted than were registered to vote. President Trump tweeted about this, and somebody replied to it claiming to have validated the claim and pointing to the data. I decided to check the numbers for myself.

The file referenced is not an original source of truth for voter registration. So no claims of unregistered voters voting can be made against it. It is actually a post-election audit system, which tallies ballots and voter registration.

This Python script ingests the county-by-county data from the file the lawmakers are referencing, and unifies it with county-by-county data from the New York Times and compares overcounts and undercounts.

As of January 3 2021, the data from the export file aligns almost exactly with the NYT count, except for Philadelphia and Allegheny, who have not fully submitted data to SURE yet.

A detailed explanation of the context, and tracing through the results step by step, is provided in breakdown.md. A visual representation with a summarized tabulation of the data in Comparison.xlsx.

The claims [were debunked](https://www.dos.pa.gov/about-us/Documents/statements/2020-12-29-Response-PA-GOP-Legislators-Misinformation.pdf) less than a day later by the Pennsylvania Department of State, with explanations mirroring those made here.

# How to run
1. Check out this repository
2. Download the SURE data exports from [here](https://www.pavoterservices.pa.gov/Pages/PurchasePAFULLVoterExport.aspx) (requires $20 USD and a fake (or real) Pennsylvania driver's license). Save the "Statewide" folder to the root of the repository.
3. pip install requirements.txt
4. python pa2.py