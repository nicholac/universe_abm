'''
Created on 21 Jan 2017

@author: dusted-ipro
'''
import os, sys
from time import sleep
# Ensure paths then use . package notation and __init__ files.
this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if this_dir not in sys.path:
    sys.path.append(this_dir)

from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId

import numpy as np
from random import choice
from time import time
from bson.binary import Binary
import pickle
from scipy.spatial import distance
from pprint import pprint

from environment import world
from data.celestialTypes import stars, planets
from data.supportFuncs import agentTemplate, explorerTemplate, clanTemplate, starTemplate, planetTemplate, positiveProbsExp, positiveProbsPow
from data.action_types import all_actions, action_sequences

from mongo_agents.base import numpify_agent, de_numpyify_agent

from genetics.algorithms import reproduce, age_kill



def generateWorld(mongoColl, clean):
    '''
    Generate the master world doc
    '''
    if clean == True:
        mongoColl.remove({'_type':'world'})
        print 'Cleaned World Doc'
    worldDoc = {'_type':'world'}
    worldDoc['procTimePerEpoch'] = 0.0
    #Total Stars
    worldDoc['numStars'] = 200
    #Size of the universe (light-years)
    worldDoc['universeDims'] = [100.0, 100.0, 100.0]
    #Average Solar system dimension - LY
    d = world.au2Ly(10.0)
    worldDoc['solarSystemDims'] = [d, d, d]
    #Average planets per solar system
    worldDoc['avgPlanets'] = 5
    #Energy amounts possible on a star - MegaWatts?
    worldDoc['starEnergyOpts'] = list(np.linspace(1000.0, 1000000.0))
    #Planet Sizes LY
    d = world.au2Ly(0.0001)
    e = world.au2Ly(0.1)
    worldDoc['starRadiusOpts'] = list(np.linspace(d, e))

    #Energy amounts possible on a planet - MegaWatts?
    worldDoc['planetEnergyOpts'] = list(np.linspace(0.0, 1000.0))
    #Raw Material amounts possible on a planet - Tons?
    worldDoc['planetRawMatOpts'] = list(np.linspace(0.0, 1000.0))
    #Planet Sizes LY
    d = world.au2Ly(0.000001)
    e = world.au2Ly(0.001)
    worldDoc['planetRadiusOpts'] = list(np.linspace(d, e))

    #Timestep - seconds
    worldDoc['timeStep'] = 0.1
    #Epoch srats at 1 so we instantiate systems at epoch 0, and can start processing
    worldDoc['epoch'] = 1

    #Time elapsed since start
    worldDoc['runTime'] = 0.0

    #Number of Clans
    worldDoc['numClans'] = 1
    #Clan consumption rates
    worldDoc['clanConsumeRates'] = list(world.genClanRates())

    #AGENT INFO
    worldDoc['agentTypes'] = {'explorer':0, 'harvestor':1}
    #Max Population - initially
    worldDoc['maxPopn'] = 100
    #Max Age (epochs) - after which chances of dying mount exponentially
    worldDoc['maxAge'] = 500
    #Reprod min age
    worldDoc['minAgeReprod'] = 50
    #Reprod max age
    worldDoc['maxAgeReprod'] = 300
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    worldDoc['agentTypeMix'] = [100.0, 0.0, 0.0, 0.0]
    #Agent Base visibility = AU - These form the genetic vector and are instantiated on agent birth
    worldDoc['agentBaseVis'] = 0.0
    #Agent base max velocity
    worldDoc['agentBaseVelMax'] = 0.0
    #Agent base Defence
    worldDoc['agentBaseDefence'] = 0.0
    #Agent base Offence
    worldDoc['agentBaseDefence'] = 0.0
    #Rates
    worldDoc['harvestorCaps'] = world.genHarvestorCaps()
    worldDoc['harvestorRates'] = world.genHarvestorRates()
    #Coordinates of star systems
    worldDoc['starCoords'] = []
    #Store for population over time
    worldDoc['popnOverTime'] = []
    worldDoc['generationFitness'] = {}
    #########################################
    #Society Globals - Nodes are integers of agent or clan UID's - the actual classes can be accessed via the global dict\
    #NOTE: Social Nets now stored per-agent (to allow distribution)
    #TODO: This allows a global view of all the social networks
    #globalSocialNet = nx.Graph()
    #Rate at which social links age (link strength per tick)
    #socialLinkAgeRate = 0.01
    #Clan Link strength - base link strength between agent and clan (Clan links dont age)
    #clanLinkStren = 0.1
    #Link creation strengths - base weight
    #chatLinkMinStrength = -5.0
    #chatLinkMaxStrength = 5.0
    #BAse chance of a social link being created - 50/50
    #baseSocialLinkCreationSplit = [True, False]
    ##########################################
    #Push world doc
    mongoColl.insert(worldDoc)
    print 'Inserted World Doc'
    return



