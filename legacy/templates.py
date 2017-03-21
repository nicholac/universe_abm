'''
Created on 16 Mar 2017

@author: dusted-ipro

Mongo Doc Templates

'''
#Externals
import numpy as np

#Internals
from data.support_funcs import au2Ly

# def star():
#     '''
#     Template Doc for stars
#     '''
#     starDoc = {'_type':'star',
#                'position':[], #3d position
#                'radius':0.0, #size of star
#                'typeId':0, #type of star
#                'energyStore': 0, #energy star holds
#                'epoch':0, #processing epoch the star system is on
#                'status':'waiting'
#                }
#     return starDoc
#
# def planet():
#     '''
#     Planet Template Doc
#     '''
#     planetDoc = {'_type':'planet',
#                  'starId':0, #Mongo Doc ID of the star system in which this planet resides
#                  'position':[], #3D position of this star
#                  'radius':0.0, #Size
#                  'typeId':0, #Type of planet
#                  'energyStore':0.0, #energy storage
#                  'rawMatStore':0.0 #raw material storage
#                  }
#     return planetDoc

# def clan():
#     '''
#     Template for Clans
#     '''
#     clan = {'_type':'clan',
#             'starId':0, # mongo doc ID of home star
#             'position':[], #coordinates of home planet
#             'planetId':0, #mongo doc id of home planet
#             'energyConsumeRate':0.0, #rate at which the society consumes energy
#             'resourceKnowledge':{}, #data about known resources in the universe
#             'starCatalogue':None
#             }
#     return clan

# def agent():
#     '''
#     Template doc for agent
#     '''
#     a = {'_type':'agent',
#          'agentType':0, #Type of agent
#          'clanId':0, #Mongo Doc ID of clan
#          'vis':0.0, #Range of visibility
#          'reprodChance':0.0, #Chance of reproduction
#          'socialLinkAgeRate':0.0, #Rate at which the agents social network ages
#          'velMag':0.0, #Maximum Velocity
#          'defence':0.0,
#          'offence':0.0,
#          'canReproduce':False,
#          'reproduceOpts':[],
#          'generation':0,
#          'parent':False, #Whether the agent has already reproduced
#          'actyGroup':0, #Current agent activity group
#          'actyData':{'complete':False,
#                      'actyId':0, #Current acty within the group
#                      'actyIdx':0}, #Index of this acty in the group
#          'destination':None, #Where the agent is heading to
#          'position':[0.0, 0.0, 0.0], #3D position
#          'velocity':[0.0, 0.0, 0.0], #3D velocity unit
#          'starId':0, #star system agent currently resides in
#          'epoch':0, #Current processing epoch
#          'messages':[], #Inter-agent messages
#          'generation':0
#          }
#     return a

# def explorer():
#     '''
#     Explorer agent template - extends agentTemplate
#     '''
#     a = {'resourceType':np.random.choice([9,10])}
#     #Use the base agent template
#     b = agent()
#     b.update(a.copy())
#     return b








