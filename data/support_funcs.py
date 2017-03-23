'''
Created on 25 Dec 2016

@author: dusted-ipro

Generic Support Functions
'''
import json
import os

import numpy as np

#CONFIGS
def load_config(master):
    '''
    Load Config JSON to dict
    ::param master boolean - running as master?
    '''
    try:
        if master == True:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'master.json')
        else:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'slave.json')
        fp = open(config_file, 'r')
        if fp:
            config_data = json.load(fp)
        else:
            raise Exception
        return config_data
    except Exception, err:
        print 'Config load failed: {}'.format(err)
        return None


def save_config(master, config_data):
    '''
    Save Config dict to JSON
    ::param master boolean - running as master?
    ::param config_data dict configuration data
    '''
    try:
        if master == True:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'master.json')
        else:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'slave.json')
        fp = open(config_file, 'r')
        if fp:
            config_data = json.dump(config_data, fp)
        else:
            raise Exception
        return True
    except:
        return None



#WORLD UNITS
#UNITS - Astro Units to Light Years
def au2Ly(au):
    '''
    Convert given AU to light years
    '''
    return au*(1.538*10e-5)

def ly2Au(ly):
    '''
    Convert given light years to AU
    '''
    return ly/(1.538*10e-5)

#WORLD RATES
def gen_harvestor_caps(raw_min, raw_max,
                       nrg_min, nrg_max,
                       hg_min, hg_max):
    '''
    Randomly generate capacities for harvestor
    Tons
    '''
    return (np.random.choice(np.linspace(raw_min, raw_max)), #Raw Mat Cap
            np.random.choice(np.linspace(nrg_min, nrg_max)), #Energy Cap
            np.random.choice(np.linspace(hg_min, hg_max))) #HG Cap

def gen_harvestor_rates(nrg_harv_min, nrg_harv_max,
                        raw_harv_min, raw_harv_max,
                        hg_min, hg_max,
                        ngr_min, nrg_max):
    '''
    Randomly generate harvest & consume rates for harvestor
    Tons per tick
    '''
    return (np.random.choice(np.linspace(nrg_harv_min, nrg_harv_max)), #Energy Harvest
            np.random.choice(np.linspace(raw_harv_min, raw_harv_max)), #Raw Mat Harvest
            np.random.choice(np.linspace(hg_min, hg_max)), #HG Consume
            np.random.choice(np.linspace(ngr_min, nrg_max))) #Energy Consume

def gen_clan_rates(clan_min, clan_max):
    '''
    Randomly generate clan global consumption rates
    Tones per tick
    '''
    return (np.random.choice(np.linspace(clan_min, clan_max)), 0.0)

def gen_agent_vel_mag(vel_min, vel_max):
    '''
    Randomly generate an agent max velocity magnitude
    Max velocities - init randomly so genetics pass the trait along
    '''
    return np.random.choice(np.linspace(au2Ly(vel_min), au2Ly(vel_max)))


#PROBABILITY GENERATION
def positive_probs_lin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward higher numbers
    '''
    return np.arange(numSamps)/np.sum(np.arange(numSamps))


def negative_probs_lin(numSamps):
    '''
    Create a linear (y=x) distribution weighted toward lower numbers
    '''
    return positive_probs_lin(numSamps)[::-1]


def positive_probs_pow(numSamps):
    '''
    Create a power (y=x^2) distribution weighted toward higher numbers
    '''
    t = np.power(np.arange(numSamps),2.0)
    return t/np.sum(t)


def negativeProbsPow(numSamps):
    '''
    Create a linear (y=x^2) distribution weighted toward lower numbers
    '''
    return positive_probs_pow(numSamps)[::-1]


def positive_probs_exp(numSamps):
    '''
    Create a exponential distribution weighted toward higher numbers
    '''
    t = np.exp2(np.arange(numSamps))
    return t/np.sum(t)


def negative_probs_exp(numSamps):
    '''
    Create a exponential distribution weighted toward lower numbers
    '''
    return positive_probs_exp(numSamps)[::-1]

