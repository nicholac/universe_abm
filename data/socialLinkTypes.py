'''
Created on 25 Dec 2016

@author: dusted-ipro

Contains callable data structures for all social link types

'''

def allLinks():
    '''
    All Link Types (Agent <-> Agent, Agent<-->Clan, Clan<-->Clan)
    ::returns Dict All types
    '''
    return {0:'clan', #In same clan
            1:'social', #Have interacted socially
            2:'family'} #Same family
