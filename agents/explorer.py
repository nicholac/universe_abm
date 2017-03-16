'''
Created on 24 Dec 2016

@author: dusted-ipro
'''
import numpy as np

from agents import base as base_agent
from environment.sensing import dist


def get_starsys(agent_doc, sys_agent_coords, mongo_coll):
    '''
    Get a star system to explore - next from clan
    '''
    clan_doc = mongo_coll.find({'_id':agent_doc['clanId']}).next()
    subset = [i for i in clan_doc['starCatalogue'] if i['_id'] not in [j['starId'] for j in clan_doc['resourceKnowledge']]]
    #Check if there are any unknown stars
    if len(subset) == 0:
        #Set Idle
        agent_doc['actyData'] = {}
        agent_doc['actyData']['actyId'] = 0
        agent_doc['actyData']['actyIdx'] = 01
        agent_doc['actyGroup'] = 0
        agent_doc['destination'] = []
        agent_doc['actyData']['complete'] = True
        return
    #Get subset of unknown (star catalogue contains everything)
    closestStar = subset[np.argmin([np.linalg.norm(np.array(agent_doc['position'])-x['position']) for x in subset])]
    #Set as destination and add to resource knowledge - as blank so the other agents know its taken
    #This only works in-system!, because the doc remains local until system is processed
    #clan_doc['resourceKnowledge'][idx] = {}
    #Set destination as outbound star
    agent_doc['destination'] = mongo_coll.find({'_id':clan_doc['starId']}).next()['position']
    #Set the ultimate target system - remember this is the index in the CLAN Star Catalogue coords list
    agent_doc['actyData']['tgtSys'] = closestStar['_id']
    agent_doc['actyData']['tgtStarCoords'] = closestStar['position']
    #Actual planet target gets populated by next acty
    agent_doc['actyData']['tgtCoords'] = []
    #Update the clan doc
    clan_doc['resourceKnowledge'].append({'starId':closestStar['_id'], 'planets':[]})
    mongo_coll.find_and_modify({'_id':agent_doc['clanId']},
                               {'$set':{'resourceKnowledge':clan_doc['resourceKnowledge']}})
    #Set activity complete
    agent_doc['actyData']['complete'] = True


def deposit_knowledge(agent_doc, sys_agent_coords, mongo_coll):
    '''
    Deposit an explorers knowledge at the clan home planet
    '''
    #Remind ourselves which star system these planets came from
    starId = mongo_coll.find({'_id':agent_doc['actyData']['planets'][0]['_id']},
                             {'starId':1}).next()['starId']
    clan_doc = mongo_coll.find({'_id':agent_doc['clanId']}).next()
    [i for i in clan_doc['resourceKnowledge'] if i['starId'] == starId][0]['planets'] = agent_doc['actyData']['planets']
    #TODO: This is working on a local copy of the clan doc which is dangerous if other stuff is editing it
    #We are only updating the resource knowledge to make it a bit safer but needs checking
    mongo_coll.find_one_and_update({'_id':agent_doc['clanId']},
                                    {'$set':{'resourceKnowledge':clan_doc['resourceKnowledge']}})
    print '% Discovered: {}'.format((len(clan_doc['resourceKnowledge'])/len(clan_doc['starCatalogue']))*100)
    #Reset the agent acty data
    agent_doc['actyData'].pop('planets')
    agent_doc['actyData'].pop('tgtSys')
    agent_doc['actyData'].pop('tgtStarCoords')
    agent_doc['actyData'].pop('tgtCoords')
    agent_doc['actyData'].pop('planetTgtId')
    agent_doc['actyData']['complete'] = True



def visit_planets(agent_doc, sys_agent_coords, mongo_coll):
    '''
    Visit all System planets in turn and scan each
    '''
    #Populate list of planets to visit if not already
    try:
        agent_doc['actyData']['planets']
    except KeyError:
        #No planets yet - Populate the list of planets in this system
        planets = list(mongo_coll.find({'_type':'planet', 'starId':agent_doc['starId']},
                                       {'_id':1}))
        agent_doc['actyData']['planets'] = []
        for i in planets:
            agent_doc['actyData']['planets'].append({'_id':i['_id'],
                                                     'visited':False,
                                                      'energyStore':None,
                                                      'rawMatStore':None})
        #Set the first one as the the current target
        agent_doc['actyData']['planetTgtId'] = agent_doc['actyData']['planets'][0]['_id']
        agent_doc['destination'] = np.array(mongo_coll.find({'_id':agent_doc['actyData']['planets'][0]['_id']},
                                                            {'position':1}).next()['position'])

    #Do we have a current planet target?
    if agent_doc['actyData']['planetTgtId'] != None:
        #Are we in range to collect data?
        if dist(agent_doc['destination'], agent_doc['position']) < agent_doc['vis']:
            #Collect data
            energy, rawMat = check_planet_resources(mongo_coll, agent_doc['actyData']['planetTgtId'])
            planet = [i for i in agent_doc['actyData']['planets'] if i['_id'] == agent_doc['actyData']['planetTgtId']][0]
            planet['energyStore'] = energy
            planet['rawMatStore'] = rawMat
            #Set visited
            planet['visited'] = True
            #Set target ID to None - gets picked up next time
            agent_doc['actyData']['planetTgtId'] = None
        else:
            #Move closer
            base_agent.system_move(agent_doc, sys_agent_coords, mongo_coll)
    else:
        try:
            #Get the next planet to be visited
            agent_doc['actyData']['planetTgtId'] = [i['_id'] for i in agent_doc['actyData']['planets'] if i['visited'] == False][0]
            #Get planet Coords & set dest
            agent_doc['destination'] = np.array(mongo_coll.find({'_id':agent_doc['actyData']['planetTgtId']},
                                                                {'position':1}).next()['position'])
        except IndexError:
            #All visited - set clan as tgt system and final destination
            clan_doc = mongo_coll.find({'_id':agent_doc['clanId']},
                                        {'starId':1, 'position':1}).next()
            agent_doc['actyData']['tgtSys'] = clan_doc['starId']
            agent_doc['actyData']['tgtStarCoords'] = mongo_coll.find({'_id':agent_doc['actyData']['tgtSys']},
                                                                     {'position':1}).next()['position']
            #Set target within the target system
            agent_doc['actyData']['tgtCoords'] = clan_doc['position']
            #Set outbound star in this system as initial dest
            base_agent.set_outbound_star(agent_doc, mongo_coll)
            #Set acty complete
            agent_doc['actyData']['complete'] = True



def check_planet_resources(mongo_coll, planet_id):
    '''
    Check a planets Resources
    '''
    res = mongo_coll.find({'_id':planet_id},
                               {'energyStore':1, 'rawMatStore':1}).next()
    return res['energyStore'], res['rawMatStore']


#=====================
#from environment import world
# from environment.sensing import closestStar, dist
# from agents.base import baseAgent
# from data.tradable_types import allTradables
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








