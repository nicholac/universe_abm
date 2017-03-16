'''
Created on 25 Dec 2016

@author: dusted-ipro

Generic Support Functions
'''
import numpy as np
from environment import world

'''
import pickle
from time import time
import os
import pygraphviz as pgv

from environment import world
from celestials.base import basePlanet, baseStar
from data.celestialTypes import planets, stars
from agents.explorer import explorer
from agents.fabricator import fabricator
from agents.harvestor import harvestor
from agents.trader import trader
from clans.base import baseClan
from data.tradableTypes import allTradables
from data.agentTypes import allAgents
from data.socialLinkTypes import allLinks
from datetime import datetime
'''

#==============================================================#
#DEPRECATED TO MONGO BUT USEFUL FOR INIT
# def generateAgents():
#     '''
#     Generate an initial seed number of agents for new universe
#     0=Explorer
#     1=Fabricator
#     2=Harvestor
#     3=Trader
#     '''
#     print 'Generating Agents...'
#     #Mix of types [ex, fa, ha, tr] (percentages of total popn)
#     #Single clan for now:
#     cnt = 0
#     clanUID = world.clans.keys()[0]
#     for idx, t in enumerate(world.agentTypeMix):
#         for a in range(int((t/100.0)*world.maxPopn)):
#             print cnt
#             cnt+=1
#             #Capacities & Rates
#             caps = world.genHarvestorCaps()
#             rates = world.genHarvestorRates()
#             maxVelMag = world.genAgentMaxVelMag()
#             #Get the next agent UID
#             agentUID = world.nextAgentUID()
#             if idx == 0:
#                 #Explorer
#                 a = explorer(0, agentUID,
#                               world.clans[clanUID].originCoords,
#                               clanUID, world.agentBaseVis, world.agentReprodChance,
#                               world.timeStep, world.socialLinkAgeRate, maxVelMag,
#                               np.random.choice([9,10]))
#             elif idx == 1:
#                 #Fabricator
#                 a = fabricator(1, agentUID,
#                               world.clans[clanUID].originCoords,
#                               clanUID,
#                               clanUID, world.agentBaseVis, world.agentReprodChance,
#                               world.timeStep, world.socialLinkAgeRate, maxVelMag,
#                               np.random.choice(allTradables().keys()))
#             elif idx == 2:
#                 #Harvestor
#                 caps = world.genHarvestorCaps()
#                 rates = world.genHarvestorRates()
#                 a = harvestor(2, agentUID,
#                               world.clans[clanUID].originCoords,
#                               clanUID,
#                               clanUID, world.agentBaseVis, world.agentReprodChance,
#                               world.timeStep, world.socialLinkAgeRate, maxVelMag,
#                               caps[0], caps[1], caps[2],
#                               rates[0], rates[1], rates[2], rates[3])
#             elif idx == 3:
#                 #Trader
#                 a = trader(3, agentUID,
#                               clanUID, world.agentBaseVis, world.agentReprodChance,
#                               world.timeStep, world.socialLinkAgeRate, maxVelMag,
#                               world.clans[clanUID].originCoords,
#                               world.clans.keys()[0])
#             else:
#                 pass
#             #Add as node in world graph
#             world.globalSocialNet.add_node(agentUID, type='agent_{}'.format(allAgents()[idx]))
#             #Initialise the agents social network link with clan here (its a new universe)
#             world.globalSocialNet.add_edge(agentUID, clanUID, {allLinks()[0]:world.clanLinkStren})
#             #Add to world lookup
#             #NEXT: WORK THROUGH MOVING AGENT STORAGE TO SYSTEMS
#             world.agents[agentUID] = a
#             #Add to clan lookup
#             world.clans[clanUID].agents.append(agentUID)
#
#     print 'Done Generating Agents'
#==============================================================#

def delAgent(agentUID, reason):
    '''
    Remove an Agent from the universe:
        - Class
        - Social Network
        - Clan
        - Star system
        - Record death
    '''
    pass


def starTemplate():
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

def planetTemplate():
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

def clanTemplate():
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

def agentTemplate():
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

def explorerTemplate():
    '''
    Explorer agent template - extends agentTemplate
    '''
    a = {'resourceType':np.random.choice([9,10])}
    #Use the base agent template
    b = agentTemplate()
    b.update(a.copy())
    return b


#Probability generation
def positiveProbsLin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward higher numbers
    '''
    return np.arange(numSamps)/np.sum(np.arange(numSamps))


def negativeProbsLin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward lower numbers
    '''
    return positiveProbsLin(numSamps)[::-1]


def positiveProbsPow(numSamps):
    '''
    Create a power (y=x^2) distribution weighted toward higher numbers
    '''
    t = np.power(np.arange(numSamps),2.0)
    return t/np.sum(t)


def negativeProbsPow(numSamps):
    '''
    Create a linear (y=x^2) distribution weighted toward lower numbers
    '''
    return positiveProbsPow(numSamps)[::-1]


def positiveProbsExp(numSamps):
    '''
    Create a exponential distribution weighted toward higher numbers
    '''
    t = np.exp2(np.arange(numSamps))
    return t/np.sum(t)


def negativeProbsExp(numSamps):
    '''
    Create a exponential distribution weighted toward lower numbers
    '''
    return positiveProbsExp(numSamps)[::-1]

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

def crossover_traits():
    '''
    List of all traits that can be crossed-over
    '''
    return ['vis', 'velMag', 'defence', 'offence']

def vis_bounds():
    '''
    Min and max for visibility trait
    '''
    return world.au2Ly(0.1), world.au2Ly(50.0)

def vel_mag_bounds():
    '''
    Min and max for vel_mag trait
    '''
    return world.au2Ly(1.0), world.au2Ly(10.0)

def offence_bounds():
    '''
    Min and max for offence trait
    '''
    return 0.0, 1.0

def mutation_bounds():
    '''
    Min and max for amount traits can be mutated by (%)
    '''
    return -0.1, 0.1






