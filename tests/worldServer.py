'''
Created on 1 Jan 2017

@author: dusted-ipro

World Server:
    - Generates universe
    - Builds a list of connected clients
    - Distributes Solar Systems (and Agents) amongst available clients
    - Helps move agents between systems (central IO point)
    - Manages the social network and global universe state

'''
from multiprocessing.managers import BaseManager
#from agents.base import baseAgent


def getAgent(input):
    return 'Hello'+input


class worldManager(BaseManager):
    pass


if __name__ == '__main__':
    try:
        worldManager.register('world_getAgent', getAgent)
        manager = worldManager(address=('', 8080), authkey='abracadabra')
        server = manager.get_server()
        print 'Starting'
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print 'Killed'
    print 'Done'


