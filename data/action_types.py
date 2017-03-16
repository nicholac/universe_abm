'''
Created on 25 Dec 2016

@author: dusted-ipro

Contains callable data structures for all activities

These functions only ever take in <agent_doc, sysAgents, mongo_coll> as params

Activity Sequencing (each step sets the next)
Explorer Resource Search: Get Job, move out star, jump, move planets, move out star, return clan

'''
from itertools import cycle

from mongo_agents import base
from mongo_agents import explorer


def action_sequences():
    '''
    All agent Activity Sequences
    The seq numbers refer to all_actions below
    '''
    out = {0:{'agentType':'explorer',
              'actyGroups':{0:{'name':'idle',
                            'seq':[0]},
                            1:{'name':'exploreResources',
                            'seq':[5, 1, 2, 6, 1, 2, 1, 4]}
                         }

              },
           1:{'agentType':'all',
              'actyGroups':{0:{'name':'idle',
                            'seq':[0]}
                         }

              }
           }
    return out


def all_actions():
    '''
    All Action Types (Agent <-> Agent)
    Root keys are the activity Id's
    ::returns Dict All types
    '''
    return {0:{'name':'idle',
               'actyFunc':base.idle,
               'actyData':{}},
            1:{'name':'moveWithinSys',
               'actyFunc':base.system_move,
               'actyData':{}},
            2:{'name':'sysJump',
               'actyFunc':base.star_jump,
               'actyData':{'tgtCoords':[],
                           'tgtSys':0,
                           'tgtStarCoords':[]}},
            3:{'name':'checkResources',
               'actyFunc':None,
               'actyData':{}},
            4:{'name':'depositKnowledge',
               'actyFunc':explorer.deposit_knowledge,
               'actyData':{}},
            5:{'name':'getStarSys',
               'actyFunc':explorer.get_starsys,
               'actyData':{}},
            6:{'name':'visitPlanets',
               'actyFunc':explorer.visit_planets,
               'actyData':{}}
            }





