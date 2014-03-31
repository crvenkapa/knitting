import os
import pandas as pd
import numpy as np

def avg(e):
	votes = [int(s) for s in e.split(';')]
	votes = np.array(votes)
	total_votes = sum(votes)
	if total_votes == 0:
		return np.NaN
	else:
		return votes.dot(np.arange(1, votes.size + 1))/float(total_votes)

def sum_rating(e):
	votes = [int(s) for s in e.split(';')]
	return sum(votes)

for f in os.listdir("data"):
	if "stats" in f:
		data = pd.read_csv(os.path.join("data", f))
		data["avgdiff"] = data['diff_rating'].apply(avg)
		data["votesdiff"] = data['diff_rating'].apply(sum_rating)
		data["avgstars"] = data['star_rating'].apply(avg)
		data["votesstars"] = data['star_rating'].apply(sum_rating)
		data.to_csv(os.path.join("data",
			os.path.splitext(f)[0] + "_ext.csv"), index=False)
