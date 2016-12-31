'''
Created on 25 Dec 2016

@author: dusted-ipro

Contains callable data structures for all service types

'''

def allActions():
    '''
    All Action Types (Agent <-> Agent)
    ::returns Dict All types
    '''
    return {0:{'name':'idle','activityLookup':{}
               },
            1:{'name':'exploreResources', 'activityLookup':{0:'idle', 1:'moveStarSys', 2:'visitPlanets', 3:'checkResources',
                                               4:'returnClan', 5:'depositKnowledge'}
               },
            2:{'name':'harvestResources', 'activityLookup':{0:'idle', 1:'moveStarSys', 2:'harvesting', 3:'waitingService',
                               4:'returnHome', 5:'avoidingCriminal', 6:'avoidingMilitary'}
               },
            3:{'name':'transport', 'activityLookup':{}
               },
            4:{'name':'defence', 'activityLookup':{}
               },
            5:{'name':'find', 'activityLookup':{}
               },
            }


