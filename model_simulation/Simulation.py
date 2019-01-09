
# coding: utf-8

#analysis for the output of this file is done in vibha's simulation

# In[1]:
import pandas as pd
import random
import os.path


# In[2]:
def find_stdev(x, mean):
    stdev = 0
    for number in x:
        stdev += (number - mean)**2
    stdev /= float(len(x))
    return stdev


# In[3]:
#Maximizing homophily strategy: pick the three with the closest scores to their own
def max_homophily(compare_scores, own_score):
    #Creates a dictionary with the difference from own score
    diff = dict()
    for person in compare_scores:
        diff[person] = abs(compare_scores[person] - own_score)
    #Picks top 3 similar ones
    #Note: if a tie in similarity to self, randomly chooses
    smallest = sorted(diff.items(), key=lambda t: t[1])[:3]
    return list(dict(smallest).keys())

#One sided homophily: pick the top 3 similar ones GIVEN that they are more extreme/closer to 10
def one_sided_homophily(compare_scores, own_score):
    diff = dict()
    for person in compare_scores:
        if compare_scores[person] - own_score >= 0:
            diff[person] = compare_scores[person] - own_score
    smallest = sorted(diff.items(), key=lambda t: t[1])[:3]
    return list(dict(smallest).keys())


# In[4]:
def simulation(agents, subjID, strategy):

    #Read in data for this participant
    me_path = 'data/' + subjID + '.csv'
    me = pd.read_csv(me_path, usecols = [3, 6])

    #Metrics over simulations
    averages = []
    diffs = []
    loyalties = []

    #Simulation
    for i in range(1000): #Repeating multiple times for each participant to get an average over random simulations

        #For the first iteration, we sample 6 random ones (different starting point than other iterations, so separate)
        pic_num = me['stimulus'][0]

        #List of possible people to choose from
        pick_from = list(agents)
        compare_scores = dict()

        #Pick random 6 people and map them to their scores
        for i in range(6):
            compare = random.choice(pick_from)
            compare_scores[compare] = agents[compare][pic_num]
            pick_from.remove(compare) #ensures we don't pick the same person twice

        #Initializing loyalty with 0 for every person seen
        loyalty = dict()
        for person in compare_scores:
            loyalty[person] = 0

        #Create our first 3 kept people
        own_score = me['subject_rating'][0]
        kept_people = strategy(compare_scores, own_score)

        # #For producing sample dataset
        # dropped = list(set(compare_scores.keys()) - set(kept_people))
        # sales = [(own_score, compare_scores, kept_people, dropped)]
        # labels = ['rating', 'agents seen', 'agents kept', 'agents eliminated']
        # sample = pd.DataFrame.from_records(sales, columns=labels)

        #For metrics
        analysis = []
        diff = []
        for person in kept_people:
            person_score = agents[person][pic_num]
            analysis.append(person_score)
            loyalty[person] += 1
            diff.append(abs(own_score - person_score))

        #For the rest of the iterations, we keep the three 'kept_people' and update their 'kept_scores' depending on the stimulus
        for i in range(1, len(me)):
            pic_num = me['stimulus'][i]
            own_score = me['subject_rating'][i]

            compare_scores = dict()

            #Update the kept people's scores depending on the stimulus
            for person in kept_people:
                compare_scores[person] = agents[person][pic_num]

            #Add 3 more random choices
            for i in range(3):
                new = random.choice(pick_from)
                compare_scores[new] = agents[new][pic_num]
                pick_from.remove(new)
                loyalty[new] = 0 #Hasn't seen them before

            #Use given strategy to pick top 3
            kept_people = strategy(compare_scores, own_score)

            #For metrics
            for person in kept_people:
                person_score = agents[person][pic_num]
                analysis.append(person_score)
                diff.append(abs(own_score - person_score))
                loyalty[person] += 1

        # #For sample dataset
        # dropped = list(set(compare_scores.keys()) - set(kept_people))
        # sample = sample.append(pd.Series({'rating': own_score, 'agents seen': compare_scores, 'agents kept': kept_people, 'agents eliminated' : dropped}), ignore_index = True)

        #Keeps track of average score of kept participants for this simulation
        #avg = sum(analysis) / float(len(analysis))
        #Adds it to results for all simulations run
        #averages.append(avg)
        averages += analysis
        #Keeps track of average distance from kept participants for this simulation
        #avg_diff = sum(diff) / float(len(diff))
        #Adds it to results for all simulations run
        #diffs.append(avg_diff)
        diffs += diff
        #Removes zeros from loyalties
        actual_loyalties = {x:y for x,y in loyalty.items() if y != 0}
        #Keeps track of avg. loyalty (number of trials kept someone for) for this simulation
        #avg_loyalty = float(sum(actual_loyalties.values())/len(actual_loyalties))
        #Adds it to results for all simulations run
        #loyalties.append(avg_loyalty)
        loyalties += actual_loyalties.values()

    #sample.to_csv("Sample_dataset.csv")

    #Find results for this person
    mean_mean = sum(averages) / float(len(averages))
    mean_stdev = find_stdev(averages, mean_mean)
    mean_low_CI = mean_mean - 1.96*mean_stdev #for 95% CI
    mean_high_CI = mean_mean + 1.96*mean_stdev #for 95% CI

    diff_mean = sum(diffs) / float(len(diffs))
    diff_stdev = find_stdev(diffs, diff_mean)
    diff_low_CI = diff_mean - 1.96*diff_stdev
    diff_high_CI = diff_mean + 1.96*diff_stdev

    #Finds average maximum loyalty
    loyalty_mean = sum(loyalties) / float(len(loyalties))
    loyalty_stdev = find_stdev(loyalties, loyalty_mean)
    loyalty_low_CI = loyalty_mean - 1.96*loyalty_stdev
    loyalty_high_CI = loyalty_mean + 1.96*loyalty_stdev

    results = [subjID, mean_mean, mean_low_CI, mean_high_CI, diff_mean, diff_low_CI, diff_high_CI, loyalty_mean, loyalty_low_CI, loyalty_high_CI]
    return results


# In[5]:


#Import agent data
agent_path = 'agent_ratings_MALE.csv'
agents = pd.read_csv(agent_path)
agents.index = range(1, 21) #1-index to be same as stimulus number

#For maximizing homophily strategy

homo_results = pd.DataFrame()

for i in range(91):
    if os.path.isfile('data/'+str(i)+'.csv'):
        subj = simulation(agents, str(i), max_homophily)
        homo_results = homo_results.append(pd.Series(subj), ignore_index = True)

homo_results.columns = ['id', 'average', 'average low CI', 'average high CI', 'difference', 'difference low CI', 'difference high CI', 'loyalty','loyalty low CI', 'loyalty high CI']
homo_results.to_csv("male_homophily.csv", index = False)

#For one-sided homophily strategy

oneside_results = pd.DataFrame()

for i in range(91):
    if os.path.isfile('data/'+str(i)+'.csv'):
        subj = simulation(agents, str(i), one_sided_homophily)
        oneside_results = oneside_results.append(pd.Series(subj), ignore_index = True)

oneside_results.columns = ['id', 'average', 'average low CI', 'average high CI', 'difference', 'difference low CI', 'difference high CI', 'loyalty','loyalty low CI', 'loyalty high CI']
oneside_results.to_csv("male_oneside_homophily.csv", index = False)
