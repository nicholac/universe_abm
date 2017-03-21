'''
Created on 21 Jan 2017

@author: dusted-ipro
'''

import os, sys
from time import sleep
# Ensure paths then use . package notation and __init__ files.
this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if this_dir not in sys.path:
    sys.path.append(this_dir)
from time import time


#Externals
from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId


#Internals
from environment.processing import process_agent, process_genetics
from environment.generate import generate_world, \
                                    generate_celestials, \
                                    generate_clans, \
                                    generate_agents


def run(numSteps, mongo_coll, master):
    '''
    Run the world
    '''
    if master == True:
        print 'Running as Master...'
    else:
        print 'Running as Slave...'
    step = 0
    sysProcCnt = 0
    while True:
        start = time()
        #print 'Systems processed: {}'.format(sysProcCnt)
        step+=1
        #Get the current processing epoch
        epoch = mongo_coll.find({'_type':'world'}, {'epoch':1}).next()['epoch']
        #Pop a system
        try:
            sys = mongo_coll.find_one_and_update({'_type':'star','epoch':epoch-1,'status':'waiting'},
                                                {'$set':{'status':'processing'}},
                                                return_document=ReturnDocument.AFTER)
            status = list(mongo_coll.aggregate([{'$match':{'_type':'star'}},
                                                    {'$group':{'_id':'null', 'status':{'$push':'$status'}}}]))
            #Stop if there are no more systems to process this epoch
            if not sys:
                raise StopIteration
        except StopIteration:
            #All Systems and agents processed for this epoch
            if master == True:
                print 'Master Processing Epoch End...'
                #Run the agent reproduction routines
                print 'Running Genetics...'
                process_genetics(mongo_coll)
                print 'Done Genetics'
                #Increment the world
                print 'Increment world, epoch: {}'.format(epoch)
                epochTime = time()-start
                #Record the population at this epoch
                mongo_coll.find_one_and_update({'_type':'world'},
                                              {'$set':{'procTimePerEpoch':epochTime}})
                #Record the population at this epoch
                cnt = mongo_coll.find({'_type':'agent'}).count()
                mongo_coll.find_one_and_update({'_type':'world'},
                                              {'$push':{'popnOverTime':{'epoch_{}'.format(epoch):cnt}}})
                sysProcCnt = 0
                #No more systems to process in this epoch - incrememnt world (any node can do this)
                mongo_coll.find_and_modify({'_type':'world'}, {"$inc": {'epoch':1}})
                mongo_coll.update_many({'_type':'star'}, {"$set": {'status':'waiting'}})
                #List of status data about systems
                status = list(mongo_coll.aggregate([{'$match':{'_type':'star'}},
                                                        {'$group':{'_id':'null', 'status':{'$push':'$status'}}}]))
                #print 'Star Sys Status: {}'.format(status)
                continue
            else:
                #Client - wait for others
                print 'Slave Waiting for Epoch Finish...'
                sleep(0.5)
                continue
        i = 0
        cnt = mongo_coll.count({'_type':'agent', 'starId':sys['_id']})
        if cnt > 0:
            agents = list(mongo_coll.find({'_type':'agent', 'starId':sys['_id']}))
            '''
            #Check the agent actys
            actys = mongo_coll.aggregate([{'$match':{'_type':'agent'}},
                                                    {'$group':{'_id':'null', 'actyGroup':{'$push':'$actyGroup'},
                                                               'actySeq':{'$push':'$actyData.actyId'},
                                                               'status':{'$push':'$actyData.complete'}}}])

            print 'Agent Status: {}'.format(actys.next()['actySeq'])
            '''
            #print 'Agents in Sys: {}'.format(len(agents))

            #Get all the initial state agent coordinates
            sysAgents = list(mongo_coll.aggregate([{'$match':{'_type':'agent', 'starId':sys['_id']}},
                                                {'$group':{'_id':'$_id', 'coords':{'$push':'$position'}}}]))
            #print 'Got Agent Coords'
            for agent in agents:
                process_agent(agent, sysAgents, mongo_coll)
            #Push all the agents back up to server
            for agent in agents:
                mongo_coll.update({'_id':agent['_id']}, agent)
        else:
            #Skipped System
            pass
        #print 'Average Time per sys run: {}'.format(avgTimeExt)
        #Update the system epoch - everything else is seperate docs
        mongo_coll.find_and_modify({'_type':'star', '_id':sys['_id']},
                                  {"$inc": {'epoch':1}, '$set':{'status':'complete'}})
        sysProcCnt+=1
    print 'Exiting Run'


if __name__ == '__main__':
    #Connect to collection
    cli = MongoClient()
    db = cli.universeabm
    universe_coll = db.universe

    master = True
    reset = True

    if master == True and reset == True:
        generate_world(universe_coll, True)
        generate_celestials(universe_coll, True)
        generate_clans(universe_coll, True)
        generate_agents(universe_coll, True)


    run(10, universe_coll, master)

    cli.close()
    print 'Done'

    '''
    NEXT: keep working through config data to world doc - loads JSON, generate as required, then load to MONGO
    NEXT: Templates will just be config data skew for mongo
    NEXT: Need to remember we want the config data to be a one-stop-shop for altering world
    NEXT: The algorithm converges now, and fast - for explorers
    NEXT:  Get the explorers doing something - watch resourceknowledge bug
    NEXT: Graph other stuff, like % fit for all types, fitness scores
    Start cleaning it up - seems like it may actually be working
    Break out configuration into a file to make it more easily tweaked
    Write some damn unit tests
    Make the new Mongo stuff the main routine
    Give it some system args for the cluster master / slave running
    Setup a run env on Digital Ocean
    Try more agents
    Try more clans
    Automatically limit population based on the resources available - pop/resources = less chance of reprod
    Increase mutation as a function of low popn - so we have more chance of the right genes appearing
    '''







