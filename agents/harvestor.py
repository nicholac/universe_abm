'''
Created on 25 Dec 2016

@author: dusted-ipro
'''
from agents.base import baseAgent
from data.tradableTypes import allTradables
import numpy as np

class harvestor(baseAgent):
    '''
    Harvestor Agent
    '''

    def __init__(self, agentType, agentId, coords, clan, harvestType):
        '''
        HarvestType is either raw mats or energy
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clan)
        self.demands = {'id':0, 'strength':1.0, 'store':0.0, 'name':allTradables()[0]}
        self.supplies = {'id':harvestType, 'strength':1.0, 'store':0.0, 'name':allTradables()[harvestType]}
        self.consumes = [{'id':0, 'rate':1.0, 'store':0.0}]
        self.energy = {'amount':0.0, 'usageRate':1.0}
        #AU
        self.collectDist = 1.0
        #Tons per sec
        self.collectRate = 1.0
        #LY / Sec
        self.maxSpeed = 1.0