'''
Created on 25 Dec 2016

@author: dusted-ipro

Setup data about the world

'''
import numpy as np
import networkx as nx

#Global Clan UID List - popped on creation, appended back to pool on death
clanUIDs = range(0, 1000)
def nextClanUID():
    return clanUIDs.pop(clanUIDs.index(np.random.choice(clanUIDs)))

def recycleClanUID(uid):
    clanUIDs.append(uid)

#Global Agent UID List - popped on creation, appended back to pool on death
agentUIDs = range(1001, 1000000)
def nextAgentUID():
    return agentUIDs.pop(agentUIDs.index(np.random.choice(agentUIDs)))

def recycleAgentUID(uid):
    agentUIDs.append(uid)

#UNITS - Astro Units to Light Years
def au2Ly(au):
    '''
    Convert given AU to light years
    '''
    return au*(1.538*10e-5)

def ly2Au(ly):
    '''
    Convert given light years to AU
    '''
    return ly/(1.538*10e-5)

def getPopn():
    '''
    Get the current total population
    '''
    pop = 0
    for c in clans:
        pop+=len(c.agents)
    return pop

def genAgentMaxVelMag():
    '''
    Randomly generate an agent max velocity magnitude
    Max velocities - init randomly so genetics pass the trait along
    '''
    return np.random.choice(np.linspace(au2Ly(1.0), au2Ly(10.0)))

def genHarvestorCaps():
    '''
    Randomly generate capacities for harvestor
    Tons
    '''
    return (np.random.choice(np.linspace(10.0, 100.0)), #Raw Mat Cap
            np.random.choice(np.linspace(10.0, 100.0)), #Energy Cap
            np.random.choice(np.linspace(10.0, 100.0))) #HG Cap

def genHarvestorRates():
    '''
    Randomly generate harvest & consume rates for harvestor
    Tons per tick
    '''
    return (np.random.choice(np.linspace(0.1, 1.0)), #Energy Harvest
            np.random.choice(np.linspace(0.1, 1.0)), #Raw Mat Harvest
            np.random.choice(np.linspace(0.0001, 0.01)), #HG Consume
            np.random.choice(np.linspace(0.0001, 0.01))) #Energy Consume

def genClanRates():
    '''
    Randomly generate clan global consumption rates
    Tones per tick
    '''
    return (np.random.choice(np.linspace(0.01, 1.0)), 0.0)


#Total Stars
numStars = 1000
#Size of the universe (light-years)
universeDims = np.array([100.0, 100.0, 100.0])
#Average Solar system dimension - LY
d = au2Ly(10.0)
solarSystemDims = np.array([d, d, d])
#Average planets per solar system
avgPlanets = 5
#Position stores
starCoords = [] #[[x,y,z], ...]
#Energy amounts possible on a star - MegaWatts?
starEnergyOpts = np.linspace(1000.0, 1000000.0)
#Planet Sizes LY
d = au2Ly(0.0001)
e = au2Ly(0.1)
starRadiusOpts = np.linspace(d, e)
#Instantiated star class storage
stars = []

#Number of planets - this is procedurally generated
numPlanets = 0
#Energy amounts possible on a planet - MegaWatts?
planetEnergyOpts = np.linspace(0.0, 1000.0)
#Raw Material amounts possible on a planet - Tons?
planetRawMatOpts = np.linspace(0.0, 1000.0)
#Planet Sizes LY
d = au2Ly(0.000001)
e = au2Ly(0.001)
planetRadiusOpts = np.linspace(d, e)

#Timestep - seconds
timeStep = 0.1
ticks = 0

#Time elapsed since start
runTime = 0.0

#Number of Clans
numClans = 1

#Clan Class storage
clans = {}

#Agent Globals - unique agent ID's that relate to node id's
agents = {}
deadAgents = {}
#Max Population - initially
maxPopn = 3
#Mix of types [ex, fa, ha, tr] (percentages of total popn)
agentTypeMix = [50.0, 0.0, 50.0, 0.0]
#Agent Base visibility = AU
agentBaseVis = au2Ly(1.0)
agentReprodChance = np.random.choice(np.linspace(0.1, 0.7))

#Society Globals - Nodes are integers of agent or clan UID's - the actual classes can be accessed via the global dict
socialNet = nx.Graph()
#Rate at which social links age (link strength per tick)
socialLinkAgeRate = 0.01
#Clan Link strength - base link strength between agent and clan (Clan links dont age)
clanLinkStren = 0.1
#Link creation strengths - base weight
chatLinkMinStrength = -10.0
chatLinkMaxStrength = 10.0
#BAse chance of a social link being created - 50/50
baseSocialLinkCreationSplit = [True, False]


def positiveProbsLin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward higher numbers
    '''
    return np.arange(numSamps)/np.sum(np.arange(numSamps))


def negativeProbsLin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward lower numbers
    '''
    return positiveProbsLin(numSamps)[::-1]


def positiveProbsPow(numSamps):
    '''
    Create a power (y=x^2) distribution weighted toward higher numbers
    '''
    t = np.power(np.arange(numSamps),2.0)
    return t/np.sum(t)


def negativeProbsPow(numSamps):
    '''
    Create a linear (y=x^2) distribution weighted toward lower numbers
    '''
    return positiveProbsPow(numSamps)[::-1]


def positiveProbsExp(numSamps):
    '''
    Create a exponential distribution weighted toward higher numbers
    '''
    t = np.exp2(np.arange(numSamps))
    return t/np.sum(t)


def negativeProbsExp(numSamps):
    '''
    Create a exponential distribution weighted toward lower numbers
    '''
    return positiveProbsExp(numSamps)[::-1]

def entropy():
    '''
    Global degrade function to be fired per tick
        - Resource Degrade
        - Universe expansion
    '''
    pass








