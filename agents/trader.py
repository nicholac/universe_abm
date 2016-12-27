'''
Created on 24 Dec 2016

@author: dusted-ipro
'''

from agents.base import baseAgent
from data.tradableTypes import allTradables
import numpy as np

class trader(baseAgent):
    '''
    Trader / Transporter Agent
    '''

    def __init__(self, agentType, agentId, coords, clan):
        '''
        Constructor
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clan)
        self.demands = {'id':1, 'strength':1.0, 'store':0.0, 'name':allTradables()[1]}
        #Doesnt supply - trades / transports
        #self.supplies = {'id':None, 'strength':0.0, 'store':0.0}
        self.consumes = [{'id':1, 'rate':1.0, 'store':0.0}]
        self.energy = {'amount':0.0, 'usageRate':1.0}
        #LY / Sec
        self.maxSpeed = 3.0
        self.maxCapacity = 10.0
        #Changes on the fly
        self.tradingGoodId = 0
        self.tradingGoodName = allTradables()[self.tradingGoodId]
