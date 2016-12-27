'''
Created on 24 Dec 2016

@author: dusted-ipro
'''

import numpy as np
import environment.world as world
from environment.sensing import closestStar, dist

class baseAgent(object):
    '''
    Base Agent Class
    '''

    def __init__(self, agentType, agentId, coords, clanId):
        '''
        Base Constructor
        '''
        self.agentType = agentType
        self.agentId = agentId
        #Visubility in AU
        self.visibilityRange = world.agentBaseVis
        self.clanId = clanId
        self.position = np.array(coords)
        self.velocity = np.array([0.0,0.0,0.0])
        self.acceleration = np.array([0.0,0.0,0.0])
        self.destination = None
        #Index of current closest star (Which system we are in)
        self.currStarIdx = closestStar(coords)[0]
        self.origin = coords
        self.activity = 0
        self.age = 0.0
        #Age required for reproduction
        self.minAgeReprod = 100.0
        self.maxAgeReprod = 1000.0
        #Chance of reproduction
        self.reprodChance = world.agentReprodChance
        #Range we have to be from a star to jump
        self.starJumpDist = 0.0000001
        #Resource Coord Store {starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, ...}
        self.resourceKnowledge = {}


    def starJump(self, targetStarIdx):
        '''
        Jump an agent between star systems
        '''
        self.currStarIdx = targetStarIdx
        #Move so we arn't in the middle of the star
        self.position = world.stars[targetStarIdx].position
        self.position[0]+=(world.stars[targetStarIdx].radius*2.0)


    def systemMove(self, maxVelMag):
        '''
        Move within a system toward a target
        If dist diff is less than a step at max velocity then just snap to the tgt for now
        '''
        if dist(self.destination, self.position) < maxVelMag*world.timeStep:
            self.position = self.destination
            return
        #Set velocity vector
        diff = self.destination-self.position
        self.velocity = np.power(((diff)/(np.linalg.norm(diff))), 2.0)*maxVelMag
        #Change this!!
        if diff[0]<0.0:
            self.velocity[0]*=-1.0
        if diff[1]<0.0:
            self.velocity[1]*=-1.0
        if diff[2]<0.0:
            self.velocity[2]*=-1.0
        #Move a step
        self.position+=self.velocity*world.timeStep


    def stop(self):
        '''
        Stop Moving
        '''
        self.velocity = np.array([0.0,0.0,0.0])


    def storeResourceKnowledge(self, energyStore, rawMatStore, starIdx, planetIdx):
        '''
        Store knowledge in our resource store
        '''
        #{starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, ...}
        if starIdx in self.resourceKnowledge.keys():
            #Already stored something about this system
            self.resourceKnowledge[starIdx][planetIdx] = {'rawMat':rawMatStore, 'energy':energyStore}
        else:
            self.resourceKnowledge[starIdx] = {planetIdx:{'rawMat':rawMatStore, 'energy':energyStore}}








