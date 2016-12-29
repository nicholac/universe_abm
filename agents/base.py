'''
Created on 24 Dec 2016

@author: dusted-ipro
'''

import numpy as np
import environment.world as world
from environment.sensing import closestStar, dist
from data.agentTypes import allAgents

class baseAgent(object):
    '''
    Base Agent Class
    '''

    def __init__(self, agentType, agentId, coords, clanId):
        '''
        Base Constructor
        '''
        self.agentType = agentType
        self.agentName = allAgents()[self.agentType]
        #This is unique globally
        self.agentId = agentId
        #Visibility in LY
        self.visibilityRange = world.agentBaseVis
        self.clanId = clanId
        self.position = np.array(coords)
        self.velocity = np.array([0.0,0.0,0.0])
        self.acceleration = np.array([0.0,0.0,0.0])
        self.destination = None
        #Index of current closest star (Which system we are in)
        self.currStarIdx = closestStar(coords)[0]
        #Adfd ourselves to the celestials list
        self.addAgentSys(self.currStarIdx)
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
        #Ticks the agent waits for services before deciding to do something itself
        self.serviceWait = 0
        self.maxServiceWait = 100


    def initSocialNet(self, links):
        '''
        When creating a new agent initialise the agents social network
            - Family links
            - Clan links(2,3,{'weight':8})
        ::param links - array of links we can use with networkX, e.g. [(clanUID, AgentUID, {'clan':0.1}),
                                                                        (AgentUID, AgentUID, {'social':0.1})
                                                                        (AgentUID, AgentUID, {'family':0.1})]
        '''
        world.socialNet.add_edges_from(links)


    def starJump(self, targetStarIdx):
        '''
        Jump an agent between star systems
        '''
        #Remove ourselves form the origin system agent list
        self.rmAgentSys(self.currStarIdx)
        self.currStarIdx = targetStarIdx
        #Move so we arn't in the middle of the star
        self.position = world.stars[targetStarIdx].position
        self.position[0]+=(world.stars[targetStarIdx].radius*2.0)
        #Record in the system store that we are here
        self.addAgentSys(self.currStarIdx)


    def addAgentSys(self, starIdx):
        '''
        Add agent from the systems list of agents
        '''
        world.stars[starIdx].agentsInSys.append(self.agentId)


    def rmAgentSys(self, starIdx):
        '''
        Remove agent from the systems list of agents
        '''
        world.stars[starIdx].agentsInSys.pop(world.stars[starIdx].agentsInSys.index(self.agentId))


    def systemMove(self, maxVelMag):
        '''
        Move within a system toward a target
        If dist diff is less than a step at max velocity then just snap to the tgt for now
        '''
        d = dist(self.destination, self.position)
        if d < maxVelMag*world.timeStep:
            self.position = self.destination
            return
        #Set velocity vector
        diff = self.destination-self.position
        self.velocity = (diff/d)*self.maxVelMag
#         #Change this!!
#         if diff[0]<0.0:
#             self.velocity[0]*=-1.0
#         if diff[1]<0.0:
#             self.velocity[1]*=-1.0
#         if diff[2]<0.0:
#             self.velocity[2]*=-1.0
        #Move a step
        self.position+=(self.velocity*world.timeStep)


    def moveHome(self):
        '''
        Move toward clan origin planet.
        Set destination null when arrived
        '''
        pass


    def stop(self):
        '''
        Stop Moving
        '''
        self.velocity = np.array([0.0,0.0,0.0])


    def storeResourceKnowledge(self, store, starIdx, planetIdx):
        '''
        Store knowledge in our resource store
        {7:{'store':0.0}, 8:{'store':0.0}}
        '''
        #{starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, ...}
        if starIdx in self.resourceKnowledge.keys():
            #Already stored something about this system
            self.resourceKnowledge[starIdx][planetIdx] = store
        else:
            self.resourceKnowledge[starIdx] = {planetIdx:store}

    def detectCriminal(self):
        '''
        Detect a criminal
        '''
        return False

    def detectMilitary(self):
        '''
        Detect military
        '''
        return False


    def transmitTradable(self, fromCls, toCls, tradableType, amount):
        '''
        Standardised interface for transmitting tradables between classes (e.g. ag<->ag, planet->ag, star->ag)
        If the receiving class has no capacity then its an infinite sink

        0 = out
        1 = in
        '''
        #try:
        #Check for wrong capacity choice - like there isnt enough to send
        if fromCls.store[tradableType]['store'] <= amount:
            amount = fromCls.store[tradableType]['store']
        #Check if the receiver has a max capacity flag
        if toCls.store[tradableType].has_key('capacity'):
            if toCls.store[tradableType]['store']+amount >= toCls.store[tradableType]['capacity']:
                amount = toCls.store[tradableType]['capacity'] - toCls.store[tradableType]['store']
                #Just fill it up
                toCls.store[tradableType]['store'] = toCls.store[tradableType]['capacity']
                fromCls.store[tradableType]['store'] -= amount
                return
            else:
                #Straight exchange
                toCls.store[tradableType]['store'] += amount
                fromCls.store[tradableType]['store'] -= amount
                return
        else:
            #Infinite sink - transfer it all
            toCls.store[tradableType]['store'] += amount
            fromCls.store[tradableType]['store'] -= amount
            return
        #except KeyError:
            #Tradable doesnt exist between parties
        #    print 'Tx error - tradables Incompatible: from: {}, to: {}'.format(fromCls, toCls)
        return


    def transmitAllTradables(self, fromCls, toCls):
        '''
        Transmit all the tradables in the fromStore, to the toStore (just calls the above iteratively)
        '''
        for k in fromCls.store.keys():
            self.transmitTradable(fromCls, toCls, k, fromCls.store[k]['store'])


    def consumeTick(self):
        '''
        Generic consumation of consumables for a tick
        '''
        for k in self.consumes.keys():
            self.store[k]['store']-=self.consumes[k]['consumeRate']
            if self.store[k]['store'] < 0.0:
                self.store[k]['store'] = 0.0


    def consumeCheck(self):
        '''
        Check if we have enough of the stuff we consume to do our job
        '''
        #Do we have the stuff required to do our job?
        for k in self.consumes.keys():
            if self.store[k] <= 0.0:
                return (False, k)
        return (True, 0)


    def chat(self):
        '''
        Basic social network formation & degredation function
        If there are other agents in range:
            - of the same clan then form a link - or strengthen it
            - of a different clan then degrade the individuals link (and potentially the overall clans)
        '''
        #Just search the agents in the system to make this faster
        for aIdx in world.stars[self.currStarIdx].agentsInSys:
            if np.linalg.norm(self.position-world.agents[aIdx].position) < self.visibilityRange:
                #Own Clan
                if aIdx in world.clans[self.clanId].agents:
                    #Strengthen or create - by probability (higher chance of good)
                    pass
                #Other clan
                else:
                    #Degrade or create - by probability (higher chance of bad)
                    pass






