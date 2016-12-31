'''
Created on 24 Dec 2016

@author: dusted-ipro
'''
import numpy as np

from environment import world
from environment.sensing import closestStar, dist
from agents.base import baseAgent
from data.tradableTypes import allTradables
from data.contractTypes import allContracts


class explorer(baseAgent):
    '''
    Explorer Agent
      - Gets a star the clan has no-knowledge of (closest without knowledge)
      - Moves to Star
      - Visits planets in solar system
      - Checks for energy or raw mat - records for each planet
      - Returns to clan origin and
      - Deposits knowledge
    '''

    def __init__(self, agentType, agentId, coords, clanId, resourceType):
        '''
        resourceType is either energy coords or raw mat coords - coords are tradable
        '''
        baseAgent.__init__(self, agentType, agentId, coords, clanId)
        #Explorer searches for an supplies coordinates of resourceType
        self.store = {resourceType:{'store':0.0, 'capacity':1000000.0},
                      7:{'store':0.0, 'capacity':1000000.0}}
        #Max Speed in System - LY / Sec
        self.maxVelMag = world.genAgentMaxVelMag()
        self.consumes = {7:{'consumeRate':1.0}}

        ###############
        #Explorer Specifics
        #What we are doing now - [moveStar, visitPlanets, checkResources, returnClan, depositKnowledge]
        #In future we might be able to encode these as dict-embedded functions (then call them with an index?)
        self.activityLookup = {0:'idle', 1:'moveStarSys', 2:'visitPlanets', 3:'checkResources',
                             4:'returnClan', 5:'depositKnowledge', 6:'avoidingCriminal', 7:'avoidingMilitary'}
        #Contract Types Offered by this agent
        #{contractType:self.function, ...}
        self.contractTypes = {}


    def actions(self):
        '''
        Conduct the Agents Actions
        '''
        #Criminal Avoidance
        if self.detectCriminal():
            #Swap to avoiding Criminal
            self.activity = 6
            return
        #Military Avoidance
        if self.detectMilitary():
            #Swap to avoiding military
            self.activity = 7
            return
        if self.activity == 1 or self.activity == 0:
            #Are we in the target system?
            if self.currStarIdx == self.targetStar:
                self.activity = 2
                self.targetPlanet = 0
                self.destination = world.stars[self.currStarIdx].planets[0].position
                return
            #Do we have a target star system yet?
            if self.destination == None:
                #Get clan next unknown from Q
                #closestStarUk = world.clans[self.clanId].closestUnknownStar(self.position)
                try:
                    nextStar = world.clans[self.clanId].explorerQ.popleft()
                    self.activity = 1
                except IndexError:
                    #Set Idle - Wait in system until clan put more jobs into the Q
                    self.activity = 0
                    return
                #Set Dest - its not in the system we are i so this is the jump out star
                self.destination = world.starCoords[self.currStarIdx]
                self.targetStar = nextStar[0]
                return
            #Are we close enough to current star to jump?
            if dist(self.position, self.destination) < self.starJumpDist:
                #Jump & swap to visit planets
                self.starJump(self.targetStar)
                self.activity = 2
                self.targetPlanet = 0
                self.destination = world.stars[self.currStarIdx].planets[0].position
            #Move closer to jump star
            else:
                self.systemMove(self.maxVelMag)
        elif self.activity == 2:
            #Are we close enough to scan?
            if dist(self.position, self.destination) < self.visibilityRange:
                #Stop
                self.stop()
                self.activity = 3
                return
            else:
                #Move closer to target planet
                self.systemMove(self.maxVelMag)
                return
        elif self.activity == 3:
            #Store the resources of the closest planet
            self.storeResourceKnowledge(world.stars[self.currStarIdx].planets[self.targetPlanet].store,
                                        self.currStarIdx,
                                        self.targetPlanet)
            #Have we done all planets?
            if len(self.resourceKnowledge[self.targetStar].keys()) == len(world.stars[self.currStarIdx].planets):
                #Yes - swap to return home
                self.activity = 4
                #Destination is initially local star (for jump)
                self.destination = world.starCoords[self.currStarIdx]
                self.targetPlanet = world.clans[self.clanId].originPlanetIdx
                self.targetStar = world.clans[self.clanId].originStarIdx
            else:
                #No - Swap target planet
                self.targetPlanet+=1
                self.activity = 2
                self.destination = world.stars[self.currStarIdx].planets[self.targetPlanet].position
            return
        elif self.activity == 4:
            #Are we in clan home system?
            if self.currStarIdx == self.targetStar:
                #Are we close enough to clan home planet to dump knowledge?
                if dist(self.position, self.destination) < self.visibilityRange:
                    #Push knowledge to clan
                    self.activity = 5
                    world.clans[self.clanId].rxResourceKnowledge(self.resourceKnowledge)
                    #Clear own knowledge
                    self.resourceKnowledge = {}
                    #Swap to moveStar
                    self.activity = 1
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
        #Avoiding Crim
        elif self.activity == 6:
            pass
        #Avoiding Mil
        elif self.activity == 7:
            pass
        return








