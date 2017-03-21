'''
Created on 3 Mar 2017

@author: dusted-ipro
'''

import os
import sys
import logging
#from pymongo import MongoClient
import json
from pymongo import MongoClient, ReturnDocument

from flask import Flask, render_template, jsonify, g, request, Response, abort

#Internal
from genetics.algorithms import fitness_sametype,fitness_scoring_sametype

# Ensure paths then use . package notation and __init__ files.
this_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if this_dir not in sys.path:
    sys.path.append(this_dir)

# Basic lagging configuration
logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.INFO, filename=os.path.dirname(os.path.abspath(__file__))+'/abm_api.log')
logger = logging.getLogger(__name__)

#Connect to collection
cli = MongoClient()
db = cli.universeabm
agentColl = db.agents
celestialsColl = db.celestials
universeColl = db.universe

# Flask App configuration
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = ''
app.name = 'universeabm'
print app.name

@app.route('/popn_type')
def popn_type():
    #Get from Mongo
    agent_types = {0:'Explorer',
                    1:'Trader',
                    2:'Harvestor',
                    3:'Soldier'}
    types = list(universeColl.aggregate([{'$match':{'_type':'agent'}},{'$group':{'_id':'null', 'agentType':{"$addToSet": "$agentType"}}}]))
    counts = {'cols':[]}
    for i in types:
        cnt = universeColl.find({'_type':'agent', 'agentType':i['agentType'][0]}).count()
        counts['cols'].append([agent_types[i['agentType'][0]], cnt])
    return Response(json.dumps(counts),  mimetype='application/json')

@app.route('/popn_fitness')
def popn_fitness():
    #Get from Mongo
    counts = {'cols':[]}
    fit = universeColl.find({'_type':'agent', 'parent':False,
                             'epoch':{'$lte':300},
                             'epoch':{'$gte':50}}).count()
    unfit = universeColl.find({'_type':'agent', 'parent':True}).count()
    unfit += universeColl.find({'_type':'agent', 'epoch':{'$gte':300}}).count()
    unfit += universeColl.find({'_type':'agent', 'epoch':{'$lte':50}}).count()
    counts['cols'].append(['Fit', fit])
    counts['cols'].append(['Unfit', unfit])
    return Response(json.dumps(counts),  mimetype='application/json')

@app.route('/popn_parent')
def popn_parents():
    #Get from Mongo
    counts = {'cols':[]}
    parent = universeColl.find({'_type':'agent', 'parent':True}).count()
    notParent = universeColl.find({'_type':'agent', 'parent':False}).count()
    counts['cols'].append(['Parent', parent])
    counts['cols'].append(['Not Parent', notParent])
    return Response(json.dumps(counts),  mimetype='application/json')

@app.route('/popn_ages')
def popn_ages():
    #Get from Mongo
    counts = {'cols':[]}
    ages = list(universeColl.aggregate([{'$match':{'_type':'agent'}},
                                         {'$group':{'_id':'null', 'ages':{"$addToSet": "$generation"}}}]))
    for i in ages[0]['ages']:
        cnt = universeColl.find({'_type':'agent', 'generation':i}).count()
        counts['cols'].append(['generation_{}'.format(i), cnt])
    return Response(json.dumps(counts),  mimetype='application/json')


@app.route('/global_stats')
def global_stats():
    #Get from Mongo
    worldData = list(universeColl.find({'_type':'world'}, {'epoch':1, 'procTimePerEpoch':1}))
    resKnowledge = list(universeColl.aggregate([{'$match':{'_type':'clan'}},
                                                {'$project':{'num':{"$size": "$resourceKnowledge"}}}]))
    #l = (uc.aggregate([{'$match':{'_type':'clan'}}, {'$unwind':'$resourceKnowledge'}, {'$project':{'num':{'$size':'$resourceKnowledge.planets'}}}]))
    #list(uc.aggregate([{'$match':{'_type':'clan'}}, {'$unwind':'$resourceKnowledge'}, {'$project':{'_id':0, 'num':{'$gt':[{'$size':'$resourceKnowledge.planets'}, 0]}}}, {'$project':{'fin':{'$cond':['$num', 1, 0]}}}]))
    #Think this is finally count of received and tasked:
    #list(uc.aggregate([{'$match':{'_type':'clan'}}, {'$unwind':'$resourceKnowledge'}, {'$project':{'_id':'null', 'num':{'$gt':[{'$size':'$resourceKnowledge.planets'}, 0]}}}, {'$project':{'fin':{'$cond':['$num', 1, 0]}}}, {'$group':{'_id':{'cnt':'$fin'}, 'count':{'$sum':1}}}]))
    totalPop = universeColl.find({'_type':'agent'}).count()

    out = {'resKnowledge':resKnowledge[0]['num'],
           'totalPop':totalPop,
           'epoch':worldData[0]['epoch'],
           'procTimePerEpoch':worldData[0]['procTimePerEpoch']}
    return Response(json.dumps(out),  mimetype='application/json')


@app.route('/generation_fitness')
def generation_fitness():
    #Get from Mongo
    out = {'cols':[], 'bars':[]}
    x = ['x']
    y = ['% passed fit']
    yPopAlive = ['Total Gen Pop Alive']
    yPopDead = ['Total Gen Pop Dead']
    gensDict = {}
    agents = list(universeColl.find({'_type':'agent'}))
    world_doc = list(universeColl.find({'_type':'world'}))
    for agent in agents:
        if agent['generation'] not in gensDict.keys():
            gensDict[agent['generation']] = {'fit':0, 'unfit':0, 'totalAlive':0, 'totalDead':0}
        fitness_chk = fitness_sametype(agent, fitness_scoring_sametype(agent,world_doc))
        if fitness_chk['canReprod'] != True:
            #Not fit for explorer
            gensDict[agent['generation']]['unfit']+=1
        else:
            gensDict[agent['generation']]['fit']+=1
        #Add Gen count
        gensDict[agent['generation']]['totalAlive']+=1

    deadAgents = list(universeColl.find({'_type':'deadAgent'}))
    for agent in deadAgents:
        if agent['generation'] not in gensDict.keys():
            gensDict[agent['generation']] = {'fit':0, 'unfit':0, 'totalAlive':0, 'totalDead':0}
        fitness_chk = fitness_sametype(agent, fitness_scoring_sametype(agent,world_doc))
        if fitness_chk['canReprod'] != True:
            #Not fit for anything
            gensDict[agent['generation']]['unfit']+=1
        else:
            gensDict[agent['generation']]['fit']+=1
        #Add Gen count
        gensDict[agent['generation']]['totalDead']+=1

    #Parse for graph
    for gen in gensDict.keys():
        #Line Graph
        x.append('Gen:{}'.format(gen))
        y.append(float(gensDict[gen]['fit'])/(float(gensDict[gen]['fit'])+float(gensDict[gen]['unfit']))*100.0)
        #Bar Graph
        yPopAlive.append(gensDict[gen]['totalAlive'])
        yPopDead.append(gensDict[gen]['totalDead'])
    print x
    print y
    print yPopAlive
    print yPopDead
    out['cols'] = [x, y]
    out['bars'] = [x, yPopAlive, yPopDead]
    return Response(json.dumps(out),  mimetype='application/json')



@app.route('/universe')
def hashPath():
    """ normal http request to a serve up the page """
    return render_template('index.html')


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8080)


