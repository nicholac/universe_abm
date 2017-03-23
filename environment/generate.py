'''
Created on 16 Mar 2017

@author: dusted-ipro
'''
from random import choice

import numpy as np

#Internals
from data.celestial_types import stars, planets
from data.support_funcs import au2Ly, load_config


def generate_world(mongo_coll, clean, master):
    '''
    Generate and insert the master world doc
    '''
    if clean == True:
        mongo_coll.remove({'_type':'world'})
        print 'Cleaned World Doc'
    #Load the config file
    config = load_config(master)
    #Run operations on config data as necessary - but the world (config) mongo doc essentially mirrors the input config JSON
    world_doc = mongify_config(config)
    #Push world doc
    mongo_coll.insert(world_doc)
    print 'Inserted World Doc'
    return


def mongify_config(config_data):
    '''
    Generate the world doc from the input config
    This just runs a few operations on the config_data
    Essentially the Mongo version mirrors the input JSON
    ::param Input config data
    '''
    config_data['universeInfo']['solarSystemDims'] = [ au2Ly(config_data['universeInfo']['solarSystemDims'][0]),
                                       au2Ly(config_data['universeInfo']['solarSystemDims'][1]),
                                       au2Ly(config_data['universeInfo']['solarSystemDims'][2]) ]
    config_data['universeInfo']['starEnergyOpts'] = list(np.linspace(config_data['universeInfo']['starEnergyOpts']['min'],
                                                     config_data['universeInfo']['starEnergyOpts']['max']))
    config_data['universeInfo']['starRadiusOpts'] = list(np.linspace(au2Ly(config_data['universeInfo']['starRadiusOpts']['min']),
                                                    au2Ly(config_data['universeInfo']['starRadiusOpts']['max'])))
    config_data['universeInfo']['planetEnergyOpts'] = list(np.linspace(config_data['universeInfo']['planetEnergyOpts']['min'],
                                                       config_data['universeInfo']['planetEnergyOpts']['max']))
    config_data['universeInfo']['planetRawMatOpts'] = list(np.linspace(config_data['universeInfo']['planetRawMatOpts']['min'],
                                                       config_data['universeInfo']['planetRawMatOpts']['max']))
    config_data['universeInfo']['planetRadiusOpts'] = list(np.linspace(au2Ly(config_data['universeInfo']['planetRadiusOpts']['min']),
                                                       au2Ly(config_data['universeInfo']['planetRadiusOpts']['max'])))

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

    return config_data


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
    starCoords = list(np.dstack([np.random.normal(world_doc['universeInfo']['universeDims'][0]/2.0,
                                                  world_doc['universeInfo']['universeDims'][0]/3.0,
                                                  size=world_doc['universeInfo']['numStars']),
                                 np.random.normal(world_doc['universeInfo']['universeDims'][1]/2.0,
                                                  world_doc['universeInfo']['universeDims'][1]/3.0,
                                                  size=world_doc['universeInfo']['numStars']),
                                 np.random.normal(world_doc['universeInfo']['universeDims'][2]/2.0,
                                                  world_doc['universeInfo']['universeDims'][2]/3.0,
                                                  size=world_doc['universeInfo']['numStars'])])[0])
    #Generate the star classes
    for idx, c in enumerate(starCoords):
        starDoc = world_doc['celestialInfo']['starInfo'].copy()
        starDoc['position']=list(c)
        starDoc['radius']=np.random.choice(world_doc['universeInfo']['starRadiusOpts'])
        starDoc['typeId']=np.random.choice(stars().keys())
        starDoc['energyStore']= np.random.choice(world_doc['universeInfo']['starEnergyOpts'])
        starDoc['epoch']=0
        starId = mongo_coll.insert(starDoc)
        #Push the coords into world array
        mongo_coll.find_and_modify({'_type':'world'}, {'$push':{'starCoords':list(c)}})
        numStarsIns+=1
        #Generate planets for this star
        numPlanets = int(np.random.choice([world_doc['universeInfo']['avgPlanets']/2.0,
                                           world_doc['universeInfo']['avgPlanets'],
                                           world_doc['universeInfo']['avgPlanets']*2.0]))
        #Generate coords for the entire system - initially these are relative to star centre
        planetCoords = list(np.dstack([np.random.normal(world_doc['universeInfo']['solarSystemDims'][0]/2.0,
                                                        world_doc['universeInfo']['solarSystemDims'][0]/3.0, size=numPlanets),
                                        np.random.normal(world_doc['universeInfo']['solarSystemDims'][1]/2.0,
                                                         world_doc['universeInfo']['solarSystemDims'][1]/3.0, size=numPlanets),
                                        np.random.normal(world_doc['universeInfo']['solarSystemDims'][2]/2.0,
                                                         world_doc['universeInfo']['solarSystemDims'][2]/3.0, size=numPlanets)])[0])
        for pidx, pc in enumerate(planetCoords):
            #Generate the planet class
            #Rebase coords relative to this star system
            coords = c+pc
            #starIdx, coords, radius, planetIdx, typeId, energyStore, rawMatStore
            planetDoc = world_doc['celestialInfo']['planetInfo'].copy()
            planetDoc['starId'] = starId
            planetDoc['position']=list(coords)
            planetDoc['radius']=np.random.choice(world_doc['universeInfo']['planetRadiusOpts'])
            planetDoc['typeId']=np.random.choice(planets().keys())
            planetDoc['energyStore']=np.random.choice(world_doc['universeInfo']['planetEnergyOpts'])
            planetDoc['rawMatStore']=np.random.choice(world_doc['universeInfo']['planetRawMatOpts'])
            mongo_coll.insert(planetDoc)
            numPlanetsIns+=1
    #Validate
    if mongo_coll.find({'_type':'star'}).count() != numStarsIns:
        print 'Warning validate failed - missing stars or planets after world build'
    else:
        print 'Validate OK - Num Stars Inserted: {}, num planets inserted: {}'.format(numStarsIns, numPlanetsIns)
    print 'Saved updated world doc params'



