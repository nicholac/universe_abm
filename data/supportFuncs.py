'''
Created on 25 Dec 2016

@author: dusted-ipro

Generic Support Functions
'''
import numpy as np
import pickle
from time import time
import os

from environment import world
from celestials.base import basePlanet, baseStar
from data.celestialTypes import planets, stars
from agents.explorer import explorer
from agents.fabricator import fabricator
from agents.harvestor import harvestor
from agents.trader import trader
from clans.base import baseClan
from data.tradableTypes import allTradables

def generateUniverse(save):
    '''
    Generate a new universe from blank:
        - Stars - total number
        - Planets - average per star
        - Agents, Clans, Civs - Seed
    Optionally save to pickle after generation
    '''
    print 'Generating Stars and Solar Systems...'
    #Distribute stars randomly in our 3D space - dims in lightyears
    world.starCoords = np.dstack([np.random.normal(world.universeDims[0]/2.0, world.universeDims[0]/3.0, size=world.numStars),
                                 np.random.normal(world.universeDims[1]/2.0, world.universeDims[1]/3.0, size=world.numStars),
                                 np.random.normal(world.universeDims[2]/2.0, world.universeDims[2]/3.0, size=world.numStars)])[0]
    #Generate the star classes
    for idx, c in enumerate(world.starCoords):
        star = baseStar(idx, c, np.random.choice(world.starRadiusOpts),
                        idx, np.random.choice(stars().keys()),
                        np.random.choice(world.starEnergyOpts))
        #Generate planets for this star
        numPlanets = np.random.choice([world.avgPlanets/2.0, world.avgPlanets, world.avgPlanets*2.0])
        #Generate coords for the entire system - initially these are relative to star centre
        planetCoords = np.dstack([np.random.normal(world.solarSystemDims[0]/2.0, world.solarSystemDims[0]/3.0, size=numPlanets),
                            np.random.normal(world.solarSystemDims[1]/2.0, world.solarSystemDims[1]/3.0, size=numPlanets),
                            np.random.normal(world.solarSystemDims[2]/2.0, world.solarSystemDims[2]/3.0, size=numPlanets)]
                            )[0]
        for pidx, pc in enumerate(planetCoords):
            #Generate the planet class
            #Rebase coords relative to this star system
            coords = c+pc
            planet = basePlanet(idx, coords, np.random.choice(world.planetRadiusOpts),
                                pidx, np.random.choice(planets().keys()),
                                np.random.choice(world.planetEnergyOpts),
                                np.random.choice(world.planetRawMatOpts))
            star.planets.append(planet)
            if star.planetCoords == None:
                #First one
                star.planetCoords = coords
            else:
                star.planetCoords = np.vstack((star.planetCoords, coords))
            world.numPlanets+=1
        world.stars.append(star)

    #Generate Clans
    generateClans()

    #Agents
    generateAgents()

    #Save out the data
    if save == True:
        print 'Saving Universe...'
        #TODO: Solve the Q pickle problem
        saveUniverse()
    print 'Generate Universe Complete'


def saveUniverse():
    '''
    Pickle the universe data and setup vars
    '''
    worldData = {'numStars':world.numStars,
                'universeDims':world.universeDims,
                'solarSystemDims':world.solarSystemDims,
                'avgPlanets':world.avgPlanets,
                'starCoords':world.starCoords,
                'starEnergyOpts':world.starEnergyOpts,
                'starRadiusOpts':world.starRadiusOpts,
                'stars':world.stars,
                'numPlanets':world.numPlanets,
                'planetEnergyOpts':world.planetEnergyOpts,
                'planetRawMatOpts':world.planetRawMatOpts,
                'planetRadiusOpts':world.planetRadiusOpts,
                'maxPopn':world.maxPopn,
                'agentTypeMix':world.agentTypeMix,
                'agentBaseVis':world.agentBaseVis,
                'agentReprodChance':world.agentReprodChance,
                'agents':world.agents,
                'clans':world.clans,
                'linkAgeRate':world.linkAgeRate
               }
    #Time based FN if we want no overwrites in future
    timeFn = str(int(time()))
    fp = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves', 'universedump.pkl'), 'w')
    pickle.dump(worldData, fp)
    fp.close()
    print 'Done Save'


def loadUniverse():
    '''
    Load the universe data back in from a pickle
    '''
    print 'Loading Universe...'
    fp = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves', 'universedump.pkl'), 'r')
    worldData = pickle.load(fp)
    fp.close
    world.numStars = worldData['numStars']
    world.universeDims = worldData['universeDims']
    world.solarSystemDims = worldData['solarSystemDims']
    world.avgPlanets = worldData['avgPlanets']
    world.starCoords = worldData['starCoords']
    world.starEnergyOpts = worldData['starEnergyOpts']
    world.starRadiusOpts = worldData['starRadiusOpts']
    world.stars = worldData['stars']
    world.numPlanets = worldData['numPlanets']
    world.planetEnergyOpts = worldData['planetEnergyOpts']
    world.planetRawMatOpts = worldData['planetRawMatOpts']
    world.planetRadiusOpts = worldData['planetRadiusOpts']
    world.maxPopn = worldData['maxPopn']
    world.agentTypeMix = worldData['agentTypeMix']
    world.agentBaseVis = worldData['agentBaseVis']
    world.agentReprodChance = worldData['agentReprodChance']
    world.agents = worldData['agents']
    world.clans = worldData['clans']
    world.linkAgeRate = worldData['linkAgeRate']
    print 'Done Loading Universe'


def generateClans():
    '''
    Initialise a set a clans
    '''
    print 'Generating Clans...'
    #Just one for now - at the first star system planet
    c = baseClan(world.stars[0].starIdx, world.stars[0].planets[0].position,
                 0, len(world.clans))
    #Populate their blank resource knowledge and explorer job Q
    for idx, s in enumerate(world.stars):
        c.resourceKnowledge[idx] = {}
        c.explorerQ.append((idx, world.starCoords[idx]))
    world.clans.append(c)
    print 'Done Generating Clans'


def generateAgents():
    '''
    Generate an initial seed number of agents for new universe
    '''
    print 'Generating Agents...'
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    for idx, t in enumerate(world.agentTypeMix):
        for a in range(int((t/100.0)*world.maxPopn)):
            if idx == 0:
                #Explorer
                ex = explorer(0, len(world.agents),
                              world.clans[0].originCoords,
                              world.clans[0].clanId,
                              np.random.choice([9,10]))
                world.agents.append(ex)
                #Clan agents are idx lookups
                world.clans[0].agents.append(idx)
            elif idx == 1:
                #Fabricator
                fa = fabricator(0, len(world.agents),
                              world.clans[0].originCoords,
                              world.clans[0].clanId,
                              np.random.choice(allTradables().keys()))
                world.agents.append(fa)
                #Clan agents are idx lookups
                world.clans[0].agents.append(idx)
            elif idx == 2:
                #Harvestor
                ha = harvestor(0, len(world.agents),
                              world.clans[0].originCoords,
                              world.clans[0].clanId,
                              np.random.choice(allTradables().keys()))
                world.agents.append(ha)
                #Clan agents are idx lookups
                world.clans[0].agents.append(idx)
            elif idx == 3:
                #Trader
                tr = trader(0, len(world.agents),
                              world.clans[0].originCoords,
                              world.clans[0].clanId)
                world.agents.append(tr)
                #Clan agents are idx lookups
                world.clans[0].agents.append(idx)

    print 'Done Generating Agents'











