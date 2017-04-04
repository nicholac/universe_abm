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

from agents.explorer import get_starsys, deposit_knowledge, visit_planets

from genetics.algorithms import crossover, reproduce, fitness_sametype, mutation, fitness_scoring_sametype


class Test(unittest.TestCase):


    def setUp(self):
        cli = MongoClient()
        db = cli.universeabm
        self.mongo_coll = db.universe


    def tearDown(self):
        self.mongo_coll.drop()



#     #GENERATE - WORKING

    def testGenerateWorld(self):
        '''
        Generate the world doc
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        self.assertNotEqual(world_doc, None)


    def testGenerateCelestials(self):
        '''
        Generate the world doc
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)

        #Count Stars
        cnt = self.mongo_coll.find({'_type':'star'}).count()
        self.assertEqual(cnt, world_doc['universeInfo']['numStars'])

        print 'Testing all star distances...'
        #Distance between stars & Planets reasonable?
        stars = list(self.mongo_coll.find({'_type':'star'}))
        starDist = []
        for i in stars:
            for j in stars:
                if i['_id'] == j['_id']:
                    continue
                starDist.append(distance.pdist([i['position'], j['position']])[0])


        for star in stars:
            planets = list(self.mongo_coll.find({'_type':'planet', 'starId':star['_id']}))
            planetDist = []
            for i in planets:
                for j in planets:
                    planetDist.append(distance.pdist([i['position'], j['position']])[0])
            #Check this solar systems planets are all closer to each other than the distances bwtween stars
            self.assertEqual(np.max(planetDist) < np.min(starDist), True)

        print 'Done star distances'

        #TODO:Are the planets starId's actually the closest stars?

    def testGenerateClans(self):
        '''
        Testing clan generation
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)

        generate_clans(self.mongo_coll, True)
        #Right number of clans
        self.assertEqual(self.mongo_coll.find({'_type':'clan'}).count(),
                         world_doc['universeInfo']['numClans'])
        #Clan homes are all different
        clanStars = list(self.mongo_coll.find({'_type':'clan'}, {'_id':0, 'starId':1}))
        for i in clanStars:
            self.assertEqual(clanStars.count(i), 1)

    def testGenExplorer(self):
        generate_world(self.mongo_coll, True, True)
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]

        #Check the map generator works
        func = agent_generate_map(0)
        self.assertEqual(isinstance(func, type(gen_explorer)), True)
        ex = func(world_doc, clan_doc)
        #Check we get a doc
        self.assertNotEqual(ex['agentType'], None)
        self.assertEqual(ex['agentType'], 0)

    def testGenHarvestor(self):
        generate_world(self.mongo_coll, True, True)
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]

        #Check the map generator works
        func = agent_generate_map(1)
        self.assertEqual(isinstance(func, type(gen_harvestor)), True)
        ex = func(world_doc, clan_doc)
        #Check we get a doc
        self.assertNotEqual(ex['agentType'], None)
        self.assertEqual(ex['agentType'], 1)

    def testGenTrader(self):
        generate_world(self.mongo_coll, True, True)
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]

        #Check the map generator works
        func = agent_generate_map(2)
        self.assertEqual(isinstance(func, type(gen_trader)), True)
        ex = func(world_doc, clan_doc)
        #Check we get a doc
        self.assertNotEqual(ex['agentType'], None)
        self.assertEqual(ex['agentType'], 2)

    def testGenSoldier(self):
        generate_world(self.mongo_coll, True, True)
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        clan_doc = list(self.mongo_coll.find({'_type':'clan'}))[0]

        #Check the map generator works
        func = agent_generate_map(3)
        self.assertEqual(isinstance(func, type(gen_soldier)), True)
        ex = func(world_doc, clan_doc)
        #Check we get a doc
        self.assertNotEqual(ex['agentType'], None)
        self.assertEqual(ex['agentType'], 3)


    def testGenerateAgents(self):
        '''
        Testing Agent generation
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)

        generate_agents(self.mongo_coll, True)
        #Initial Popn
        self.assertEqual(self.mongo_coll.find({'_type':'agent'}).count(),
                         world_doc['universeInfo']['initPopn']*world_doc['universeInfo']['numClans'])

        #Diversity
        clan = self.mongo_coll.find_one({'_type':'clan'})
        clanAgents = list(self.mongo_coll.find({'_type':'agent', 'clanId':clan['_id']}))
        explorers = [i for i in clanAgents if i['agentType'] == 0]
        self.assertEqual(len(explorers),
                         world_doc['universeInfo']['agentTypeMix'][0]/100.0*world_doc['universeInfo']['initPopn'])
        harvestors = [i for i in clanAgents if i['agentType'] == 1]
        self.assertEqual(len(harvestors),
                         world_doc['universeInfo']['agentTypeMix'][1]/100.0*world_doc['universeInfo']['initPopn'])
        traders = [i for i in clanAgents if i['agentType'] == 2]
        self.assertEqual(len(traders),
                         world_doc['universeInfo']['agentTypeMix'][2]/100.0*world_doc['universeInfo']['initPopn'])
        soldiers = [i for i in clanAgents if i['agentType'] == 3]
        self.assertEqual(len(soldiers),
                         world_doc['universeInfo']['agentTypeMix'][3]/100.0*world_doc['universeInfo']['initPopn'])

    #ENVIRONMENT.SENSING
    def testClosestStar(self):
        pos = [0.0, 0.0, 0.0]
        coords = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0],
                  [10.0, 10.0, 0.0], [20.0, 20.0, 0.0]]

        chk = closest_star(pos, coords)
        self.assertEqual(chk, coords[0])

    #BASE AGENT ACTIONS
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


    #EXPLORER AGENT ACTIONS
    def testExplorerGetStarSys(self):
        '''
        Get Explorer next star system to investigate
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)

        #Get an Agent
        agent_doc = self.mongo_coll.find_one({'_type':'agent'})
        clan = self.mongo_coll.find({'_id':agent_doc['clanId']}, {'starId':1}).next()
        get_starsys(agent_doc, None, self.mongo_coll)

        #Check initial destination - our clans star
        star = self.mongo_coll.find({'_id':clan['starId']}, {'position':1}).next()
        self.assertListEqual(agent_doc['destination'], star['position'])

        #Check other set vars
        self.assertEqual(agent_doc['actyData']['tgtSys'], star['_id'])
        self.assertListEqual(agent_doc['actyData']['tgtStarCoords'], star['position'])
        #Check clan doc got populated correctly
        clan = self.mongo_coll.find({'_id':agent_doc['clanId']}, {'resourceKnowledge':1}).next()
        self.assertListEqual(clan['resourceKnowledge'], [{'starId':star['_id'], 'planets':[]}])
        self.assertEqual(agent_doc['actyData']['complete'],  True)
        #Check no more planets to explore
        fullKnowledge = []
        stars = list(self.mongo_coll.find({'_type':'star'}))
        for star in stars:
            fullKnowledge.append({'starId':star['_id'], 'planets':[]})
        self.mongo_coll.find_and_modify({'_id':agent_doc['clanId']},
                                        {'$set':{'resourceKnowledge':fullKnowledge}})
        #Make sure its arrived in mongo
        clan = self.mongo_coll.find({'_id':agent_doc['clanId']}, {'resourceKnowledge':1,
                                                                  'starCatalogue':1}).next()
        self.assertListEqual(clan['resourceKnowledge'], fullKnowledge)
        get_starsys(agent_doc, None, self.mongo_coll)
        self.assertDictEqual(agent_doc['actyData'], {'actyId': 0, 'actyIdx': 0, 'complete': True})
        self.assertEqual(agent_doc['actyData']['actyId'], 0)

    #EXPLORER AGENT ACTIONS
    def testExplorerDepositKnowledge(self):
        '''
        Deposit knowledge at the explorer clan
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent
        agent_doc = self.mongo_coll.find_one({'_type':'agent'})
        #Get a star to explore
        get_starsys(agent_doc, None, self.mongo_coll)
        #Get a planet
        planet = self.mongo_coll.find_one({'_type':'planet', 'starId':agent_doc['actyData']['tgtSys']})
        #Push into agent_doc (simulate explored)
        agent_doc['actyData']['planets'] = [{'_id':planet['_id'],
                                             'visited':True,
                                              'energyStore':0.0,
                                              'rawMatStore':0.1}]
        #Make sure its arrived in mongo
        clan = self.mongo_coll.find({'_id':agent_doc['clanId']}, {'resourceKnowledge':1,
                                                                  'starCatalogue':1}).next()
        self.assertListEqual(clan['resourceKnowledge'], [{u'starId': planet['starId'], u'planets': []}])
        #Simulated job data
        agent_doc['actyData']['tgtStarCoords'] = ''
        agent_doc['actyData']['tgtCoords'] = ''
        agent_doc['actyData']['planetTgtId'] = ''
        agent_doc['actyData']['complete'] = True
        #Dump the knowledge
        deposit_knowledge(agent_doc, None, self.mongo_coll)
        #Check clan resource knowledge
        clan = self.mongo_coll.find({'_id':agent_doc['clanId']}, {'resourceKnowledge':1}).next()
        self.assertEqual({'starId':planet['starId'],
                          'planets':[{'_id':planet['_id'],'visited':True,'energyStore':0.0,'rawMatStore':0.1}]} in clan['resourceKnowledge'], True)

    def testExplorerVisitPlanets(self):
        '''
        Explorer visit all planets in star sys
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent
        agent_doc = self.mongo_coll.find_one({'_type':'agent'})
        sys_agent_coords = [{'_id':1, 'coords':[[0.0, 0.0, 0.0]]},
                             {'_id':2, 'coords':[[10.0, 10.0, 10.0]]},
                             {'_id':agent_doc['_id'], 'coords':agent_doc['position']}]
        #Move away from the first planet
        agent_doc['position'] = [i+10.0 for i in agent_doc['position']]
        visit_planets(agent_doc, sys_agent_coords, self.mongo_coll)
        #Check we have a valid target adn the number of planets is correct
        planets = list(self.mongo_coll.find({'_type':'planet',
                                             'starId':agent_doc['starId']}))
        self.assertEqual(len(planets), len(agent_doc['actyData']['planets']))
        self.assertEqual(planets[0]['_id'], agent_doc['actyData']['planets'][0]['_id'])
        self.assertEqual(agent_doc['actyData']['planets'][0]['visited'], False)
        #Move agent to the planet - check if it gets visited
        agent_doc['position'] = planets[0]['position']
        visit_planets(agent_doc, sys_agent_coords, self.mongo_coll)
        self.assertEqual(agent_doc['actyData']['planets'][0]['visited'], True)
        self.assertEqual(planets[0]['energyStore'], agent_doc['actyData']['planets'][0]['energyStore'])
        self.assertEqual(planets[0]['rawMatStore'], agent_doc['actyData']['planets'][0]['rawMatStore'])
        #Try collecting all the system data
        cnt = 0
        print 'Visiting Planets test'
        while agent_doc['actyData']['complete'] == False:
            visit_planets(agent_doc, sys_agent_coords, self.mongo_coll)
            cnt+=1
        print 'Num turns to collect a system: ', cnt, len(agent_doc['actyData']['planets'])
        #Check we are set to go home
        clan_doc = self.mongo_coll.find({'clanId':agent_doc['clanId']}).next()
        self.assertEqual(agent_doc['actyData']['tgtCoords'], clan_doc['position'])
        #Check all the data
        for idx, p in enumerate(planets):
            self.assertEqual(p['rawMatStore'], agent_doc['actyData']['planets'][idx]['rawMatStore'])
            self.assertEqual(p['energyStore'], agent_doc['actyData']['planets'][idx]['energyStore'])


#GENETICS

    def testCrossover(self):
        '''
        Genetics - crossover two agents
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent
        agents = list(self.mongo_coll.find({'_type':'agent'}))
        agent1_doc = agents[0]
        agent2_doc = agents[1]
        split_pos = 1
        child_1, child_2 = crossover(agent1_doc, agent2_doc,
                                     world_doc['gaInfo']['crossoverTraits'], split_pos)
        #Check the children - chromosomes
        self.assertEqual(child_1['vis'], agent2_doc['vis'])
        self.assertEqual(child_1['velMag'], agent1_doc['velMag'])
        self.assertEqual(child_1['defence'], agent1_doc['defence'])
        self.assertEqual(child_1['offence'], agent1_doc['offence'])
        self.assertEqual(child_2['vis'], agent1_doc['vis'])
        self.assertEqual(child_2['velMag'], agent2_doc['velMag'])
        self.assertEqual(child_2['defence'], agent2_doc['defence'])
        self.assertEqual(child_2['offence'], agent2_doc['offence'])

    def testMutation(self):
        '''
        Genetic mutation
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent
        agent_doc = self.mongo_coll.find_one({'_type':'agent'})
        #Record traits before
        recTraits = []
        for trait in world_doc['gaInfo']['crossoverTraits']:
            recTraits.append(agent_doc[trait])
        mutation(agent_doc, world_doc['gaInfo']['crossoverTraits'],
                 world_doc['gaInfo']['mutationBounds']['min'],
                 world_doc['gaInfo']['mutationBounds']['max'])
        #Check the traits have changed
        for idx, trait in enumerate(world_doc['gaInfo']['crossoverTraits']):
            self.assertEqual(agent_doc[trait] >= (world_doc['gaInfo']['mutationBounds']['min']*recTraits[idx])+recTraits[idx], True)
            self.assertEqual(agent_doc[trait] <= (world_doc['gaInfo']['mutationBounds']['max']*recTraits[idx])+recTraits[idx], True)

    def testFitnessSameType(self):
        '''
        Testing of fitness for same agent type
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent - explorer
        #TODO: replicate for all other agents
        agent_doc = self.mongo_coll.find_one({'_type':'agent', 'agentType':0})
        #Make sure its fit
        for trait in world_doc['gaInfo']['crossoverTraits']:
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'gte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['val']+1.0
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'lte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]-1.0
        #Generate the fitness template
        ft = fitness_scoring_sametype(agent_doc, world_doc)
        #Do the fitness check
        chk = fitness_sametype(agent_doc, ft)
        self.assertEqual(chk['canReprod'], True)
        #Try a fitter agent
        for trait in world_doc['gaInfo']['crossoverTraits']:
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'gte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['val']+10.0
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'lte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['val']-10.0
        #Do the fitness check
        chk2 = fitness_sametype(agent_doc, ft)
        self.assertEqual(chk2['canReprod'], True)
        #Check to make sure the fitness score is higher
        self.assertGreater(chk2['fitScore'], chk['fitScore'])
        #Check a failing agent
        for trait in world_doc['gaInfo']['crossoverTraits']:
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'gte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['val']-1.0
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'lte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]+1.0

        #Do the fitness check
        chk2 = fitness_sametype(agent_doc, ft)
        self.assertEqual(chk2['canReprod'], False)

    def testReproduce(self):
        '''
        Top-level reproduction func
        '''
        generate_world(self.mongo_coll, True, True)
        world_doc = self.mongo_coll.find({'_type':'world'}).next()
        generate_celestials(self.mongo_coll, True)
        generate_clans(self.mongo_coll, True)
        generate_agents(self.mongo_coll, True)
        #Get an Agent - explorer
        #TODO: replicate for all other agents
        agent_doc = self.mongo_coll.find_one({'_type':'agent', 'agentType':0})
        #Check the fitness bail - it should be too young
        self.assertEqual(reproduce(agent_doc, self.mongo_coll, world_doc), False)
        #Make the agent fit to reproduce
        agent_doc['epoch'] = world_doc['universeInfo']['minAgeReprod']+1
        for trait in world_doc['gaInfo']['crossoverTraits']:
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'gte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['val']+10.0
            if world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]['operator'] == 'lte':
                agent_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent_doc['agentType'])][trait]-10.0

        #Check population bail out - agent should be changed to ready for reprod, but not actually spawned children
        world_doc['universeInfo']['maxPopn'] = world_doc['universeInfo']['initPopn']-10
        self.assertEqual(reproduce(agent_doc, self.mongo_coll, world_doc), False)
        #Check the agents changed in mongo
        agent_doc = self.mongo_coll.find({'_id':agent_doc['_id']}).next()
        self.assertEqual(agent_doc['canReproduce'], True)

        #Reset the population
        world_doc['universeInfo']['maxPopn'] = world_doc['universeInfo']['initPopn']+20
        #Create a partner thats fit to reproduce
        agent2_doc = self.mongo_coll.find({'_type':'agent', '_id':{"$ne":agent_doc['_id']}}).next()
        #Make the agent fit to reproduce
        agent2_doc['epoch'] = world_doc['universeInfo']['minAgeReprod']+1
        for trait in world_doc['gaInfo']['crossoverTraits']:
            if world_doc['gaInfo']['fitnessReqs'][str(agent2_doc['agentType'])][trait]['operator'] == 'gte':
                agent2_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent2_doc['agentType'])][trait]['val']+10.0
            if world_doc['gaInfo']['fitnessReqs'][str(agent2_doc['agentType'])][trait]['operator'] == 'lte':
                agent2_doc[trait] = world_doc['gaInfo']['fitnessReqs'][str(agent2_doc['agentType'])][trait]-10.0
        #Insert
        self.mongo_coll.update({'_id':agent2_doc['_id']}, agent2_doc)

        #Now try to reproduce these two agents
        self.assertEqual(reproduce(agent2_doc, self.mongo_coll, world_doc), True)
        #Do we have children in the DB?
        cnt = self.mongo_coll.find({'_type':'agent', 'generation':1}).count()
        self.assertEqual(cnt, 2)

        #TODO: If we run this for a while - does the general population fitness grow?
        #TODO: Write a global fitness retrieval function - to get fitness for a clan

# NEXT: Tests: All thats left is to write tests for the processing and engine!
# NEXT: Tests: Can also write some longer run tests for the genetics
# NEXT: API wont work at this stage - fix
# NEXT: Harvestor behaviour
# NEXT: Priority queues for explorers and harvestors
# NEXT: Clan Scoring - for learning


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()