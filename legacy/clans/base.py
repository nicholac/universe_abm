'''
Created on 25 Dec 2016

@author: dusted-ipro
'''

import numpy as np
import collections
from environment.sensing import closestStar, closestStarSubSet
from environment import world



def closestStar(position, star_coords):
    '''
    Return the closest star from the given list of starCoords - idx and coords
    ::param position x,y,z array
    ::param star_coords array of xyz coords
    '''
    idx = np.argmin([np.linalg.norm(np.array(position)-x) for x in star_coords])
    return star_coords[idx]


#=============================#
#DEPRECATED BUT USED FOR MONGO CONVERSION
# class baseClan(object):
#     '''
#     Base Clan Class
#     '''
#
#     def __init__(self, starIdx, coords, planetIdx, clanId, energyConsumeRate):
#         '''
#         Constructor
#         '''
#         self.clanId = clanId
#         self.clanName = 'clan_{}'.format(self.clanId)
#         #Where's home - these are the planet coords - not star
#         self.originCoords = coords
#         self.originName = ''
#         #Closest Star - index in world.starCoords
#         self.originStarIdx = starIdx
#         #Origin Planet
#         self.originPlanetIdx = planetIdx
#         #Array of all the clans agents - dict key lookup to world.agents
#         self.agents = []
#         #n Agents * n Agents matrix of link strength (2d array)
#         self.societyNet = np.zeros((len(self.agents), len(self.agents)))
#         #n Agents * n Agents matrix of demand and supply (3d array)
#         self.tradeNet = np.zeros((len(self.agents), len(self.agents), 2))
#         #Resource Knowledge {starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, planetIdx:{'rawMat':X, 'energy':Y}}}
#         #Initially populated with all stars - and no knowledge
#         self.resourceKnowledge = {}
#         #Agent job queues
#         #Explorer - (starIdx, starCoords) - unknown places
#         self.explorerQ = collections.deque()
#         #Harvestor - this is basically the resource knowledge sorted by distance
#         self.harvestorQ = collections.deque()
#
#         #Clan Global Resource storage
#         self.demands = {7:{'store':10.0}}
#         #{tradableId:storeAmount, ...}
#         self.store = {0:{'store':0.0}, 1:{'store':0.0}, 2:{'store':0.0},
#                          3:{'store':0.0}, 4:{'store':0.0}, 5:{'store':0.0},
#                          6:{'store':0.0}, 7:{'store':0.0}, 8:{'store':0.0},
#                          9:{'store':0.0}, 10:{'store':0.0}}
#         self.consumes = {7:{'consumeRate':energyConsumeRate, 'store':10.0}}
#
#
#     def popn(self):
#         '''
#         Get the clans total population
#         ::return int total number of agents
#         '''
#         return len(self.agents)
#
#
#     def agentPositions(self):
#         '''
#         Get the locations of all agents in this clan
#         ::return array of agent.positions
#         '''
#         return [agent.position for agent in self.agents]
#
#
#     def societyStrength(self):
#         '''
#         Get some basic measure of the society network strength
#         ::return float 0 (weak) -> 1(strong)
#         '''
#         return np.sum(self.societyNet)/len(self.agents)
#
#     def closestUnknownStar(self, coords):
#         '''
#         Get the star index of the closest clan unknown (unscanned) system
#         '''
#         uk = []
#         for k in self.resourceKnowledge.keys():
#             if self.resourceKnowledge[k] == {}:
#                 uk.append(world.starCoords[k])
#         return closestStarSubSet(coords, uk)
#
#
#     def rxResourceKnowledge(self, inputKnowledge):
#         '''
#         Receive resource knowledge from an explorer or other
#         '''
#         for inK in inputKnowledge.keys():
#             #Check if star knowledge exists
#             if inK not in self.resourceKnowledge.keys():
#                 #New star
#                 self.resourceKnowledge[inK] = inputKnowledge[inK]
#                 #Add all the planets to the harvestorQ - just the star and planet indexes as tuples
#                 for p in inputKnowledge[inK].keys():
#                     self.harvestorQ.append((inK, p, inputKnowledge[inK][p]))
#             else:
#                 #Star exists - check we have all the planets
#                 for inP in inputKnowledge[inK]:
#                     if inP not in self.resourceKnowledge[inK].keys():
#                         self.resourceKnowledge[inK][inP] = inputKnowledge[inK][inP]
#                         #Add it to the resource Q
#                         self.harvestorQ.append((inK, inP, inputKnowledge[inK][inP]))
#         #Reorder Harvestor Q - closest first
#         self.orderHarvestorQ()
#
#
#     def orderHarvestorQ(self):
#         '''
#         Take a moment to re-order the harvestorQ by distance from clan origin
#         So we can just pop the first one off at any stage
#         '''
#         dists = []
#         for i in self.harvestorQ:
#             dists.append(np.linalg.norm(world.stars[i[0]].planets[i[1]].position-self.originCoords))
#         chk = sorted(zip(dists, self.harvestorQ))
#         self.harvestorQ.clear()
#         for i in chk:
#             self.harvestorQ.append(i[1])
#=================================#