def generateCelestials(mongoColl, clean):
    '''
    Generate and store celestials in Mongo

    ::param mongoColl Mongo Collection instantiated for celestials
    ::param clean boolean delete existing celestials
    '''
    print 'Generating Celestials...'
    if clean == True:
        mongoColl.remove({'_type':'star'})
        mongoColl.remove({'_type':'planet'})
        print 'Cleaned Celestials'
    numPlanetsIns = 0
    numStarsIns = 0
    #Get world doc for vars
    worldDoc = mongoColl.find({'_type':'world'}).next()
    starCoords = list(np.dstack([np.random.normal(worldDoc['universeDims'][0]/2.0, worldDoc['universeDims'][0]/3.0, size=worldDoc['numStars']),
                                 np.random.normal(worldDoc['universeDims'][1]/2.0, worldDoc['universeDims'][1]/3.0, size=worldDoc['numStars']),
                                 np.random.normal(worldDoc['universeDims'][2]/2.0, worldDoc['universeDims'][2]/3.0, size=worldDoc['numStars'])])[0])
    #Generate the star classes
    for idx, c in enumerate(starCoords):
        starDoc = starTemplate()
        starDoc['_type'] ='star'
        starDoc['position']=list(c)
        starDoc['radius']=np.random.choice(worldDoc['starRadiusOpts'])
        starDoc['typeId']=np.random.choice(stars().keys())
        starDoc['energyStore']= np.random.choice(worldDoc['starEnergyOpts'])
        starDoc['epoch']=0
        starId = mongoColl.insert(starDoc)
        #Push the coords into world array
        mongoColl.find_and_modify({'_type':'world'}, {'$push':{'starCoords':list(c)}})
        numStarsIns+=1
        #Generate planets for this star
        numPlanets = int(np.random.choice([worldDoc['avgPlanets']/2.0, worldDoc['avgPlanets'], worldDoc['avgPlanets']*2.0]))
        #Generate coords for the entire system - initially these are relative to star centre
        planetCoords = list(np.dstack([np.random.normal(worldDoc['solarSystemDims'][0]/2.0, worldDoc['solarSystemDims'][0]/3.0, size=numPlanets),
                                        np.random.normal(worldDoc['solarSystemDims'][1]/2.0, worldDoc['solarSystemDims'][1]/3.0, size=numPlanets),
                                        np.random.normal(worldDoc['solarSystemDims'][2]/2.0, worldDoc['solarSystemDims'][2]/3.0, size=numPlanets)])[0])
        for pidx, pc in enumerate(planetCoords):
            #Generate the planet class
            #Rebase coords relative to this star system
            coords = c+pc
            #starIdx, coords, radius, planetIdx, typeId, energyStore, rawMatStore
            planetDoc = planetTemplate()
            planetDoc['_type']='planet'
            planetDoc['starId'] = starId
            planetDoc['position']=list(coords)
            planetDoc['radius']=np.random.choice(worldDoc['planetRadiusOpts'])
            planetDoc['typeId']=np.random.choice(planets().keys())
            planetDoc['energyStore']=np.random.choice(worldDoc['planetEnergyOpts'])
            planetDoc['rawMatStore']=np.random.choice(worldDoc['planetRawMatOpts'])
            mongoColl.insert(planetDoc)
    #Validate
    if mongoColl.find({'_type':'star'}).count() != numStarsIns:
        print 'Warning validate failed - missing stars or planets after world build'
    else:
        print 'Validate OK - Num Stars Inserted: {}, num planets inserted: {}'.format(numStarsIns, numPlanetsIns)
    print 'Saved updated world doc params'