def generate_clans(mongo_coll, clean):
    '''
    Initialise and setup clans
    TODO: Allow run-time alteration of clans - currently wont work because of the star movement
    ::param clanColl MongoCollection instantiated
    ::param clean boolean delete existing clans
    '''
    if clean == True:
        mongo_coll.remove({'_type':'clan'})
        print 'Cleaned Clans'
    #Get the world doc
    print 'Generating Clans...'
    #Get the world doc
    world_doc = mongo_coll.find({'_type':'world'}).next()
    clanStars = []
    #Home Location - pick randomly
    stars = np.random.choice(list(mongo_coll.find({'_type':'star'})), size=world_doc['universeInfo']['numClans'])
    for idx, star in enumerate(stars):
        planet = choice(list(mongo_coll.find({'_type':'planet', 'starId':star['_id']})))
        clan = world_doc['clanInfo']
        clan['starId']=star['_id']
        clan['clanName'] = 'clan_{}'.format(idx)
        clan['position']=planet['position']
        clan['planetId']=planet['_id']
        sysCoords = list(mongo_coll.find({'_type':'star'},
                                         {'position':1,
                                         '_id':1}))
        clan['starCatalogue'] = sysCoords
        clan['resourceKnowledge']=[] #maps to [starId:id,planets:[{id:x, nrg:x, rawMat:x},...]}]
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
    clans = (mongo_coll.find({'_type':'clan'}))
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    #Single clan for now:
    for clan in clans:
        cnt = 0
        #clan = mongo_coll.find_one({'_type':'clan'})
        for idx, t in enumerate(world_doc['universeInfo']['agentTypeMix']):
            for i in range(int((t/100.0)*world_doc['universeInfo']['initPopn'])):
                agent = agent_generate_map(idx)(world_doc, clan)
                #Insert
                res = mongo_coll.insert(agent)
                cnt+=1
                if cnt%10 == 0:
                    print 'Done {}'.format(cnt)
        print 'Done Clan {}'.format(clan['clanName'])
    #Validate
    res = mongo_coll.find({'_type':'agent'}).count()
    print 'Total Agents in Mongo: {}'.format(res)


def agent_generate_map(agent_id):
    '''
    Returns the correct function for generating an agent
    '''
    map = {0:gen_explorer,
           1:gen_harvestor,
           2:gen_trader,
           3:gen_soldier}
    return map[agent_id]


def gen_explorer(world_doc, clan_doc):
    '''
    Specialise function for explorer agent generation
    '''
    #Explorer
    a = world_doc['agentInfo']['explorer'].copy()
    a['clanId'] = clan_doc['_id']
    #GA Vector
    a['vis'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['explorer']['visBounds']['min']),
                                            au2Ly(world_doc['agentInfo']['explorer']['visBounds']['max'])))
    a['velMag'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['explorer']['velMagBounds']['min']),
                                               au2Ly(world_doc['agentInfo']['explorer']['velMagBounds']['max'])))
    a['offence'] = np.random.choice(np.linspace(world_doc['agentInfo']['explorer']['offenceBounds']['min'],
                                                world_doc['agentInfo']['explorer']['offenceBounds']['max']))
    a['defence'] = np.random.choice(np.linspace(world_doc['agentInfo']['explorer']['defenceBounds']['min'],
                                                world_doc['agentInfo']['explorer']['defenceBounds']['max']))
    #/GA Vector
    a['actyGroup'] = 1 #Exploring Resources group
    a['actyData']['actyId'] = 5 #Idle
    a['destination'] = clan_doc['position']
    a['position'] = clan_doc['position']
    a['starId'] = clan_doc['starId']
    a['generation'] = 0
    return a


