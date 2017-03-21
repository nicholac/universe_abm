'''
Created on 1 Mar 2017

@author: dusted-ipro

Genetic Algorithms for Agents

Selection, Crossover and Mutation
Fitness attributes initially:
[visdist, maxvel, defence, offence]

Future potential additions:
[num friends/total agents, num enemies/total agents]

'''

import numpy as np
from random import random, choice
import copy
from data.support_funcs import au2Ly


def reproduce(agent_doc, mongo_coll, world_doc):
    '''
    Top-level reproduction func
    Called per-agent, per epoch - on the master node after the system has been processed
    '''
    #Has the agent already reproduced?
    #if agent_doc['parent'] == True:
    #    return
    #Are we between the min max ages?
    if agent_doc['epoch'] < world_doc['minAgeReprod'] or agent_doc['epoch'] > world_doc['maxAgeReprod']:
        return
    #Is the agent fit to reproduce - with any type?
    #Do this first so we get a pool of potential partners when at max pop
    fitness_chk = fitness(agent_doc, fitness_scoring())
    #NEXT: It gets stuck here when turning reqs back down because existing agemts dont get fitness recalculated
    #if agent_doc['canReproduce'] == False:
    #Is it fit to reproduce with its OWN TYPE
    if [i['canReprod'] for i in fitness_chk if i['_type'] == agent_doc['agentType']][0] == False:
        #Not fit to repro with own type
    #Any Type:
    #if not any([i['canReprod'] for i in fitness_chk]) == True:
        #Not fit for anything
        return
    else:
        #Update agent
        agent_doc['canReproduce'] = True
        agent_doc['reproduceOpts'] = fitness_chk

    #Are we at max population (two children)?
    #TODO: This should be clan max popn not world
    #cnt = mongo_coll.find({'_type':'agent', 'clanId':agent_doc['clanId']}).count()
    cnt = mongo_coll.find({'_type':'agent'}).count()
    if cnt >= world_doc['maxPopn']:
        #Store agent and return
        mongo_coll.update({'_id':agent_doc['_id']}, agent_doc)
        return

    #Can Reproduce - Find a partner in same clan - randomise select
    #For mixed breeding:
    #partner_type = [i['_type'] for i in fitness_chk if i['canReprod'] == True]
    partners = list(mongo_coll.find({'_type':'agent',
                          'clanId':agent_doc['clanId'],
                          'canReproduce':True,
                          #For mixed breeding: 'agentType':{'$in':partner_type},
                          'agentType':agent_doc['agentType']},
                          #removed requirement for not being parent: 'parent':False},
                         {'_id':1, 'reproduceOpts':1}))
    if len(partners) == 0:
        #No valid partners in clan
        mongo_coll.update({'_id':agent_doc['_id']}, agent_doc)
        #print 'No partners'
        return
    #Select a partner - weighted toward fitter partners
    #print 'Partners:{}'.format(partners)

    #Create probability scores
    scores = []
    for p in partners:
        #Only explorers at this stage
        score = [i['fitScore'] for i in p['reproduceOpts'] if i['_type'] == agent_doc['agentType']][0]
        scores.append(score)
    #Convert in probs - get sum of all scores, convert scores to proportion of sum
    #print 'scores:{}'.format(scores)
    #try:
    print 'Scores:{}, {}'.format(len(scores), len(partners))
    probs = [i/sum(scores) for i in scores]
    partner = np.random.choice(partners, p=probs)

    #except Exception, err:
        #Weird div by zero error
        #print 'Scores:{}'.format(scores)
        #Just select one at random
        #partner = np.random.choice(partners)

    #Get full partner doc
    partner_doc = mongo_coll.find({'_id':partner['_id']}).next()

    #Crossover
    #NOTE: Here we are crossing over all available traits, instead of just the ones used for fitness selection
    #We may have situations where two different types of agents have been selected ,
    #This means that no matter what the pairing we include all traits in the genetic crossover
    gene_split_pos = np.random.choice(range(len(world_doc['gaInfo']['crossoverTraits'])))
    child_1, child_2 = crossover(agent_doc, partner_doc,
                                 world_doc['gaInfo']['crossoverTraits'], gene_split_pos)

    #Mutate
    mutation(child_1,
             world_doc['gaInfo']['crossoverTraits'],
             world_doc['gaInfo']['mutationBounds']['min'],
             world_doc['gaInfo']['mutationBounds']['max'])
    mutation(child_2, world_doc['gaInfo']['crossoverTraits'],
             world_doc['gaInfo']['mutationBounds']['min'],
             world_doc['gaInfo']['mutationBounds']['max'])

    #Reset some child attrs
    clan_doc = mongo_coll.find({'_id':agent_doc['clanId']},
                                        {'starId':1, 'position':1}).next()
    child_1['position'] = clan_doc['position']
    child_1['actyGroup'] = 0 #Idle
    child_1['actyData']['actyId'] = 0 #Idle
    child_1['destination'] = []
    child_1['starId'] = clan_doc['starId']
    child_1['parent'] = False
    child_1['canReproduce'] = False
    child_1['reproduceOpts'] = None
    child_1['epoch'] = 0

    child_2['position'] = clan_doc['position']
    child_2['actyGroup'] = 0 #Idle
    child_2['actyData']['actyId'] = 0 #Idle
    child_2['destination'] = []
    child_2['starId'] = clan_doc['starId']
    child_2['parent'] = False
    child_2['canReproduce'] = False
    child_2['reproduceOpts'] = None
    child_2['epoch'] = 0


    #Reset parents
    agent_doc['parent'] = True
    agent_doc['canReproduce'] = False
    agent_doc['reproduceOpts'] = None
    partner_doc['parent'] = True
    partner_doc['canReproduce'] = False
    partner_doc['reproduceOpts'] = None

    #Send back to mongo
    mongo_coll.update({'_id':agent_doc['_id']}, agent_doc)
    mongo_coll.update({'_id':partner_doc['_id']}, partner_doc)
    mongo_coll.insert(child_1)
    mongo_coll.insert(child_2)




