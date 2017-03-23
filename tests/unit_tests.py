'''
Created on 19 Mar 2017

@author: dusted-ipro
'''
import unittest

from pymongo import MongoClient
import numpy as np
from scipy.spatial import distance


from environment.generate import generate_world, \
                                    generate_celestials, \
                                    generate_clans, \
                                    generate_agents, \
                                    agent_generate_map, \
                                    gen_explorer, \
                                    gen_harvestor, \
                                    gen_trader, \
                                    gen_soldier

from environment.sensing import closest_star

from agents.base import star_jump, set_outbound_star, \
                        system_move, numpify_agent, \
                        de_numpyify_agent, \
                        numpify_agent, \
                        age_kill


class Test(unittest.TestCase):


    def setUp(self):
        cli = MongoClient()
        db = cli.universeabm
        self.mongo_coll = db.universe


    def tearDown(self):
        self.mongo_coll.drop()



#     #GENERATE - WORKING
#
#     def testGenerateWorld(self):
#         '''
#         Generate the world doc
#         '''
#         generate_world(self.mongo_coll, True, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         self.assertNotEqual(world_doc, None)
#
#
#     def testGenerateCelestials(self):
#         '''
#         Generate the world doc
#         '''
#         generate_world(self.mongo_coll, True, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         generate_celestials(self.mongo_coll, True)
#
#         #Count Stars
#         cnt = self.mongo_coll.find({'_type':'star'}).count()
#         self.assertEqual(cnt, world_doc['universeInfo']['numStars'])
#
#         print 'Testing all star distances...'
#         #Distance between stars & Planets reasonable?
#         stars = list(self.mongo_coll.find({'_type':'star'}))
#         starDist = []
#         for i in stars:
#             for j in stars:
#                 if i['_id'] == j['_id']:
#                     continue
#                 starDist.append(distance.pdist([i['position'], j['position']])[0])
#
#
#         for star in stars:
#             planets = list(self.mongo_coll.find({'_type':'planet', 'starId':star['_id']}))
#             planetDist = []
#             for i in planets:
#                 for j in planets:
#                     planetDist.append(distance.pdist([i['position'], j['position']])[0])
#             #Check this solar systems planets are all closer to each other than the distances bwtween stars
#             self.assertEqual(np.max(planetDist) < np.min(starDist), True)
#
#         print 'Done star distances'
#
#         #TODO:Are the planets starId's actually the closest stars?
#
#     def testGenerateClans(self):
#         '''
#         Testing clan generation
#         '''
#         generate_world(self.mongo_coll, True, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         generate_celestials(self.mongo_coll, True)
#
#         generate_clans(self.mongo_coll, True)
#         #Right number of clans
#         self.assertEqual(self.mongo_coll.find({'_type':'clan'}).count(),
#                          world_doc['universeInfo']['numClans'])
#         #Clan homes are all different
#         clanStars = list(self.mongo_coll.find({'_type':'clan'}, {'_id':0, 'starId':1}))
#         for i in clanStars:
#             self.assertEqual(clanStars.count(i), 1)
#
#     def testGenExplorer(self):
#         generate_world(self.mongo_coll, True, True)
#         generate_celestials(self.mongo_coll, True)
#         generate_clans(self.mongo_coll, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]
#
#         #Check the map generator works
#         func = agent_generate_map(0)
#         self.assertEqual(isinstance(func, type(gen_explorer)), True)
#         ex = func(world_doc, clan_doc)
#         #Check we get a doc
#         self.assertNotEqual(ex['agentType'], None)
#         self.assertEqual(ex['agentType'], 0)
#
#     def testGenHarvestor(self):
#         generate_world(self.mongo_coll, True, True)
#         generate_celestials(self.mongo_coll, True)
#         generate_clans(self.mongo_coll, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]
#
#         #Check the map generator works
#         func = agent_generate_map(1)
#         self.assertEqual(isinstance(func, type(gen_harvestor)), True)
#         ex = func(world_doc, clan_doc)
#         #Check we get a doc
#         self.assertNotEqual(ex['agentType'], None)
#         self.assertEqual(ex['agentType'], 1)
#
#     def testGenTrader(self):
#         generate_world(self.mongo_coll, True, True)
#         generate_celestials(self.mongo_coll, True)
#         generate_clans(self.mongo_coll, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]
#
#         #Check the map generator works
#         func = agent_generate_map(2)
#         self.assertEqual(isinstance(func, type(gen_trader)), True)
#         ex = func(world_doc, clan_doc)
#         #Check we get a doc
#         self.assertNotEqual(ex['agentType'], None)
#         self.assertEqual(ex['agentType'], 2)
#
#     def testGenSoldier(self):
#         generate_world(self.mongo_coll, True, True)
#         generate_celestials(self.mongo_coll, True)
#         generate_clans(self.mongo_coll, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]
#
#         #Check the map generator works
#         func = agent_generate_map(3)
#         self.assertEqual(isinstance(func, type(gen_soldier)), True)
#         ex = func(world_doc, clan_doc)
#         #Check we get a doc
#         self.assertNotEqual(ex['agentType'], None)
#         self.assertEqual(ex['agentType'], 3)
#
#
#     def testGenerateAgents(self):
#         '''
#         Testing Agent generation
#         '''
#         generate_world(self.mongo_coll, True, True)
#         world_doc = self.mongo_coll.find({'_type':'world'}).next()
#         generate_celestials(self.mongo_coll, True)
#         generate_clans(self.mongo_coll, True)
#
#         generate_agents(self.mongo_coll, True)
#         #Initial Popn
#         self.assertEqual(self.mongo_coll.find({'_type':'agent'}).count(),
#                          world_doc['universeInfo']['initPopn']*world_doc['universeInfo']['numClans'])
#
#         #Diversity
#         clan = self.mongo_coll.find_one({'_type':'clan'})
#         clanAgents = list(self.mongo_coll.find({'_type':'agent', 'clanId':clan['_id']}))
#         explorers = [i for i in clanAgents if i['agentType'] == 0]
#         self.assertEqual(len(explorers),
#                          world_doc['universeInfo']['agentTypeMix'][0]/100.0*world_doc['universeInfo']['initPopn'])
#         harvestors = [i for i in clanAgents if i['agentType'] == 1]
#         self.assertEqual(len(harvestors),
#                          world_doc['universeInfo']['agentTypeMix'][1]/100.0*world_doc['universeInfo']['initPopn'])
#         traders = [i for i in clanAgents if i['agentType'] == 2]
#         self.assertEqual(len(traders),
#                          world_doc['universeInfo']['agentTypeMix'][2]/100.0*world_doc['universeInfo']['initPopn'])
#         soldiers = [i for i in clanAgents if i['agentType'] == 3]
#         self.assertEqual(len(soldiers),
#                          world_doc['universeInfo']['agentTypeMix'][3]/100.0*world_doc['universeInfo']['initPopn'])

    #ENVIRONMENT.SENSING
    def testClosestStar(self):
        pos = [0.0, 0.0, 0.0]
        coords = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0],
                  [10.0, 10.0, 0.0], [20.0, 20.0, 0.0]]

        chk = closest_star(pos, coords)
        self.assertEqual(chk, coords[0])

    #AGENT ACTIONS
    def testStarJump(self):
        '''
        Agent Jump between systems
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = {'position':[0.0, 0.0, 0.0],
                    'starId':1,
                    '_id':1}
        ex = gen_explorer(world_doc, clan_doc)
        ex['actyData']['tgtSys'] = 1
        star_jump(ex)
        self.assertEqual(ex['starId'], 1)
        self.assertEqual(ex['actyData']['complete'], True)

    def testSetOutboundStar(self):
        '''
        Set outbound star
        '''
        generate_world(self.mongo_coll, True, True)
        generate_celestials(self.mongo_coll, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = {'position':[0.0, 0.0, 0.0],
                    'starId':1,
                    '_id':1}
        ex = gen_explorer(world_doc, clan_doc)
        chkStar = self.mongo_coll.find({'_type':'star'}).next()
        ex['starId'] = chkStar['_id']
        set_outbound_star(ex, self.mongo_coll)
        self.assertEqual(ex['destination'], chkStar['position'])


    def testNumpifyAgent(self):
        '''
        Doc arrays to numpy
        '''
        ex = {'destination':[0.0, 0.0, 0.0],
              'position':[10.0, 10.0, 10.0],
              'velocity':[0.0, 0.0, 0.0]}
        numpify_agent(ex)
        self.assertEqual(isinstance(ex['destination'], type(np.array([1,2,3]))), True)

    def testDeNumpifyAgent(self):
        '''
        Doc arrays to numpy
        '''
        ex = {'destination':np.array([0.0, 0.0, 0.0]),
              'position':np.array([10.0, 10.0, 10.0]),
              'velocity':np.array([0.0, 0.0, 0.0])}
        de_numpyify_agent(ex)
        self.assertEqual(isinstance(ex['destination'], type([1,2,3])), True)


    def testSystemMove(self):
        '''
        Move Agent a bit in the system
        '''
        generate_world(self.mongo_coll, True, True)
        sysAgents = [{'_id':1, 'coords':[[0.0, 0.0, 0.0]]}, {'_id':2, 'coords':[[10.0, 10.0, 10.0]]}]
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = {'position':[0.0, 0.0, 0.0],
                    'starId':1,
                    '_id':1}
        ex = gen_explorer(world_doc, clan_doc)
        ex['_id'] = 1
        ex['destination'] = [10.0, 10.0, 10.0]
        numpify_agent(ex)
        chkDist1 = np.linalg.norm(ex['destination']-ex['position'])
        system_move(ex, sysAgents, self.mongo_coll)
        chkDist2 = np.linalg.norm(ex['destination']-ex['position'])
        #Did it move closer?
        self.assertGreater(chkDist1, chkDist2)
        #Check arrival flags
        ex['vis'] = np.linalg.norm(ex['destination']-ex['position'])+0.1
        system_move(ex, sysAgents, self.mongo_coll)
        #Did it arrive?
        self.assertEqual(list(ex['destination']), list(ex['position']))
        self.assertEqual(ex['actyData']['complete'], True)

    def testAgeKill(self):
        '''
        Test if we can kill an agent by age
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = {'position':[0.0, 0.0, 0.0],
                    'starId':1,
                    '_id':1}
        ex = gen_explorer(world_doc, clan_doc)
        chk = age_kill(ex, world_doc['universeInfo']['maxAge'])
        self.assertEqual(chk, False)
        ex['epoch'] = 600
        chk = age_kill(ex, world_doc['universeInfo']['maxAge'])
        self.assertEqual(chk, True)




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()