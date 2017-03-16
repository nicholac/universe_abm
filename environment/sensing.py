'''
Created on 25 Dec 2016

@author: dusted-ipro

Sensing functions for agents detecting stuff in the environment

'''
import numpy as np


def dist(coords1, coords2):
    '''
    Basic 3D dist - not sure I really need to subclass this
    '''
    return np.linalg.norm(coords1-coords2)


def closest_star(position, star_coords):
    '''
    Return the closest star from the given list of starCoords - idx and coords
    ::param position x,y,z array
    ::param star_coords array of xyz coords
    '''
    idx = np.argmin([np.linalg.norm(np.array(position)-x) for x in star_coords])
    return star_coords[idx]


# def closestStarSubSet(coords, starCoords):
#     '''
#     Return the closest star from the given list of starCoords - idx and coords
#     '''
#     idx = np.argmin([np.linalg.norm(coords-x) for x in starCoords])
#     return (idx, starCoords[idx])
#
#
# def closestPlanetSys(coords, starIdx):
#     '''
#     Return the closest planet (searches just the star system universe) - idx and coords
#     '''
#     idx = np.argmin([np.linalg.norm(coords-x) for x in world.stars[starIdx].planetCoords])
#     return (idx, world.stars[starIdx].planetCoords[idx])
#
#
# def starSysPlanets(starIdx):
#     '''
#     Get all the planet coords in this star system
#     '''
#     return world.stars[starIdx].planetCoords
#
#
# def planetsInRange(coords, dist, starIdx):
#     '''
#     Get all planets within given range - only searches star system
#     Returns a list of planet indexes in the star system
#     '''
#     #Get the ones in range
#     outDists = [np.linalg.norm(x.position-coords) for x in starSysPlanets(starIdx)]
#     outIdx = starSysPlanets(starIdx)[np.where(map(lambda x: x<=dist, outDists))]
#     return outIdx
#
#
# def checkHarvestEnv(agent):
#     '''
#     Check for harvestor agents resources within range - on planets, stars
#     Presumes the agent can collect!
#     '''
#     #Get celestials in visibility range (LY)
#     pIdx = planetsInRange(agent.position, agent.visibilityRange, agent.currStarIdx)
#     #NEXT: Check for presence of the actual resource on planets we can see
#
#
# def checkExploreEnv(agent):
#     '''
#     Check for explorer agents resources within range - on planets, stars
#     Presumes the agent can collect
#     '''
#     #Get celestials in visibility range (LY)
#     pIdx = planetsInRange(agent.position, agent.visibilityRange, agent.currStarIdx)
#     #NEXT: Check for presence of the actual resource on planets we can see



