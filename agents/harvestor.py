'''
Created on 25 Dec 2016

@author: dusted-ipro
'''

import numpy as np

from environment import world
from environment.sensing import dist
from agents.base import baseAgent
from data.tradableTypes import allTradables
from data.actionTypes import allActions


class harvestor(baseAgent):
    '''
    Harvestor Agent
    '''

    def __init__(self, agentType, agentId, coords, clan,
                 energyCap, rawMatCap, hgCap, energyHRate, rawMatHRate, hgConsumeRate, energyConsumeRate):
        '''
        Harvestors collect both energy and rawMats at the same time (for now)
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clan)
        self.store = {0:{'store':100.0, 'capacity':hgCap},
                      7:{'store':0.0, 'capacity':energyCap},
                      8:{'store':0.0, 'capacity':rawMatCap}}

        self.consumes = {0:{'consumeRate':hgConsumeRate}}
        #Max Speed in System - LY / Sec
        self.maxVelMag = world.genAgentMaxVelMag()
        ###############
        #Harvestor Specifics
        self.energyHRate = energyHRate
        self.rawMatHRate = rawMatHRate
        #LY
        self.collectDist = 1.0
        #Tons per sec
        self.collectRate = 1.0

        #All Available to this agent
        self.actionsAll = {0:{'func':self.idle, 'args':[], 'activity':0,
                              'expiry':0.0, 'status':None,
                              'blocking':False, 'default':False},
                           2:{'func':self.harvestResources, 'args':[], 'activity':0,
                              'expiry':0.0, 'status':None,
                              'blocking':False, 'default':True}
                           }
        #Actions offered as services to others
        self.actionsOffered = [3]
        #Current Action (id matches actionTypes lookup)
        #Default on init
        for k in self.actionsAll.keys():
            if self.actionsAll[k]['default'] == True:
                self.action = k

    def harvestResources(self, args):
        '''
        Collect basic resources - Energy, Raw Materials
        Default Action
        args = []
        '''
        #Move - catch for idle restart
        if self.actionsAll[self.action]['activity'] == 1 or self.actionsAll[self.action]['activity'] == 0:
            #Do we have a target?
            if self.destination == None:
                try:
                    #Get the next in Q - its already sorted by distance
                    nextResource = world.clans[self.clanId].harvestorQ.popleft()
                except IndexError:
                    #Set Idle - Wait in system until clan put more jobs into the Q
                    self.stop()
                    self.actionsAll[self.action]['activity'] = 0
                    return
                #Set Dest - its not in the system we are in so this is the jump out star
                self.actionsAll[self.action]['activity'] = 1
                self.destination = world.starCoords[self.currStarIdx]
                self.targetPlanet = nextResource[1]
                self.targetStar = nextResource[0]
                return
            #Are we in the target System?
            if self.currStarIdx == self.targetStar:
                #Are we close enough to collect?
                if dist(self.position, self.destination) < self.visibilityRange:
                    #Stop
                    self.stop()
                    #Swap harvest
                    self.actionsAll[self.action]['activity'] = 2
                    return
                else:
                    #Move closer to target planet
                    self.systemMove(self.maxVelMag)
                    return
            #Are we close enough to current star to jump?
            if dist(self.position, self.destination) < self.starJumpDist:
                #Jump & swap dest to target planet
                self.starJump(self.targetStar)
                self.destination = world.stars[self.targetStar].planets[self.targetPlanet].position
                return
            #No - Move closer to jump star
            else:
                self.systemMove(self.maxVelMag)
                return
        #Harvesting
        elif self.actionsAll[self.action]['activity'] == 2:
            #Does the planet have any resources left?
            if world.stars[self.currStarIdx].planets[self.targetPlanet].checkDepleted() == True:
                #Set move home
                self.actionsAll[self.action]['activity'] = 4
                self.destination = world.starCoords[self.currStarIdx]
                self.targetStar = None
                self.targetPlanet = None
                return
            #Do we have the stuff required to do our job?
            if self.consumeCheck()[0] == False:
                #Swap to waiting service and type
                self.actionsAll[self.action]['activity'] = 3
                #self.serviceTypeRequired = XXX
                return
            #Harvest - check capacities
            if self.store[7]['store'] <= self.store[7]['capacity']:
                self.transmitTradable(world.stars[self.currStarIdx].planets[self.targetPlanet],
                                      self, 7, self.energyHRate)
                #Consume - while harvesting
                self.consumeTick()
            if self.store[8]['store'] <= self.store[8]['capacity']:
                self.transmitTradable(world.stars[self.currStarIdx].planets[self.targetPlanet],
                                      self, 8, self.rawMatHRate)
                #Consume - while harvesting
                self.consumeTick()
            if self.store[8]['store'] >= self.store[8]['capacity'] and self.store[7]['store'] >= self.store[7]['capacity']:
                #Both at capacity - swap to waiting collection service
                #NEXT: Figure out service demand and supply!
                #It must include:
                #    - Communication about requirements (for tradable and service strength)
                #    - Strength increase, decrease and queuing
                #    - Services like pickup, dropoff, military assistance, medical help, etc...
                self.actionsAll[self.action]['activity'] = 3
            return
        #Waiting Service
        elif self.actionsAll[self.action]['activity'] == 3:
            #Have we been serviced?
            if self.store[7]['store'] > 0.0:
                #TODO: Reset demand
                pass
            if self.store[8]['store'] > 0.0:
                #TODO: Reset demand
                pass
            #Check again if we have everything needed to continue
            if self.consumeCheck()[0] == False:
                #Swap back to harvesting
                self.actionsAll[self.action]['activity'] = 2
                return
            else:
                #If we've waited long enough - then do something ourselves
                if self.serviceWait > self.maxServiceWait:
                    self.actionsAll[self.action]['activity'] = 4
                    #Set Dest
                    if self.currStarIdx == world.clans[self.clanId].originStarIdx:
                        #Already home sys
                        self.destination = world.clans[self.clanId].originCoords
                    else:
                        self.destination = world.starCoords[self.currStarIdx]
                    self.targetPlanet = None
                    self.targetStar = world.clans[self.clanId].originStarIdx
                    self.serviceWait = 0
                    return
                self.serviceWait+=1
                #Wait for a pickup - increase demand strength
                #NEXT: Figure out service demand and supply!
            return
        #Moving Home
        elif self.actionsAll[self.action]['activity'] == 4:
            #Are we in clan home system?
            if self.currStarIdx == self.targetStar:
                #Are we close enough to clan home planet to stop and dump resources?
                if dist(self.position, self.destination) < self.visibilityRange:
                    #Push all Resources to clan main store
                    self.transmitAllTradables(self, world.clans[self.clanId])
                    #Swap to moveStarSys (new harvesting Job)
                    self.actionsAll[self.action]['activity'] = 0
                    self.destination = None
                    self.targetPlanet = None
                    self.targetStar = None
                    return
                else:
                    #Move closer to target planet
                    self.systemMove(self.maxVelMag)
                    return
            #Are we close enough to outer star to jump home?
            elif dist(self.position, self.destination) < self.starJumpDist:
                #Jump
                self.starJump(self.targetStar)
                #Swap destination to clan home planet (now we are in correct system)
                self.destination = world.stars[world.clans[self.clanId].originStarIdx].planets[world.clans[self.clanId].originPlanetIdx].position
                return
            else:
                #Move closer to star
                self.systemMove(self.maxVelMag)
                return
        else:
            return









