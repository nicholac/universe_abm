'''
Created on 16 Mar 2017

@author: dusted-ipro

Processing for the entire world / environment

'''
#Externals
import numpy as np
from scipy.spatial import distance

#Internals
from data.action_types import all_actions, action_sequences
from agents.base import numpify_agent, de_numpyify_agent, age_kill
from genetics.algorithms import reproduce


def process_agent(agent_doc, sysAgents, mongoColl):
    '''
    Wrapper for processing a single agent
    '''
    #Find close Agents
    d = distance.cdist([agent_doc['position']], [j['coords'][0] for j in sysAgents])
    #Check completed group activity
    if agent_doc['actyData']['complete'] == True:
        #Cycle next in Sequence
        seq = action_sequences()[agent_doc['agentType']]['actyGroups'][agent_doc['actyGroup']]['seq']
        idx = agent_doc['actyData']['actyIdx']+1
        #Rotate if at end
        if idx >= len(seq):
            idx = 0
        #Set new acty in seq
        agent_doc['actyData']['actyId'] = seq[idx]
        agent_doc['actyData']['actyIdx'] = idx
        agent_doc['actyData']['complete'] = False
    #Numpify the agent data
    numpify_agent(agent_doc)
    #Do the activity
    all_actions()[agent_doc['actyData']['actyId']]['actyFunc'](agent_doc, sysAgents, mongoColl)
    #Prep for return
    #Increment its epoch
    agent_doc['epoch']+=1
    #Convert numpy data for serialisation
    de_numpyify_agent(agent_doc)


def process_genetics(mongo_coll):
    '''
    Master only routine to run through agent population and do genetic functions
    '''
    world_doc = mongo_coll.find({'_type':'world'}).next()
    agents = list(mongo_coll.find({'_type':'agent'}))
    #Randomise agent selection
    idxs = range(len(agents))
    while len(idxs)!=0:
        i = np.random.choice(idxs)
        idxs.pop(idxs.index(i))
        agent = agents[i]
        #Kill old agents - and some random young ones
        if age_kill(agent, world_doc['maxAge']) == True:
            agent['_type'] = 'deadAgent'
            agent['reasonForDeath'] = 'age'
            mongo_coll.update({'_id':agent['_id']}, agent)
        else:
            #Run the reproduction GA - this does all the updates internally
            reproduce(agent, mongo_coll, world_doc)
