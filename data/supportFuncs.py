'''
Created on 25 Dec 2016

@author: dusted-ipro

Generic Support Functions
'''
import numpy as np
import pickle
from time import time
import os
import pygraphviz as pgv

from environment import world
from celestials.base import basePlanet, baseStar
from data.celestialTypes import planets, stars
from agents.explorer import explorer
from agents.fabricator import fabricator
from agents.harvestor import harvestor
from agents.trader import trader
from clans.base import baseClan
from data.tradableTypes import allTradables
from data.agentTypes import allAgents
from data.socialLinkTypes import allLinks
from datetime import datetime

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
        #saveUniverse()
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
                'socialLinkAgeRate':world.socialLinkAgeRate,
                'socialNet':world.socialNet,
                'clanUIDs':world.clanUIDs,
                'agentUIDs':world.agentUIDs,
                'ticks':world.ticks,
                'deadAgents':world.deadAgents
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
    world.linkAgeRate = worldData['socialLinkAgeRate']
    world.socialNet = worldData['socialNet']
    world.clanUIDs = worldData['clanUIDs']
    world.agentUIDs = worldData['agentUIDs']
    world.ticks = worldData['ticks']
    world.deadAgents = worldData['deadAgents']
    print 'Done Loading Universe'


def generateClans():
    '''
    Initialise a set a clans
    '''
    print 'Generating Clans...'
    #Just one for now - at the first star system planet
    rates = world.genClanRates()
    clanUID = world.nextClanUID()
    c = baseClan(world.stars[0].starIdx, world.stars[0].planets[0].position,
                 0, clanUID, rates[0])
    #Populate their blank resource knowledge and explorer job Q
    for idx, s in enumerate(world.stars):
        c.resourceKnowledge[idx] = {}
        c.explorerQ.append((idx, world.starCoords[idx]))
    #Add to dict lookup
    world.clans[clanUID] = c
    #Add Clan node into social graph
    world.socialNet.add_node(clanUID, type='clan')
    print 'Done Generating Clans'


def generateAgents():
    '''
    Generate an initial seed number of agents for new universe
    0=Explorer
    1=Fabricator
    2=Harvestor
    3=Trader
    '''
    print 'Generating Agents...'
    #Mix of types [ex, fa, ha, tr] (percentages of total popn)
    #Single clan for now:
    cnt = 0
    clanUID = world.clans.keys()[0]
    for idx, t in enumerate(world.agentTypeMix):
        for a in range(int((t/100.0)*world.maxPopn)):
            print cnt
            cnt+=1
            #Capacities & Rates
            caps = world.genHarvestorCaps()
            rates = world.genHarvestorRates()
            #Get the next agent UID
            agentUID = world.nextAgentUID()
            if idx == 0:
                #Explorer
                a = explorer(0, agentUID,
                              world.clans[clanUID].originCoords,
                              clanUID,
                              np.random.choice([9,10]))
            elif idx == 1:
                #Fabricator
                a = fabricator(1, agentUID,
                              world.clans[clanUID].originCoords,
                              clanUID,
                              np.random.choice(allTradables().keys()))
            elif idx == 2:
                #Harvestor
                caps = world.genHarvestorCaps()
                rates = world.genHarvestorRates()
                a = harvestor(2, agentUID,
                              world.clans[clanUID].originCoords,
                              clanUID,
                              caps[0], caps[1], caps[2],
                              rates[0], rates[1], rates[2], rates[3])
            elif idx == 3:
                #Trader
                a = trader(3, agentUID,
                              world.clans[clanUID].originCoords,
                              world.clans.keys()[0])
            else:
                pass
            #Add as node in world graph
            world.socialNet.add_node(agentUID, type='agent_{}'.format(allAgents()[idx]))
            #Initialise the agents social network link with clan here (its a new universe)
            a.addSocialLink(clanUID, allLinks()[0], world.clanLinkStren)
            #Add to world lookup
            world.agents[agentUID] = a
            #Add to clan lookup
            world.clans[clanUID].agents.append(agentUID)

    print 'Done Generating Agents'


def delAgent(agentUID, reason):
    '''
    Remove an Agent from the universe:
        - Class
        - Social Network
        - Clan
        - Star system
        - Record death
    '''
    try:
        world.socialNet.remove_node(agentUID)
    except:
        print 'Failed to Delete an agent from social Net: {}'.format(agentUID)
    #Clan
    try:
        idx = world.clans[world.agents[agentUID].clanID].agents.index(agentUID)
        world.clans[world.agents[agentUID].clanID].agents.pop(idx)
    except:
        print 'Failed to Delete an agent from Clan: {}'.format(agentUID)
    #Star Sys - horrific!
    try:
        world.stars[world.agents[agentUID].currStarSys].pop(world.stars[world.agents[agentUID].currStarSys].agents.index(agentUID))
    except:
        print 'Failed to Delete an agent from Star Sys: {}'.format(agentUID)
    #Class
    world.agents.pop(agentUID)
    #Record death
    world.deadAgents[agentUID] = {'reason':reason,
                                  'dtg':datetime.now().isoformat()}


def socialNetEntropy():
    '''
    Globally degrade the social network each tick
    This is a first basic implementation and presumes:
        - Agent links are non-directional (they both know each other equally well)
        - When links are created they are even between agents (They both know each other equally well)
    '''
    for (u,v,d) in world.socialNet.edges(data='social'):
        #Dont age clan, family etc
        if d.has_key('social'):
            d['social']-=world.socialLinkAgeRate
            if d['social'] < world.socialLinkMinStren:
                d['social'] = world.socialLinkMinStren
            if d['social'] > world.socialLinkMaxStren:
                d['social'] = world.socialLinkMaxStren



def export2Graphviz():
    '''
    Export the current graph to graphviz (manually as the internal funcs dont work on mac atm)
    '''
    import os
    os.environ['PATH'] = os.environ['PATH']+':/usr/local/bin'
    G = pgv.AGraph()
    G.add_nodes_from(world.socialNet.nodes())
    for e in world.socialNet.edges(data=True):
        if e[2].has_key('social'):
            G.add_edge(e[0], e[1], label=e[2]['social'])
        elif e[2].has_key('clan'):
            G.add_edge(e[0], e[1], label=e[2]['clan'])
    G.layout(prog='dot')
    fn = "/Users/dusted-ipro/Documents/LiClipse Workspace/universe_abm/data/saves/{}{}".format(world.ticks, '_social_net.png')
    G.draw(fn)









