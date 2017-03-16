'''
Created on 25 Dec 2016

@author: dusted-ipro
'''
from agents.base import baseAgent
from data.tradableTypes import allTradables
import numpy as np

class fabricator(baseAgent):
    '''
    Fabricator Agent
    '''

    def __init__(self, agentType, agentId, coords, clan, goodType):
        '''
        Constructor
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clan)
        self.demands = {'id':2, 'strength':1.0, 'store':0.0, 'name':allTradables()[2]}
        #Fabricators only supply a single thing
        self.supplies = {'id':goodType, 'strength':1.0, 'store':0.0, 'name':allTradables()[goodType]}
        self.consumes = [{'id':2, 'rate':1.0, 'store':0.0}]
        self.energy = {'amount':0.0, 'usageRate':1.0}
        #Production info - Tons per sec
        self.prodRateBase = 1.0
        self.prodRateMult = 1.0
        #LY / Sec
        self.maxSpeed = 0.5