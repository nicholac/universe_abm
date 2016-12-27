'''
Created on 24 Dec 2016

@author: dusted-ipro
'''
import numpy as np

from environment import world
from environment.sensing import closestStar, dist
from agents.base import baseAgent
from data.tradableTypes import allTradables


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
        self.demands = {'id':6, 'strength':1.0, 'store':0.0, 'name':allTradables()[6]}
        #Explorer searches for an supplies coordinates of resourceType
        self.supplies = {'id':resourceType, 'strength':0.0, 'store':[], 'name':allTradables()[resourceType]}
        self.consumes = [{'id':6, 'rate':1.0, 'store':0.0}]
        self.energy = {'amount':0.0, 'usageRate':1.0}
        #Max Speed in System - LY / Sec
        self.maxVelMag = world.genAgentMaxVelMag()
        #What we are doing now - [moveStar, visitPlanets, checkResources, returnClan, depositKnowledge]
        #In future we might be able to encode these as dict-embedded functions (then call them with an index?)
        self.activityLookup = {0:'moveStarSys', 1:'visitPlanets', 2:'checkResources',
                             3:'returnClan', 4:'depositKnowledge'}
        #Current targets
        self.targetStar = None
        self.targetPlanet = None


    def actions(self):
        '''
        Conduct the Agents Actions
        '''
        if self.activity == 0:
            #Are we in the target system?
            if self.currStarIdx == self.targetStar:
                self.activity = 1
                self.targetPlanet = 0
                self.destination = world.stars[self.currStarIdx].planets[0].position
                return
            #Do we have a target star system yet?
            if self.destination == None:
                print '{}'.format('Getting next Job')
                #Get clan next closest unknown
                closestStarUk = world.clans[self.clanId].closestUnknownStar(self.position)
                #Set Dest - its not in the system we are i so this is the jump out star
                self.destination = world.starCoords[self.currStarIdx]
                self.targetStar = closestStarUk[0]
                return
            #Are we close enough to current star to jump?
            if dist(self.position, self.destination) < self.starJumpDist:
                #Jump & swap to visit planets
                self.starJump(self.targetStar)
                self.activity = 1
                self.targetPlanet = 0
                self.destination = world.stars[self.currStarIdx].planets[0].position
            #Move closer to jump star
            else:
                self.systemMove(self.maxVelMag)
        elif self.activity == 1:
            #Are we close enough to scan?
            if dist(self.position, self.destination) < self.visibilityRange:
                #Stop
                self.stop()
                self.activity = 2
                return
            else:
                #Move closer to target planet
                self.systemMove(self.maxVelMag)
                return
        elif self.activity == 2:
            #Store the resources of the closest planet
            self.storeResourceKnowledge(world.stars[self.currStarIdx].planets[self.targetPlanet].energyStore,
                                        world.stars[self.currStarIdx].planets[self.targetPlanet].rawMatStore,
                                        self.currStarIdx,
                                        self.targetPlanet)
            #Have we done all planets?
            if len(self.resourceKnowledge[self.targetStar].keys()) == len(world.stars[self.currStarIdx].planets):
                #Yes - swap to return home
                self.activity = 3
                #Destination is initially local star (for jump)
                self.destination = world.starCoords[self.currStarIdx]
                self.targetPlanet = world.clans[self.clanId].originPlanetIdx
                self.targetStar = world.clans[self.clanId].originStarIdx
            else:
                #No - Swap target planet
                self.targetPlanet+=1
                self.activity = 1
                self.destination = world.stars[self.currStarIdx].planets[self.targetPlanet].position
            return
        elif self.activity == 3:
            #Are we in clan home system?
            if self.currStarIdx == self.targetStar:
                #Are we close enough to clan home planet to dump knowledge?
                if dist(self.position, self.destination) < self.visibilityRange:
                    #Push knowledge to clan
                    world.clans[self.clanId].rxResourceKnowledge(self.resourceKnowledge)
                    #Clear own knowledge
                    self.resourceKnowledge = {}
                    #Swap to moveStar
                    self.activity = 0
                    self.destination = None
                    self.targetPlanet = None
                    self.targetStar = None
                    print '{}'.format('Arrived home, dumped knowledge')
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
        #Check for our resource type in range