def gen_harvestor(world_doc, clan_doc):
    '''
    Specialise function for harvestor agent generation
    '''
    #Harvestor
    a = world_doc['agentInfo']['harvestor'].copy()
    a['clanId'] = clan_doc['_id']
    #GA Vector
    a['vis'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['harvestor']['visBounds']['min']),
                                            au2Ly(world_doc['agentInfo']['harvestor']['visBounds']['max'])))
    a['velMag'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['harvestor']['velMagBounds']['min']),
                                               au2Ly(world_doc['agentInfo']['harvestor']['velMagBounds']['max'])))
    a['offence'] = np.random.choice(np.linspace(world_doc['agentInfo']['harvestor']['offenceBounds']['min'],
                                                world_doc['agentInfo']['harvestor']['offenceBounds']['max']))
    a['defence'] = np.random.choice(np.linspace(world_doc['agentInfo']['harvestor']['defenceBounds']['min'],
                                                world_doc['agentInfo']['harvestor']['defenceBounds']['max']))
    #/GA Vector
    a['actyGroup'] = 1 #Trader Group
    a['actyData']['actyId'] = 5 #Idle
    a['destination'] = clan_doc['position']
    a['position'] = clan_doc['position']
    a['starId'] = clan_doc['starId']
    a['generation'] = 0
    return a

def gen_trader(world_doc, clan_doc):
    '''
    Specialise function for trader agent generation
    '''
    #Harvestor
    a = world_doc['agentInfo']['trader'].copy()
    a['clanId'] = clan_doc['_id']
    #GA Vector
    a['vis'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['trader']['visBounds']['min']),
                                            au2Ly(world_doc['agentInfo']['trader']['visBounds']['max'])))
    a['velMag'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['trader']['velMagBounds']['min']),
                                               au2Ly(world_doc['agentInfo']['trader']['velMagBounds']['max'])))
    a['offence'] = np.random.choice(np.linspace(world_doc['agentInfo']['trader']['offenceBounds']['min'],
                                                world_doc['agentInfo']['trader']['offenceBounds']['max']))
    a['defence'] = np.random.choice(np.linspace(world_doc['agentInfo']['trader']['defenceBounds']['min'],
                                                world_doc['agentInfo']['trader']['defenceBounds']['max']))
    #/GA Vector
    a['actyGroup'] = 1 #Trader Group
    a['actyData']['actyId'] = 5 #Idle
    a['destination'] = clan_doc['position']
    a['position'] = clan_doc['position']
    a['starId'] = clan_doc['starId']
    a['generation'] = 0
    return a


def gen_soldier(world_doc, clan_doc):
    '''
    Specialise function for soldier agent generation
    '''
    #Harvestor
    a = world_doc['agentInfo']['soldier'].copy()
    a['clanId'] = clan_doc['_id']
    #GA Vector
    a['vis'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['soldier']['visBounds']['min']),
                                            au2Ly(world_doc['agentInfo']['soldier']['visBounds']['max'])))
    a['velMag'] = np.random.choice(np.linspace(au2Ly(world_doc['agentInfo']['soldier']['velMagBounds']['min']),
                                               au2Ly(world_doc['agentInfo']['soldier']['velMagBounds']['max'])))
    a['offence'] = np.random.choice(np.linspace(world_doc['agentInfo']['soldier']['offenceBounds']['min'],
                                                world_doc['agentInfo']['soldier']['offenceBounds']['max']))
    a['defence'] = np.random.choice(np.linspace(world_doc['agentInfo']['soldier']['defenceBounds']['min'],
                                                world_doc['agentInfo']['soldier']['defenceBounds']['max']))
    #/GA Vector
    a['actyGroup'] = 1 #Soldier Group
    a['actyData']['actyId'] = 5 #Idle
    a['destination'] = clan_doc['position']
    a['position'] = clan_doc['position']
    a['starId'] = clan_doc['starId']
    a['generation'] = 0
    return a