def generateClans(mongoColl, clean):
    '''
    Initialise a set a clans

    ::param clanColl MongoCollection instantiated
    ::param clean boolean delete existing clans
    '''
    if clean == True:
        mongoColl.remove({'_type':'clan'})
        print 'Cleaned Clans'
    print 'Generating Clans...'
    #Get the world doc
    worldDoc = mongoColl.find({'_type':'world'}).next()
    #Home Location - pick randomly
    star = choice(list(mongoColl.find({'_type':'star'})))
    planet = choice(list(mongoColl.find({'_type':'planet', 'starId':star['_id']})))
    clan = clanTemplate()
    clan['_type']='clan'
    clan['starId']=star['_id']
    clan['position']=planet['position']
    clan['planetId']=planet['_id']
    clan['energyConsumeRate']=worldDoc['clanConsumeRates'][0]
    #Fill the resource knowledge with all the stars
    sysCoords = list(mongoColl.find({'_type':'star', '_id':{'$ne':star['_id']}},
                                    {'position':1,
                                     '_id':1}))
    clan['starCatalogue'] = sysCoords
    #TODO: Something smarter than presuming every clan knows about all stars form the start?
    #TODO: Add Clan node into social graph
    clan['resourceKnowledge']=[] #maps to [starId:id,
                                        #  planets:[{id:x, nrg:x, rawMat:x},...]}]
    mongoColl.insert(clan)
    #Validate
    if mongoColl.find({'_type':'clan'}).count() != 1:
        print 'Warning validate failed - missing clans after world build'
    else:
        print 'Validate OK - Clans'
    print 'Done Generating Clans'


def generateAgents(mongoColl, clean):
    '''
    Generate an initial seed number of agents for new universe
    0=Explorer
    1=Trader
    2=Harvestor
    3=soldier
    '''
    if clean == True:
        res = mongoColl.delete_many({'_type':'agent'})
        res = mongoColl.delete_many({'_type':'deadAgent'})
        print 'Cleaned all Agents'
    print 'Generating Agents...'
    #Get world doc
    worldDoc = mongoColl.find({'_type':'world'}).next()
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    #Single clan for now:
    cnt = 0
    clan = mongoColl.find_one({'_type':'clan'})
    for idx, t in enumerate(worldDoc['agentTypeMix']):
        for i in range(int((t/100.0)*worldDoc['maxPopn']-10)):
            if idx == 0:
                #Explorer
                a = explorerTemplate()
                a = agentTemplate()
                a['agentType'] = 0
                a['clanId'] = clan['_id']
                a['socialLinkAgeRate'] = world.socialLinkAgeRate
                #GA Vector
                a['vis'] = np.random.choice(np.linspace(world.au2Ly(1.0), world.au2Ly(10.0)))
                a['velMag'] = world.genAgentMaxVelMag()
                a['offence'] = np.random.choice(np.linspace(0.0, 0.4))
                a['defence'] = np.random.choice(np.linspace(0.0, 0.4))
                #/GA Vector
                a['actyGroup'] = 1 #Exploring Resources group
                a['actyData']['actyId'] = 5 #Idle
                a['destination'] = []
                a['position'] = clan['position']
                a['starId'] = clan['starId']
                a['generation'] = 0
                #Insert
                res = mongoColl.insert(a)
                cnt+=1
                if cnt%10 == 0:
                    print 'Done {}'.format(cnt)
    #Dump agent coords to star system
    #mongoColl.find_and_modify({'_type':'star'}, {"$set": {'agCoords':agCoords}})
    #Validate
    res = mongoColl.find({'_type':'agent'}).count()
    print 'Total Agents in Mongo: {}'.format(res)


