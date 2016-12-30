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
from data.supportFuncs import generateUniverse, loadUniverse, socialNetEntropy, export2Graphviz


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
            cnt = 0
            while True:
                cnt+=1
                world.ticks+=1
                print 'Step {}'.format(cnt)
                for k in world.agents.keys():
                    a = world.agents[k]
                    a.actions()
                    print '============'
                    print 'Agent:{} {}'.format(a.agentId, a.agentName)
                    print 'Clan Home Star:{}'.format(world.starCoords[world.clans[a.clanId].originStarIdx])
                    print 'Pos:{}'.format(a.position)
                    print 'Target:{}'.format(a.destination)
                    try:
                        print 'Dist:{}'.format(np.linalg.norm(a.destination-a.position))
                    except:
                        pass
                    print 'Activity:{}'.format(a.activityLookup[a.activity])
                    #Stores
                    try:
                        print 'Stores: {}'.format(a.store)
                    except:
                        pass
                    for ck in world.clans.keys():
                        print 'Clan Stores:{}'.format(world.clans[ck].store)
                    print '============'
                sleep(world.timeStep)
                #Global Entropy
                socialNetEntropy()
                #Save social net every X steps
                if cnt%100 == 0:
                    export2Graphviz()
        except KeyboardInterrupt:
            print '{}'.format('Run interrupt')
            return


if __name__ == '__main__':
    print 'Hello ABM'
    model = abm(True)
    model.run()
    del model
    print 'Goodbye ABM'






