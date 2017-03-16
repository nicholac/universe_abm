'''
Created on 24 Dec 2016

@author: dusted-ipro
'''
import numpy as np

#from environment import world
#NEXT: WORK THROUGH THE ACTUAL TRADER ACTION LOGIC
from agents.base import baseAgent
from data.tradableTypes import allTradables
from data.actionTypes import allActions

class trader(baseAgent):
    '''
    Trader / Transporter Agent
    '''

    def __init__(self, agentType, agentId, coords, clan, tgConsumeRate):
        '''
        Constructor
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clan)
        #Basically infinite stores for now
        self.store = {0:{'store':0.0, 'capacity':100000.0},
                      1:{'store':100.0, 'capacity':100000.0},
                      2:{'store':0.0, 'capacity':100000.0},
                      3:{'store':0.0, 'capacity':100000.0},
                      4:{'store':0.0, 'capacity':100000.0},
                      5:{'store':0.0, 'capacity':100000.0},
                      6:{'store':0.0, 'capacity':100000.0},
                      7:{'store':0.0, 'capacity':100000.0},
                      8:{'store':0.0, 'capacity':100000.0},
                      9:{'store':0.0, 'capacity':100000.0},
                      10:{'store':0.0, 'capacity':100000.0}}

        self.consumes = {1:{'consumeRate':tgConsumeRate}}
        #Max Speed in System - LY / Sec
        self.maxVelMag = world.genAgentMaxVelMag()


        #All Available to this agent
        self.actionsAll = {0:{'func':self.idle, 'args':[], 'activity':0,
                              'expiry':0.0, 'status':None,
                              'blocking':False, 'default':True},
                           3:{'func':self.transport, 'args':[], 'activity':0,
                              'expiry':0.0, 'status':None,
                              'blocking':False, 'default':False}
                           }
        #Actions offered as services to others
        self.actionsOffered = [3]
        #Contracts are actions that have been demanded as being required
        self.activeContracts = {}
        #Current Action (id matches actionTypes lookup)
        #Default on init
        for k in self.actionsAll.keys():
            if self.actionsAll[k]['default'] == True:
                self.action = k


    def transport(self, args):
        '''
        Move stuff from X to Y
        ::param args [fromCls, toCls]
        '''
        pass










