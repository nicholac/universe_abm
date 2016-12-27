'''
Created on 25 Dec 2016

@author: dusted-ipro
'''
import numpy as np

from data.celestialTypes import planets, stars
from environment.sensing import closestStar

class basePlanet(object):
    '''
    Basic Info about a planet
    '''

    def __init__(self, starIdx, coords, radius, planetIdx, typeId, energyStore, rawMatStore):
        '''
        Constructor
        '''
        #Universe position
        self.position = np.array(coords)
        #Star Index
        self.starIdx = starIdx
        #Radius - Light years
        self.radius = radius
        #Planet unique ID in this system
        self.planetIdx = planetIdx
        self.name = 'star_{}_planet_{}'.format(self.starIdx, self.planetIdx)
        #Celestial Type Info
        self.typeId = typeId
        self.typeName = planets()[self.typeId]
        #Resources
        self.energyStore = energyStore
        self.rawMatStore = rawMatStore

    def localPopn(self, AU):
        '''
        Get the number of agents in the given AU area
        '''
        pass


class baseStar(object):
    '''
    Basic Info about a star
    '''

    def __init__(self, starIdx, coords, radius, celestialId, typeId, energyStore):
        '''
        Constructor
        '''
        #Universe position - LY
        self.position = np.array(coords)
        #This is the index in the world star array
        self.starIdx = starIdx
        #Radius - LY
        self.radius = radius
        #Celestial unique ID - index in world.starCoords
        self.celestialId = celestialId
        self.name = 'celestial_{}'.format(self.celestialId)
        #Celestial Type Info
        self.typeId = typeId
        self.typeName = stars()[self.typeId]
        #Resources
        self.energyStore = energyStore
        #Planets - instantiated classes
        self.planets = []
        #Planet Coords - for ease / rapid searching
        self.planetCoords = None
        #Agents in system
        self.agentsInSys = []


    def localPopn(self, AU):
        '''
        Get the number of agents in the given AU area
        '''
        pass
