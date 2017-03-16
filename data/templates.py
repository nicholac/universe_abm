'''
Created on 16 Mar 2017

@author: dusted-ipro

Mongo Doc Templates

'''
#Externals
import numpy as np

#Internals
from environment import world


def world_template():
    '''
    Template for the World Doc
    '''
    worldDoc = {'_type':'world',
                'procTimePerEpoch': 0.0,
                'numStars':200, #Total Stars
                'universeDims':[100.0, 100.0, 100.0], #Size of the universe (light-years)
                'solarSystemDims':[ world.au2Ly(10.0), #Average Solar system dimension - LY
                                       world.au2Ly(10.0),
                                       world.au2Ly(10.0) ],

                'avgPlanets':5, #Average planets per solar system
                'starEnergyOpts':list(np.linspace(1000.0, 1000000.0)), #Energy amounts possible on a star - MegaWatts?
                'starRadiusOpts':list(np.linspace(world.au2Ly(0.0001), world.au2Ly(0.1))), #Planet Sizes LY
                'planetEnergyOpts':list(np.linspace(0.0, 1000.0)), #Energy amounts possible on a planet - MegaWatts?
                'planetRawMatOpts':list(np.linspace(0.0, 1000.0)), #Raw Material amounts possible on a planet - Tons?
                'planetRadiusOpts':list(np.linspace(world.au2Ly(0.000001), world.au2Ly(0.001))), #Planet Sizes LY
                'timeStep': 0.1, #Timestep - seconds
                'epoch':1, #Epoch srats at 1 so we instantiate systems at epoch 0, and can start processing
                'runTime': 0.0, #Time elapsed since start
                'numClans':1, #Number of Clans
                'clanConsumeRates':list(world.genClanRates()), #Clan consumption rates
                #AGENT INFO
                'agentTypes':{'explorer':0, 'harvestor':1},
                'maxPopn': 100, #Max Population - initially
                'maxAge': 500, #Max Age (epochs) - after which chances of dying mount exponentially
                'minAgeReprod':50, #Reprod min age
                'maxAgeReprod': 300, #Reprod max age
                'agentTypeMix':[100.0, 0.0, 0.0, 0.0], #Mix of types [ex, fa, ha, tr] (percentages of total popn)
                'agentBaseVis':0.0, #Agent Base visibility = AU - These form the genetic vector and are instantiated on agent birth
                'agentBaseVelMax':0.0, #Agent base max velocity
                'agentBaseDefence':0.0, #Agent base Defence
                'agentBaseDefence':0.0, #Agent base Offence
                'harvestorCaps':world.genHarvestorCaps(), #Rates
                'harvestorRates':world.genHarvestorRates(),
                'starCoords':[], #Coordinates of star systems
                'popnOverTime':[], #Store for population over time
                'generationFitness':{}
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
            }
    return worldDoc

def star_template():
    '''
    Template Doc for stars
    '''
    starDoc = {'_type':'star',
               'position':[], #3d position
               'radius':0.0, #size of star
               'typeId':0, #type of star
               'energyStore': 0, #energy star holds
               'epoch':0, #processing epoch the star system is on
               'status':'waiting'
               }
    return starDoc

def planet_template():
    '''
    Planet Template Doc
    '''
    planetDoc = {'_type':'planet',
                 'starId':0, #Mongo Doc ID of the star system in which this planet resides
                 'position':[], #3D position of this star
                 'radius':0.0, #Size
                 'typeId':0, #Type of planet
                 'energyStore':0.0, #energy storage
                 'rawMatStore':0.0 #raw material storage
                 }
    return planetDoc

def clan_template():
    '''
    Template for Clans
    '''
    clan = {'_type':'clan',
            'starId':0, # mongo doc ID of home star
            'position':[], #coordinates of home planet
            'planetId':0, #mongo doc id of home planet
            'energyConsumeRate':0.0, #rate at which the society consumes energy
            'resourceKnowledge':{}, #data about known resources in the universe
            'starCatalogue':None
            }
    return clan

def agent_template():
    '''
    Template doc for agent
    '''
    a = {'_type':'agent',
         'agentType':0, #Type of agent
         'clanId':0, #Mongo Doc ID of clan
         'vis':0.0, #Range of visibility
         'reprodChance':0.0, #Chance of reproduction
         'socialLinkAgeRate':0.0, #Rate at which the agents social network ages
         'velMag':0.0, #Maximum Velocity
         'defence':0.0,
         'offence':0.0,
         'canReproduce':False,
         'reproduceOpts':[],
         'generation':0,
         'parent':False, #Whether the agent has already reproduced
         'actyGroup':0, #Current agent activity group
         'actyData':{'complete':False,
                     'actyId':0, #Current acty within the group
                     'actyIdx':0}, #Index of this acty in the group
         'destination':None, #Where the agent is heading to
         'position':[0.0, 0.0, 0.0], #3D position
         'velocity':[0.0, 0.0, 0.0], #3D velocity unit
         'starId':0, #star system agent currently resides in
         'epoch':0, #Current processing epoch
         'messages':[] #Inter-agent messages
         }
    return a

def explorer_template():
    '''
    Explorer agent template - extends agentTemplate
    '''
    a = {'resourceType':np.random.choice([9,10])}
    #Use the base agent template
    b = agent_template()
    b.update(a.copy())
    return b


def ga_fitness_template():
    '''
    Fitness doc template for base Genetic Algo fitness to breed
    0=Explorer
    1=Trader
    2=Harvestor
    3=Soldier
    '''
    out = {0:{'vis':{'val':world.au2Ly(3.0), 'operator':np.greater, 'desc':'visibility'},
                       'velMag':{'val':world.au2Ly(4.0), 'operator':np.greater, 'desc':'velocity max'},
                       'defence':{'val':0.1, 'operator':np.greater, 'desc':'defensive-ness'}},
           2:{'vis':{'val':world.au2Ly(3.0), 'operator':np.less, 'desc':'visibility'},
                       'velMag':{'val':world.au2Ly(3.0), 'operator':np.greater, 'desc':'velocity max'},
                       'defence':{'val':0.1, 'operator':np.greater, 'desc':'defensive-ness'}},
           1:{'velMag':{'val':world.au2Ly(7.0), 'operator':np.greater, 'desc':'velocity max'},},
           3:{'vis':{'val':world.au2Ly(2.0), 'operator':np.greater, 'desc':'visibility'},
                       'velMag':{'val':world.au2Ly(2.0), 'operator':np.greater, 'desc':'velocity max'},
                       'offence':{'val':0.3, 'operator':np.greater, 'desc':'offensive-ness'},
                       'defence':{'val':0.3, 'operator':np.greater, 'desc':'defensive-ness'}}
           }
    return out








