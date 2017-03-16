'''
Created on 25 Dec 2016

@author: dusted-ipro

Generic Support Functions
'''
import numpy as np

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
def gen_harvestor_caps():
    '''
    Randomly generate capacities for harvestor
    Tons
    '''
    return (np.random.choice(np.linspace(10.0, 100.0)), #Raw Mat Cap
            np.random.choice(np.linspace(10.0, 100.0)), #Energy Cap
            np.random.choice(np.linspace(10.0, 100.0))) #HG Cap

def gen_harvestor_rates():
    '''
    Randomly generate harvest & consume rates for harvestor
    Tons per tick
    '''
    return (np.random.choice(np.linspace(0.1, 1.0)), #Energy Harvest
            np.random.choice(np.linspace(0.1, 1.0)), #Raw Mat Harvest
            np.random.choice(np.linspace(0.0001, 0.01)), #HG Consume
            np.random.choice(np.linspace(0.0001, 0.01))) #Energy Consume

def gen_clan_rates():
    '''
    Randomly generate clan global consumption rates
    Tones per tick
    '''
    return (np.random.choice(np.linspace(0.01, 1.0)), 0.0)




#Probability generation
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


#GENETICS

def crossover_traits():
    '''
    List of all traits that can be crossed-over
    '''
    return ['vis', 'velMag', 'defence', 'offence']

def vis_bounds():
    '''
    Min and max for visibility trait
    '''
    return au2Ly(0.1), au2Ly(50.0)

def vel_mag_bounds():
    '''
    Min and max for vel_mag trait
    '''
    return au2Ly(1.0), au2Ly(10.0)

def offence_bounds():
    '''
    Min and max for offence trait
    '''
    return 0.0, 1.0

def mutation_bounds():
    '''
    Min and max for amount traits can be mutated by (%)
    '''
    return -0.1, 0.1





