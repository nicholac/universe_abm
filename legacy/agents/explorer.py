'''
Created on 24 Dec 2016

@author: dusted-ipro
'''
import numpy as np


def get_starsys(agent_doc, sysAgentCoords, mongo_coll):
    '''
    Get a star system to explore - next from clan
    '''
    clan_doc = mongo_coll.find({'_id':agent_doc['clanId']}).next()
    #Get subset of unknown (star catalogue contains everything)
    subset = [i for i in clan_doc['starCatalogue'] if i not in clan_doc['resourceKnowledge'].keys()]
    #Key closest by Index
    idx = np.argmin([np.linalg.norm(np.array(agent_doc['position'])-x) for x in subset])
    #Set as destination and add to resource knowledge - as blank so the other agents know its taken
    #This only works in-system!, because the doc remains local until system is processed
    #clan_doc['resourceKnowledge'][idx] = {}
    #Set destination as outbound star
    agent_doc['destination'] = clan_doc['starCatalogue'][idx]
    #Set activity to moving
    agent_doc['acty'] = 1
    #Set the ultimate target system - remember this is the index in the CLAN Star Catalogue coords list
    agent_doc['actyData'] = {'tgtStarSys':idx, 'planetsVisited':[]}
    #Update the clan doc
    mongo_coll.find_and_update({'_id':agent_doc['clanId']}, {'$set':{'resourceKnowledge.{}'.format(idx):{}}})



