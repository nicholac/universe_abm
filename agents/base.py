'''
Created on 24 Dec 2016

@author: dusted-ipro
'''

import numpy as np

#Internal
from environment.sensing import dist
from data.support_funcs import positive_probs_exp


def idle(agent_doc, sysAgents, mongo_coll):
    '''
    Idle Actions
    args = []
    '''
    agent_doc['activity'] = 0


def star_jump(agent_doc):
    '''
    Jump an agent between star systems
    - Just changes agent internal data - they agent is moved by world when it returns to the server
    '''
    #Hop System
    agent_doc['starId'] = agent_doc['actyData']['tgtSys']
    agent_doc['position'] = agent_doc['actyData']['tgtStarCoords']
    agent_doc['destination'] = agent_doc['actyData']['tgtCoords']
    agent_doc['actyData']['complete'] = True


def set_outbound_star(agent_doc, mongo_coll):
    '''
    Set an agents destination as the current system star
    (prep for swap between system move and star jump)
    NOTE: Requires the tgtStarId and tgtStarCoords in actyData to be set already - or the jump wont work
    '''
    agent_doc['destination'] = mongo_coll.find({'_id':agent_doc['starId']},
                                               {'position':1}).next()['position']



def system_move(agent_doc, sysAgents, mongo_coll):
    '''
    Move within a system toward a target
    If dist diff is less than a step at max velocity then just snap to the tgt for now
    '''
    #Get the current dist to dest
    d = dist(agent_doc['destination'], agent_doc['position'])
    time_step = mongo_coll.find({'_type':'world'}).next()['universeInfo']['timeStep']
    #Snap to destination instead of flying straight past
    if d < agent_doc['velMag']*time_step or d < agent_doc['vis']:
        agent_doc['position'] = agent_doc['destination']
        #Set activity complete
        agent_doc['actyData']['complete'] = True
        return
    #Set velocity vector
    diff = agent_doc['destination']-agent_doc['position']
    agent_doc['velocity'] = (diff/d)*agent_doc['velMag']
    #Move a step
    agent_doc['position']+=(agent_doc['velocity']*time_step)
    #Update local coord array
    agentIdx = [idx for idx, i in enumerate(sysAgents) if i['_id']==agent_doc['_id']][0]
    sysAgents[agentIdx]['coords'][0] = agent_doc['position']


def stop(agent_doc):
    '''
    Stop Moving
    '''
    agent_doc['velocity'] = [0.0, 0.0, 0.0]




def send_message(from_agent, to_agent, msg, mongo_coll):
    '''
    Send a message between agents within a system or between systems
    '''
    #Find if agent is in system
        #yes - alter doc in system list
        #no - find and update the remote doc


def numpify_agent(agent_doc):
    '''
    Convert agent data to numpy so we can do numpy ops
    '''
    agent_doc['destination'] = np.array(agent_doc['destination'])
    agent_doc['position'] = np.array(agent_doc['position'])


def de_numpyify_agent(agent_doc):
    '''
    Convert agent data back to pyton / bson serialisable for mongo
    '''
    agent_doc['destination'] = list(agent_doc['destination'])
    agent_doc['position'] = list(agent_doc['position'])
    agent_doc['velocity'] = list(agent_doc['velocity'])


def age_kill(agent_doc, max_age):
    '''
    Kill of agent if getting too old
    Probability weighted toward higher chance when older
    '''
    #Generate a distro so more chance of dying when older
    r = range(0, max_age, 50)
    chk = np.random.choice(r, p=positive_probs_exp(len(r)))
    return agent_doc['epoch'] > chk




