'''
Created on 25 Dec 2016

@author: dusted-ipro
'''

import numpy as np

from environment import world
from environment.sensing import dist
from agents.base import baseAgent
from data.tradableTypes import allTradables
from data.interactionTypes import allInteractions


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

        #self.demands = {0:{'store':0.0, 'capacity':energyCap, 'strength':0.0}}
        self.energyHRate = energyHRate
        self.rawMatHRate = rawMatHRate
        self.consumes = {0:{'consumeRate':hgConsumeRate}}
        #Service Types Offered by this agent
        #{serviceType:{}}
        self.serviceTypes = {}
        #AU
        self.collectDist = 1.0
        #Tons per sec
        self.collectRate = 1.0
        #Max Speed in System - LY / Sec
        self.maxVelMag = world.genAgentMaxVelMag()
        #Activities
        self.activityLookup = {0:'idle', 1:'moveStarSys', 2:'harvesting', 3:'waitingService',
                               4:'returnHome', 5:'avoidingCriminal', 6:'avoidingMilitary'}
        #Current targets
        self.targetStar = None
        self.targetPlanet = None


    def actions(self):
        '''
        Conduct the Agents Actions
        '''
        #Social net
        self.chat()
        #Criminal Avoidance
        if self.detectCriminal():
            #Swap to avoiding Criminal
            self.activity = 5
            return
        #Military Avoidance
        if self.detectMilitary():
            #Swap to avoiding military
            self.activity = 6
            return
        #Move - catch for idle restart
        if self.activity == 1 or self.activity == 0:
            #Do we have a target?
            if self.destination == None:
                try:
                    #Get the next in Q - its already sorted by distance
                    nextResource = world.clans[self.clanId].harvestorQ.popleft()
                except IndexError:
                    #Set Idle - Wait in system until clan put more jobs into the Q
                    self.stop()
                    self.activity = 0
                    return
                #Set Dest - its not in the system we are in so this is the jump out star
                self.activity = 1
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
                    self.activity = 2
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
        elif self.activity == 2:
            #Does the planet have any resources left?
            if world.stars[self.currStarIdx].planets[self.targetPlanet].checkDepleted() == True:
                #Set move home
                self.activity = 4
                self.destination = world.starCoords[self.currStarIdx]
                self.targetStar = None
                self.targetPlanet = None
                return
            #Do we have the stuff required to do our job?
            if self.consumeCheck()[0] == False:
                #Swap to waiting service and type
                self.activity = 3
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
                self.activity = 3
            return
        #Waiting Service
        elif self.activity == 3:
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
                self.activity = 2
                return
            else:
                #If we've waited long enough - then do something ourselves
                if self.serviceWait > self.maxServiceWait:
                    self.activity = 4
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
        elif self.activity == 4:
            #Are we in clan home system?
            if self.currStarIdx == self.targetStar:
                #Are we close enough to clan home planet to stop and dump resources?
                if dist(self.position, self.destination) < self.visibilityRange:
                    #Push all Resources to clan main store
                    self.transmitAllTradables(self, world.clans[self.clanId])
                    #Swap to moveStarSys (new harvesting Job)
                    self.activity = 0
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
        #Avoiding Criminal
        elif self.activity == 5:
            #Is criminal in range?
                #Check criminal position
                #Move away at max speed
            #Swap to moving
            pass
        #Avoiding Military
        elif self.activity == 6:
            #Is military in range?
                #Check military position
                #Move away at max speed
            #Swap to moving
            pass
        else:
            return