#=====================
#from environment import world
# from environment.sensing import closestStar, dist
# from agents.base import baseAgent
# from data.tradableTypes import allTradables
# from data.actionTypes import allActions
# class explorer(baseAgent):
#     '''
#     Explorer Agent
#       - Gets a star the clan has no-knowledge of (closest without knowledge)
#       - Moves to Star
#       - Visits planets in solar system
#       - Checks for energy or raw mat - records for each planet
#       - Returns to clan origin and
#       - Deposits knowledge
#     '''
#
#     def __init__(self, agentType, agentId, coords, clanId, resourceType):
#         '''
#         resourceType is either energy coords or raw mat coords - coords are tradable
#         '''
#         baseAgent.__init__(self, agentType, agentId, coords, clanId)
#         #Explorer searches for an supplies coordinates of resourceType
#         self.store = {resourceType:{'store':0.0, 'capacity':1000000.0},
#                       7:{'store':0.0, 'capacity':1000000.0}}
#         #Max Speed in System - LY / Sec
#         self.maxVelMag = world.genAgentMaxVelMag()
#         self.consumes = {7:{'consumeRate':1.0}}
#
#
#         #All Available to this agent
#         self.actionsAll = {0:{'func':self.idle, 'args':[], 'activity':0,
#                               'expiry':0.0, 'status':None,
#                               'blocking':False, 'default':False},
#                            1:{'func':self.exploreResources, 'args':[], 'activity':0,
#                               'expiry':0.0, 'status':None,
#                               'blocking':False, 'default':True},
#                            5:{'func':self.find, 'args':[], 'activity':0,
#                               'expiry':0.0, 'status':None,
#                               'blocking':False, 'default':False}
#                            }
#         #Actions offered as services to others
#         self.actionsOffered = [5]
#         #Contracts are actions that have been demanded as being required
#         self.activeContracts = {}
#         #Current Action (id matches actionTypes lookup)
#         #Default on init
#         for k in self.actionsAll.keys():
#             if self.actionsAll[k]['default'] == True:
#                 self.action = k
#
#
#     def exploreResources(self, args):
#         '''
#         Default Action
#         Offered Action - Explore the universe finding resources
#         args = []
#         '''
#         if self.actionsAll[self.action]['activity'] == 1 or self.actionsAll[self.action]['activity'] == 0:
#             #Are we in the target system?
#             if self.currStarIdx == self.targetStar:
#                 self.actionsAll[self.action]['activity'] = 2
#                 self.targetPlanet = 0
#                 self.destination = world.stars[self.currStarIdx].planets[0].position
#                 return
#             #Do we have a target star system yet?
#             if self.destination == None:
#                 #Get clan next unknown from Q
#                 #closestStarUk = world.clans[self.clanId].closestUnknownStar(self.position)
#                 try:
#                     nextStar = world.clans[self.clanId].explorerQ.popleft()
#                     self.actionsAll[self.action]['activity'] = 1
#                 except IndexError:
#                     #Set Idle - Wait in system until clan put more jobs into the Q
#                     self.actionsAll[self.action]['activity'] = 0
#                     return
#                 #Set Dest - its not in the system we are i so this is the jump out star
#                 self.destination = world.starCoords[self.currStarIdx]
#                 self.targetStar = nextStar[0]
#                 return
#             #Are we close enough to current star to jump?
#             if dist(self.position, self.destination) < self.starJumpDist:
#                 #Jump & swap to visit planets
#                 self.starJump(self.targetStar)
#                 self.actionsAll[self.action]['activity'] = 2
#                 self.targetPlanet = 0
#                 self.destination = world.stars[self.currStarIdx].planets[0].position
#             #Move closer to jump star
#             else:
#                 self.systemMove(self.maxVelMag)
#         elif self.actionsAll[self.action]['activity'] == 2:
#             #Are we close enough to scan?
#             if dist(self.position, self.destination) < self.visibilityRange:
#                 #Stop
#                 self.stop()
#                 self.actionsAll[self.action]['activity'] = 3
#                 return
#             else:
#                 #Move closer to target planet
#                 self.systemMove(self.maxVelMag)
#                 return
#         elif self.actionsAll[self.action]['activity'] == 3:
#             #Store the resources of the closest planet
#             self.storeResourceKnowledge(world.stars[self.currStarIdx].planets[self.targetPlanet].store,
#                                         self.currStarIdx,
#                                         self.targetPlanet)
#             #Have we done all planets?
#             if len(self.resourceKnowledge[self.targetStar].keys()) == len(world.stars[self.currStarIdx].planets):
#                 #Yes - swap to return home
#                 self.actionsAll[self.action]['activity'] = 4
#                 #Destination is initially local star (for jump)
#                 self.destination = world.starCoords[self.currStarIdx]
#                 self.targetPlanet = world.clans[self.clanId].originPlanetIdx
#                 self.targetStar = world.clans[self.clanId].originStarIdx
#             else:
#                 #No - Swap target planet
#                 self.targetPlanet+=1
#                 self.actionsAll[self.action]['activity'] = 2
#                 self.destination = world.stars[self.currStarIdx].planets[self.targetPlanet].position
#             return
#         elif self.actionsAll[self.action]['activity'] == 4:
#             #Are we in clan home system?
#             if self.currStarIdx == self.targetStar:
#                 #Are we close enough to clan home planet to dump knowledge?
#                 if dist(self.position, self.destination) < self.visibilityRange:
#                     #Push knowledge to clan
#                     self.actionsAll[self.action]['activity'] = 5
#                     world.clans[self.clanId].rxResourceKnowledge(self.resourceKnowledge)
#                     #Clear own knowledge
#                     self.resourceKnowledge = {}
#                     #Swap to moveStar
#                     self.actionsAll[self.action]['activity'] = 1
#                     self.destination = None
#                     self.targetPlanet = None
#                     self.targetStar = None
#                     return
#                 else:
#                     #Move closer to target planet
#                     self.systemMove(self.maxVelMag)
#                     return
#             #Are we close enough to outer star to jump home?
#             elif dist(self.position, self.destination) < self.starJumpDist:
#                 #Jump
#                 self.starJump(self.targetStar)
#                 #Swap destination to clan home planet (now we are in correct system)
#                 self.destination = world.stars[world.clans[self.clanId].originStarIdx].planets[world.clans[self.clanId].originPlanetIdx].position
#                 return
#             else:
#                 #Move closer to star
#                 self.systemMove(self.maxVelMag)
#                 return
#         return
#
#     def find(self):
#         '''
#         Offered Action - Find
#         '''








