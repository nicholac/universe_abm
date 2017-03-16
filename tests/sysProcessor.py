'''
Created on 1 Jan 2017

@author: dusted-ipro

Processes a solar system and all the agents within

'''

from multiprocessing.managers import BaseManager


class systemManager(BaseManager):
    pass

systemManager.register('world_getAgent')

m = systemManager(address=('', 8080), authkey='abracadabra')

m.connect()

print m.world_getAgent('gday')

