'''
Created on 25 Dec 2016

@author: dusted-ipro

Agent Based Model Engine / Main

'''
#Internals
import pickle
import os
from time import sleep
import numpy as np
#Globals
import environment.world as world
from data.supportFuncs import generateUniverse, loadUniverse
#Data
from data.agentTypes import allAgents
from data.celestialTypes import planets, stars
from data.tradableTypes import allTradables
#Agents
from agents.explorer import explorer as a_explorer
from agents.fabricator import fabricator as a_fabricator
from agents.harvestor import harvestor as a_harvestor
from agents.trader import trader as a_trader
from celestials.base import basePlanet, baseStar
from clans.base import baseClan


class abm(object):
    '''
    Core ABM
    '''

    def __init__(self, newUniverse):
        '''
        Constructor
        '''
        if newUniverse == True:
            #Regenerate Universe
            generateUniverse(True)
        else:
            #Load latest universe
            loadUniverse()
        #Print Some Stats
        print 'Agent PopN: {}'.format(len(world.agents))
        print 'Clan PopN: {}'.format(len(world.clans))
        print 'Planets: {}'.format(world.numPlanets)
        print 'Stars: {}'.format(len(world.stars))
        print 'Universe Dims (LY):{}, {}, {}'.format(world.universeDims[0],
                                                     world.universeDims[1],
                                                     world.universeDims[2])
        print 'World Successfully Initialised'

    def run(self):
        '''
        Run the world
        '''
        try:
            for i in range(1000):
                print 'Step {}'.format(i)
                for a in world.agents:
                    a.actions()
                    print '============'
                    print 'Agent:{}'.format(a.agentId)
                    print 'Clan Home Star:{}'.format(world.starCoords[world.clans[a.clanId].originStarIdx])
                    print 'Pos:{}'.format(a.position)
                    print 'Target:{}'.format(a.destination)
                    print 'Vel:{}'.format(a.velocity)
                    try:
                        print 'Dist:{}'.format(np.linalg.norm(a.destination-a.position))
                    except:
                        pass
                    print 'Activity:{}'.format(a.activityLookup[a.activity])
                    print '============'
                sleep(0.1)
        except KeyboardInterrupt:
            print '{}'.format('Run interrupt')
            return


if __name__ == '__main__':
    print 'Hello ABM'
    model = abm(True)
    model.run()
    del model
    print 'Goodbye ABM'






