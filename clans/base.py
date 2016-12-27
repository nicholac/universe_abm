'''
Created on 25 Dec 2016

@author: dusted-ipro
'''

import numpy as np
import collections
from environment.sensing import closestStar, closestStarSubSet
from environment import world


class baseClan(object):
    '''
    Base Clan Class
    '''

    def __init__(self, starIdx, coords, planetIdx, clanId):
        '''
        Constructor
        '''
        self.clanId = clanId
        self.clanName = 'clan_{}'.format(self.clanId)
        #Where's home - these are the planet coords - not star
        self.originCoords = coords
        self.originName = ''
        #Closest Star - index in world.starCoords
        self.originStarIdx = starIdx
        #Origin Planet
        self.originPlanetIdx = planetIdx
        #Array of all the clans agents - index lookup to world.agents
        self.agents = []
        #n Agents * n Agents matrix of link strength (2d array)
        self.societyNet = np.zeros((len(self.agents), len(self.agents)))
        #n Agents * n Agents matrix of demand and supply (3d array)
        self.tradeNet = np.zeros((len(self.agents), len(self.agents), 2))
        #Resource Knowledge {starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, planetIdx:{'rawMat':X, 'energy':Y}}}
        #Initially populated with all stars - and no knowledge
        self.resourceKnowledge = {}
        #Agent job queues
        #Explorer - (starIdx, starCoords)
        self.explorerQ = collections.deque()


    def popn(self):
        '''
        Get the clans total population
        ::return int total number of agents
        '''
        return len(self.agents)


    def agentPositions(self):
        '''
        Get the locations of all agents in this clan
        ::return array of agent.positions
        '''
        return [agent.position for agent in self.agents]


    def societyStrength(self):
        '''
        Get some basic measure of the society network strength
        ::return float 0 (weak) -> 1(strong)
        '''
        return np.sum(self.societyNet)/len(self.agents)

    def closestUnknownStar(self, coords):
        '''
        Get the star index of the closest clan unknown (unscanned) system
        '''
        uk = []
        for k in self.resourceKnowledge.keys():
            if self.resourceKnowledge[k] == {}:
                uk.append(world.starCoords[k])
        return closestStarSubSet(coords, uk)


    def rxResourceKnowledge(self, inputKnowledge):
        '''
        Receive resource knowledge from an explorer or other
        '''
        for inK in inputKnowledge.keys():
            #Check if star knowledge exists
            if inK not in self.resourceKnowledge.keys():
                #New star
                self.resourceKnowledge[inK] = inputKnowledge[inK]
            else:
                #Star exists - check we have all the planets
                for inP in inputKnowledge[inK]:
                    if inP not in self.resourceKnowledge[inK].keys():
                        self.resourceKnowledge[inK][inP] = inputKnowledge[inK][inP]





