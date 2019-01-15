import os.path
import pandas as pd
import itertools

DATA_PATH = '../'

def combinatoric(agent_scores):
	#Finds all possible choices of 3 agent scores from these 6
	agent_scores = list(agent_scores.values())
	combinations = list(itertools.combinations(agent_scores, 3))
	#Find the sums of each of these combinations and rank them
	sums = []
	for item in combinations:
		summed = item[0] + item[1] + item[2]
		sums.append(summed)
	sums = sorted(sums)
	return sums

def simulation(subjID):
	me_path = DATA_PATH + subjID + '.csv'
	me = pd.read_csv(me_path)

	for i in range(len(me)):
		#Get all *seen* agent scores for this stimulus
		agent_scores = dict()
		for j in range(1, 7):
			agent_scores[me['a%s_name'%j][i]] = me['a%s_rating'%j][i]
		print("Seen agents:")
		print(agent_scores)
		#Find all combinatoric possiblities
		possible_sums = combinatoric(agent_scores)
		print("Possible sums:")
		print(possible_sums)
		#Find picked possibility
		picked_agents = dict()
		for j in range(1, 4):
			picked_agents[me['kept_%s_name'%j][i]] = me['kept_%s_rating'%j][i]

		picked_scores = list(picked_agents.values())
		picked_sum = 0
		for j in range(len(picked_scores)):
			picked_sum += picked_scores[j]
		print("Picked agents:")
		print(picked_agents)
		print("Picked sum:")
		print(picked_sum)

		#Find ranking in comparison
		rank = 0
		for j in range(len(possible_sums)):
			if possible_sums[j] < picked_sum:
				rank += 1
		print("Ranking:")
		print(rank)

#Can iterate through all subjects to produce some output sheet, but check above first
simulation('3')