def fitness(agent, fitness_doc):
    '''
    Checks if the given agent has the skills required to reproduce with an agent type(s)
    ::param agent agent doc
    ::param fitness dict of required attributes
    ::return boolean True - can reproduce, false cant
    '''
    out = []
    for k in fitness_doc:
        #Agent Types
        chk = True
        #Generate some indication of HOW fit, other than just boolean
        fitScore = 0.0
        for i in fitness_doc[k].keys():
            #Fitness measures
            #print fitness_doc[k][i]['operator'], agent[i], fitness_doc[k][i]['val']
            if fitness_doc[k][i]['operator'](agent[i], fitness_doc[k][i]['val']) == False:
                chk = False
            #Add to fit score - get the absolute diff
            #So further away it is in either greater or less direction the fitter you are
            fitScore += abs(agent[i] - fitness_doc[k][i]['val'])
        if chk == True:
            d = {'_type':k,
                'canReprod':chk,
                'fitScore':fitScore}
        else:
            d = {'_type':k,
                'canReprod':chk,
                'fitScore':0.0}
        out.append(d.copy())
    return out


def crossover(agent_1, agent_2, trait_list, gene_split_pos):
    '''
    Breed the two agents & crossover their attributes
    ::param gene_pos - where to splice the genes for crossover
    ::param trait_list list of trait keys to crossover
    ::return child_1, child_2 two dicts - new agent docs
    '''
    #Build the Chromosomes
    chromo_1 = []
    for i in agent_1.keys():
        if i in trait_list:
            chromo_1.append(agent_1[i])
    chromo_2 = []
    for i in agent_2.keys():
        if i in trait_list:
            chromo_2.append(agent_2[i])
    #Crossover
    child_1_chromo = chromo_2[:gene_split_pos]+chromo_1[gene_split_pos:]
    child_2_chromo = chromo_1[:gene_split_pos]+chromo_2[gene_split_pos:]
    #print chromo_1, chromo_2, child_2_chromo
    #Pick what the new agent type will be (the mating may not be between same type)
    #child_1_type = np.random.choice([agent_1['_type'], agent_2['_type']])
    #child_2_type = np.random.choice([agent_1['_type'], agent_2['_type']])
    #Create two new agent docs - clone parent first -
    child_1_doc = copy.deepcopy(agent_1)
    #Reset ID
    child_1_doc.pop('_id')
    #Insert the mutated traits
    for idx, trait in enumerate(child_1_chromo):
        child_1_doc[trait_list[idx]] = trait

    child_2_doc = copy.deepcopy(agent_2)
    child_2_doc.pop('_id')
    for idx, trait in enumerate(child_2_chromo):
        child_2_doc[trait_list[idx]] = trait
    #Increment generation
    child_1_doc['generation']+=1
    child_2_doc['generation']+=1
    #Return Children
    return child_1_doc, child_2_doc


def mutation(agent, trait_list, mutation_min, mutation_max):
    '''
    Mutate a new childs genes by random factors
    ::param agent agent child doc
    ::param trait_list list of traits that can be mutated / crossed over
    ::return altered child doc
    '''
    #Mutate each trait a little - (1 - 30% of what it is after crossover)
    for t in trait_list:
        agent[t] += (np.random.choice(np.linspace(mutation_min, mutation_max)) * agent[t])


def fitness_scoring():
    '''
    Fitness doc template for base Genetic Algo fitness to breed
    0=Explorer
    1=Trader
    2=Harvestor
    3=Soldier
    '''
    out = {0:{'vis':{'val':au2Ly(3.0), 'operator':np.greater, 'desc':'visibility'},
                       'velMag':{'val':au2Ly(4.0), 'operator':np.greater, 'desc':'velocity max'},
                       'defence':{'val':0.1, 'operator':np.greater, 'desc':'defensive-ness'}},
           2:{'vis':{'val':au2Ly(3.0), 'operator':np.less, 'desc':'visibility'},
                       'velMag':{'val':au2Ly(3.0), 'operator':np.greater, 'desc':'velocity max'},
                       'defence':{'val':0.1, 'operator':np.greater, 'desc':'defensive-ness'}},
           1:{'velMag':{'val':au2Ly(7.0), 'operator':np.greater, 'desc':'velocity max'},},
           3:{'vis':{'val':au2Ly(2.0), 'operator':np.greater, 'desc':'visibility'},
                       'velMag':{'val':au2Ly(2.0), 'operator':np.greater, 'desc':'velocity max'},
                       'offence':{'val':0.3, 'operator':np.greater, 'desc':'offensive-ness'},
                       'defence':{'val':0.3, 'operator':np.greater, 'desc':'defensive-ness'}}
           }
    return out




