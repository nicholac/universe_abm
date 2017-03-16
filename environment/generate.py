'''
Created on 16 Mar 2017

@author: dusted-ipro
'''
from random import choice

import numpy as np

#Internals
from data.templates import world_template, agent_template, explorer_template, \
                            clan_template, star_template, planet_template
from data.celestial_types import stars, planets
from data.support_funcs import au2Ly


def generate_world(mongo_coll, clean):
    '''
    Generate and insert the master world doc
    '''
    if clean == True:
        mongo_coll.remove({'_type':'world'})
        print 'Cleaned World Doc'
    world_doc = world_template()
    #Push world doc
    mongo_coll.insert(world_doc)
    print 'Inserted World Doc'
    return


def generate_celestials(mongo_coll, clean):
    '''
    Generate and store celestials in Mongo

    ::param mongoColl Mongo Collection instantiated for celestials
    ::param clean boolean delete existing celestials
    '''
    print 'Generating Celestials...'
    if clean == True:
        mongo_coll.remove({'_type':'star'})
        mongo_coll.remove({'_type':'planet'})
        print 'Cleaned Celestials'
    numPlanetsIns = 0
    numStarsIns = 0
    #Get world doc for vars
    world_doc = mongo_coll.find({'_type':'world'}).next()
    starCoords = list(np.dstack([np.random.normal(world_doc['universeDims'][0]/2.0, world_doc['universeDims'][0]/3.0, size=world_doc['numStars']),
                                 np.random.normal(world_doc['universeDims'][1]/2.0, world_doc['universeDims'][1]/3.0, size=world_doc['numStars']),
                                 np.random.normal(world_doc['universeDims'][2]/2.0, world_doc['universeDims'][2]/3.0, size=world_doc['numStars'])])[0])
    #Generate the star classes
    for idx, c in enumerate(starCoords):
        starDoc = star_template()
        starDoc['_type'] ='star'
        starDoc['position']=list(c)
        starDoc['radius']=np.random.choice(world_doc['starRadiusOpts'])
        starDoc['typeId']=np.random.choice(stars().keys())
        starDoc['energyStore']= np.random.choice(world_doc['starEnergyOpts'])
        starDoc['epoch']=0
        starId = mongo_coll.insert(starDoc)
        #Push the coords into world array
        mongo_coll.find_and_modify({'_type':'world'}, {'$push':{'starCoords':list(c)}})
        numStarsIns+=1
        #Generate planets for this star
        numPlanets = int(np.random.choice([world_doc['avgPlanets']/2.0, world_doc['avgPlanets'], world_doc['avgPlanets']*2.0]))
        #Generate coords for the entire system - initially these are relative to star centre
        planetCoords = list(np.dstack([np.random.normal(world_doc['solarSystemDims'][0]/2.0, world_doc['solarSystemDims'][0]/3.0, size=numPlanets),
                                        np.random.normal(world_doc['solarSystemDims'][1]/2.0, world_doc['solarSystemDims'][1]/3.0, size=numPlanets),
                                        np.random.normal(world_doc['solarSystemDims'][2]/2.0, world_doc['solarSystemDims'][2]/3.0, size=numPlanets)])[0])
        for pidx, pc in enumerate(planetCoords):
            #Generate the planet class
            #Rebase coords relative to this star system
            coords = c+pc
            #starIdx, coords, radius, planetIdx, typeId, energyStore, rawMatStore
            planetDoc = planet_template()
            planetDoc['_type']='planet'
            planetDoc['starId'] = starId
            planetDoc['position']=list(coords)
            planetDoc['radius']=np.random.choice(world_doc['planetRadiusOpts'])
            planetDoc['typeId']=np.random.choice(planets().keys())
            planetDoc['energyStore']=np.random.choice(world_doc['planetEnergyOpts'])
            planetDoc['rawMatStore']=np.random.choice(world_doc['planetRawMatOpts'])
            mongo_coll.insert(planetDoc)
    #Validate
    if mongo_coll.find({'_type':'star'}).count() != numStarsIns:
        print 'Warning validate failed - missing stars or planets after world build'
    else:
        print 'Validate OK - Num Stars Inserted: {}, num planets inserted: {}'.format(numStarsIns, numPlanetsIns)
    print 'Saved updated world doc params'



def generate_clans(mongo_coll, clean):
    '''
    Initialise and setup clans
    ::param clanColl MongoCollection instantiated
    ::param clean boolean delete existing clans
    '''
    if clean == True:
        mongo_coll.remove({'_type':'clan'})
        print 'Cleaned Clans'
    print 'Generating Clans...'
    #Get the world doc
    world_doc = mongo_coll.find({'_type':'world'}).next()
    #Home Location - pick randomly
    star = choice(list(mongo_coll.find({'_type':'star'})))
    planet = choice(list(mongo_coll.find({'_type':'planet', 'starId':star['_id']})))
    clan = clan_template()
    clan['_type']='clan'
    clan['starId']=star['_id']
    clan['position']=planet['position']
    clan['planetId']=planet['_id']
    clan['energyConsumeRate']=world_doc['clanConsumeRates'][0]
    #Fill the resource knowledge with all the stars
    sysCoords = list(mongo_coll.find({'_type':'star', '_id':{'$ne':star['_id']}},
                                    {'position':1,
                                     '_id':1}))
    clan['starCatalogue'] = sysCoords
    #TODO: Something smarter than presuming every clan knows about all stars form the start?
    #TODO: Add Clan node into social graph
    clan['resourceKnowledge']=[] #maps to [starId:id,
                                        #  planets:[{id:x, nrg:x, rawMat:x},...]}]
    mongo_coll.insert(clan)
    #Validate
    if mongo_coll.find({'_type':'clan'}).count() != 1:
        print 'Warning validate failed - missing clans after world build'
    else:
        print 'Validate OK - Clans'
    print 'Done Generating Clans'


def generate_agents(mongo_coll, clean):
    '''
    Generate an initial seed number of agents for new universe
    0=Explorer
    1=Trader
    2=Harvestor
    3=soldier
    '''
    if clean == True:
        res = mongo_coll.delete_many({'_type':'agent'})
        res = mongo_coll.delete_many({'_type':'deadAgent'})
        print 'Cleaned all Agents'
    print 'Generating Agents...'
    #Get world doc
    world_doc = mongo_coll.find({'_type':'world'}).next()
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    #Single clan for now:
    cnt = 0
    clan = mongo_coll.find_one({'_type':'clan'})
    for idx, t in enumerate(world_doc['agentTypeMix']):
        for i in range(int((t/100.0)*world_doc['maxPopn']-10)):
            if idx == 0:
                #Explorer
                a = explorer_template()
                a = agent_template()
                a['agentType'] = 0
                a['clanId'] = clan['_id']
                a['socialLinkAgeRate'] = 0.0
                #GA Vector
                a['vis'] = np.random.choice(np.linspace(au2Ly(1.0), au2Ly(10.0)))
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
                res = mongo_coll.insert(a)
                cnt+=1
                if cnt%10 == 0:
                    print 'Done {}'.format(cnt)
    #Dump agent coords to star system
    #mongoColl.find_and_modify({'_type':'star'}, {"$set": {'agCoords':agCoords}})
    #Validate
    res = mongo_coll.find({'_type':'agent'}).count()
    print 'Total Agents in Mongo: {}'.format(res)




