'''
Created on 25 Dec 2016

@author: dusted-ipro

Basic data about the world

'''
import numpy as np

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
    return np.random.choice(np.linspace(au2Ly(0.1), au2Ly(1.0)))

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
timeStep = 1.0

#Time elapsed since start
runTime = 0.0

#Number of Clans
numClans = 1

#Clan Class storage
clans = []

#Agent Globals
#Max Population - initially
maxPopn = 1
#Mix of types [ex, fa, ha, tr] (percentages of total popn)
agentTypeMix = [100.0, 0.0, 0.0, 0.0]
#Agent Base visibility = AU
agentBaseVis = au2Ly(1.0)
agentReprodChance = np.random.choice(np.linspace(0.1, 0.7))
agents = []


#Society Globals
#Rate at which social links age (link strength per tick)
linkAgeRate = 0.01