def run(numSteps, mongoColl, master):
    '''
    Run the world
    '''
    print 'Running'
    step = 0
    sysProcCnt = 0
    totTimeExternal = 0.0
    while True:
        start = time()
        #print 'Systems processed: {}'.format(sysProcCnt)
        step+=1
        #Get the current processing epoch
        epoch = mongoColl.find({'_type':'world'}, {'epoch':1}).next()['epoch']
        #Get a copy of the current world doc aswell
        world = mongoColl.find({'_type':'world'}).next()
        #Pop a system
        try:
            sys = mongoColl.find_one_and_update({'_type':'star','epoch':epoch-1,'status':'waiting'},
                                                {'$set':{'status':'processing'}},
                                                return_document=ReturnDocument.AFTER)
            status = list(mongoColl.aggregate([{'$match':{'_type':'star'}},
                                                    {'$group':{'_id':'null', 'status':{'$push':'$status'}}}]))
            if not sys:
                raise StopIteration
        except StopIteration:
            #All Systems and agents processed for this epoch
            if master == True:
                #Run the agent reproduction routines
                print 'Running Genetics...'
                process_genetics(mongoColl)
                print 'Done Genetics'
                #Increment the world
                print 'Increment world, epoch: {}'.format(epoch)
                epochTime = time()-start
                #Record the population at this epoch
                mongoColl.find_one_and_update({'_type':'world'},
                                              {'$set':{'procTimePerEpoch':epochTime}})
                #Record the population at this epoch
                cnt = mongoColl.find({'_type':'agent'}).count()
                mongoColl.find_one_and_update({'_type':'world'},
                                              {'$push':{'popnOverTime':{'epoch_{}'.format(epoch):cnt}}})
                sysProcCnt = 0
                #No more systems to process in this epoch - incrememnt world (any node can do this)
                mongoColl.find_and_modify({'_type':'world'}, {"$inc": {'epoch':1}})
                mongoColl.update_many({'_type':'star'}, {"$set": {'status':'waiting'}})
                #List of status data about systems
                status = list(mongoColl.aggregate([{'$match':{'_type':'star'}},
                                                        {'$group':{'_id':'null', 'status':{'$push':'$status'}}}]))
                #print 'Star Sys Status: {}'.format(status)
                continue
            else:
                #Client - wait for others
                sleep(0.5)
                continue
        i = 0
        cnt = mongoColl.count({'_type':'agent', 'starId':sys['_id']})
        if cnt > 0:
            agents = list(mongoColl.find({'_type':'agent', 'starId':sys['_id']}))
            '''
            #Check the agent actys
            actys = mongoColl.aggregate([{'$match':{'_type':'agent'}},
                                                    {'$group':{'_id':'null', 'actyGroup':{'$push':'$actyGroup'},
                                                               'actySeq':{'$push':'$actyData.actyId'},
                                                               'status':{'$push':'$actyData.complete'}}}])

            print 'Agent Status: {}'.format(actys.next()['actySeq'])
            '''
            #print 'Agents in Sys: {}'.format(len(agents))

            #Get all the initial state agent coordinates
            sysAgents = list(mongoColl.aggregate([{'$match':{'_type':'agent', 'starId':sys['_id']}},
                                                {'$group':{'_id':'$_id', 'coords':{'$push':'$position'}}}]))
            #print 'Got Agent Coords'
            for agent in agents:
                process_agent(agent, sysAgents, mongoColl)
            #Push all the agents back up to server
            for agent in agents:
                mongoColl.update({'_id':agent['_id']}, agent)
        else:
            #Skipped System
            pass
        #print 'Average Time per sys run: {}'.format(avgTimeExt)
        #Update the system epoch - everything else is seperate docs
        mongoColl.find_and_modify({'_type':'star', '_id':sys['_id']},
                                  {"$inc": {'epoch':1}, '$set':{'status':'complete'}})
        sysProcCnt+=1
    print 'Exiting Run'


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
    print len(idxs)
    while len(idxs)!=0:
        i = np.random.choice(idxs)
        idxs.pop(idxs.index(i))
        agent = agents[i]
    #for agent in agents:
        #Kill old agents - and some random young ones
        if age_kill(agent, world_doc['maxAge']) == True:
            agent['_type'] = 'deadAgent'
            agent['reasonForDeath'] = 'age'
            mongo_coll.update({'_id':agent['_id']}, agent)
        else:
            #Run the reproduction GA - this does all the updates internally
            reproduce(agent, mongo_coll, world_doc)



if __name__ == '__main__':
    #Connect to collection
    cli = MongoClient()
    db = cli.universeabm
    agentColl = db.agents
    celestialsColl = db.celestials
    universeColl = db.universe

    master = True
    reset = True

    if master == True and reset == True:
        generateWorld(universeColl, True)
        generateCelestials(universeColl, True)
        generateClans(universeColl, True)
        generateAgents(universeColl, True)


    run(10, universeColl, master)

    cli.close()
    print 'Done'
    '''
    NEXT: The algorithm converges now, and fast - for explorers
    NEXT:  Get the explorers doing something - watch resourceknowledge bug
    NEXT: Graph other stuff, like % fit for all types, fitness scores
    Start cleaning it up - seems like it may actually be working
    Break out configuration into a file to make it more easily tweaked
    Write some damn unit tests
    Make the new Mongo stuff the main routine
    Give it some system args for the cluster master / slave running
    Setup a run env on Digital Ocean
    Try more agents
    Try more clans
    Automatically limit population based on the resources available - pop/resources = less chance of reprod
    Increase mutation as a function of low popn - so we have more chance of the right genes appearing
    '''







