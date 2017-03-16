'''
Created on 24 Dec 2016

@author: dusted-ipro
'''

import numpy as np

#import environment.world as world
#NEXT: WORK THROUGH REMOVING WORLD FUNCS - FOR DISTRIBUTION
from environment.sensing import closestStar, dist
from data.agentTypes import allAgents
from data.socialLinkTypes import allLinks

class baseAgent(object):
    '''
    Base Agent Class
    '''

    def __init__(self, agentType, agentId, coords, clanId,
                 visRange, reprodChance, timeStep, socialLinkAgeRate, maxVelMag):
        '''
        Base Constructor
        '''
        self.agentType = agentType
        self.agentName = allAgents()[self.agentType]
        #This is unique globally
        self.agentId = agentId
        #Visibility in LY
        self.visibilityRange = visRange
        self.clanId = clanId
        self.position = np.array(coords)
        self.velocity = np.array([0.0,0.0,0.0])
        #Max Speed in System - LY / Sec
        self.maxVelMag = maxVelMag
        self.acceleration = np.array([0.0,0.0,0.0])
        self.timeStep = timeStep
        self.destination = None
        #Index of current closest star (Which system we are in)
        self.currStarIdx = closestStar(coords)[0]
        #Adfd ourselves to the celestials list
        self.addAgentSys(self.currStarIdx)
        self.origin = coords
        self.activity = 0
        #Age in secs
        self.age = 0.0
        #Age Rate (multiplier for faster aging per tick)
        self.agentAgeRate = 1.0
        #Age required for reproduction (secs)
        self.minAgeReprod = 100.0
        self.maxAgeReprod = 1000.0
        #Chance of reproduction
        self.reprodChance = reprodChance
        #Range we have to be from a star to jump
        self.starJumpDist = 0.0000001
        #Current targets
        self.targetStar = None
        self.targetPlanet = None
        #Resource Coord Store {starIdx:{planetIdx:{'rawMat':X, 'energy':Y}}, ...}
        self.resourceKnowledge = {}
        #Ticks the agent waits for services (contracts) before deciding to do something itself
        self.serviceWait = 0
        self.maxServiceWait = 100
        #Agents social Network
        #{AgentUID:{type:weight, ...}}
        self.socialNet = {}
        self.socialLinkAgeRate = socialLinkAgeRate
        self.socialLinkMaxStren = 100.0
        self.socialLinkMinStren = -100.0
        self.chatLinkMinStrength = -5.0
        self.chatLinkMaxStrength = 5.0


    def actions(self):
        '''
        Conduct the Agents Actions
        '''
        #Entropy
        self.entropy()
        #Check for contracts amongst social net contacts

        #Do action
        self.actionsAll[self.action]['func'](self.actionsAll[self.action]['args'])


    def idle(self, args):
        '''
        Idle Actions
        args = []
        '''
        pass

    #DEPRECATED to Dict#####
    #def addSocialLink(self, agent1Id, agent2Id, _type, weight):
    #    '''
    #    Add a link to this agent, of type and weight
    #    nodeId can be agentId, clanId
    #    '''
    #    self.socialNet.add_edge(agent1Id, agent2Id, {_type:weight})
    ########################

    def addSocialLink(self, otherAgentId, _type, weight):
        '''
        Add a local social net Node
        '''
        if self.socialNet.has_key(otherAgentId):
            if self.socialNet[otherAgentId].has_key(_type):
                #Already exists
                return
            else:
                #Add the new type
                self.socialNet[otherAgentId][_type]=weight
        else:
            self.socialNet[otherAgentId]={_type:weight}


    def starJump(self, targetStarIdx):
        '''
        Jump an agent between star systems
        - Just changes agent internal data - they agent is moved by world when it returns to the server
        '''
        #Remove ourselves form the origin system agent list
        #self.rmAgentSys(self.currStarIdx)
        self.currStarIdx = targetStarIdx
        #Move so we arn't in the middle of the star
        #self.position = world.stars[targetStarIdx].position
        #self.position[0]+=(world.stars[targetStarIdx].radius*2.0)
        #Record in the system store that we are here
        #self.addAgentSys(self.currStarIdx)

    ###############################
    #DEPRECATED - Dont on resync at Server
    #def addAgentSys(self, starIdx):
    #    '''
    #    Add agent from the systems list of agents
    #    '''
    #    world.stars[starIdx].agentsInSys.append(self.agentId)
    #
    #
    #def rmAgentSys(self, starIdx):
    #    '''
    #    Remove agent from the systems list of agents
    #    '''
    #    world.stars[starIdx].agentsInSys.pop(world.stars[starIdx].agentsInSys.index(self.agentId))
    ################################


    def systemMove(self, maxVelMag):
        '''
        Move within a system toward a target
        If dist diff is less than a step at max velocity then just snap to the tgt for now
        '''
        d = dist(self.destination, self.position)
        if d < maxVelMag*self.timeStep:
            self.position = self.destination
            return
        #Set velocity vector
        diff = self.destination-self.position
        self.velocity = (diff/d)*self.maxVelMag
        #Move a step
        self.position+=(self.velocity*self.timeStep)


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


    def chat(self, otherAgentId, otherAgentClanId):
        '''
        Basic social network formation & degredation function
        For the interacting agents
            - of the same clan then form a link - or strengthen it
            - of a different clan then degrade the individuals link (and potentially the overall clans)
        Caveats:
            - When links are created they are even between agents (They both know each other equally well)
            - Links are non-directed (single even link between agents)
        TODO: Reengineer potentially to have agents knowing each other different amounts
            - What knock on effects for service provision?
        '''
        #Firstly some chance of even interacting
        if np.random.choice([True, False]) == True:
            if otherAgentId == self.agentId:
                #Dont interact with self
                return
            #if np.linalg.norm(self.position-world.agents[aId].position) < self.visibilityRange:
            #Own Clan
            if otherAgentClanId == self.clanId:
                #Strengthen or create - by probability (higher chance of good)
                #print 'Stronger: {}, {}'.format(self.agentId, aId)
                stren = np.random.choice(np.linspace(self.chatLinkMinStrength,
                                                     self.chatLinkMaxStrength, 20),
                                                    p=self.positiveProbsPow(20))
                try:
                    #Check if it exists
                    if not self.socialNet.has_key(otherAgentId):
                        #Add the new link to the social net
                        self.socialNet[otherAgentId] = {'social':stren}
                    else:
                        #Change existing - check for boundary
                        if self.socialNet[otherAgentId]['social']+stren > self.socialLinkMaxStren:
                            self.socialNet[otherAgentId]['social'] = self.socialLinkMaxStren
                        elif self.socialNet[otherAgentId]['social']+stren < self.socialLinkMinStren:
                            self.socialNet[otherAgentId]['social'] = self.socialLinkMinStren
                        else:
                            self.socialNet[otherAgentId]['social']+=stren
                except Exception, err:
                    print 'Failed to create social link: {}, {}, {}'.format(self.agentId, otherAgentId, err)
            #Other clan
            else:
                try:
                    #Degrade or create - by probability (higher chance of bad)
                    #print 'Weaker: {}, {}'.format(self.agentId, aId)
                    stren = np.random.choice(np.linspace(self.chatLinkMinStrength,
                                                         self.chatLinkMaxStrength, 20),
                                                        p=self.negativeProbsPow(20))
                    #Check if it exists
                    if not self.socialNet.has_key(otherAgentId):
                        #Add the new link to the social net
                        self.socialNet[otherAgentId] = {'social':stren}
                    else:
                        #Change existing - check for boundary
                        if self.socialNet[otherAgentId]['social']+stren > self.socialLinkMaxStren:
                            self.socialNet[otherAgentId]['social'] = self.socialLinkMaxStren
                        elif self.socialNet[otherAgentId]['social']+stren < self.socialLinkMinStren:
                            self.socialNet[otherAgentId]['social'] = self.socialLinkMinStren
                        else:
                            self.socialNet[otherAgentId]['social']+=stren
                except Exception, err:
                        print 'Failed to create social link: {}, {}, {}'.format(self.agentId, otherAgentId, err)


    def entropy(self):
        '''
        Degrade toward disorder - per tick
            - Social Net - done globally to avoid duplication
            - Family Net - as above
            - Resources?
            - Age
            - Chance of reprod
        '''
        #Age Agent
        self.age+=(self.timeStep*self.agentAgeRate)
        #Age Social net
        for k in self.socialNet.keys():
            if self.socialNet[k].has_key('social'):
                self.socialNet[k]['social']-=self.socialLinkAgeRate
                if self.socialNet[k]['social'] < self.socialLinkMinStren:
                    self.socialNet[k]['social'] = self.socialLinkMinStren
                if self.socialNet[k]['social'] > self.socialLinkMaxStren:
                    self.socialNet[k]['social'] = self.socialLinkMaxStren


    def reprod(self):
        '''
        Reproduce
        TODO
        '''
        pass






    #Probability generation (socialnets now with Agents instead of world)
    def positiveProbsLin(self, numSamps):
        '''
        Create a linear (y=x) distribution weighted toward higher numbers
        '''
        return np.arange(numSamps)/np.sum(np.arange(numSamps))


    def negativeProbsLin(self, numSamps):
        '''
        Create a linear (y=x) distribution weighted toward lower numbers
        '''
        return self.positiveProbsLin(numSamps)[::-1]


    def positiveProbsPow(self, numSamps):
        '''
        Create a power (y=x^2) distribution weighted toward higher numbers
        '''
        t = np.power(np.arange(numSamps),2.0)
        return t/np.sum(t)


    def negativeProbsPow(self, numSamps):
        '''
        Create a linear (y=x^2) distribution weighted toward lower numbers
        '''
        return self.positiveProbsPow(numSamps)[::-1]


    def positiveProbsExp(self, numSamps):
        '''
        Create a exponential distribution weighted toward higher numbers
        '''
        t = np.exp2(np.arange(numSamps))
        return t/np.sum(t)


    def negativeProbsExp(self, numSamps):
        '''
        Create a exponential distribution weighted toward lower numbers
        '''
        return self.positiveProbsExp(numSamps)[::-1]






