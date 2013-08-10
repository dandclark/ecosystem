#
#    Dan Clark
#    thedanclark@gmail.com
#    15 June 2013
#
#    main.py
#    Ecosystem
#

from organism import Organism
import world
import graphics
import config
from util import LOGGING

if __name__ == "__main__":
    print("Hello, world")
    
    graphics.initialize()
    
    world.spawnPlants(config.NUM_STARTING_PLANTS)
    world.spawnAnimals(config.NUM_STARTING_ANIMALS)
    
    shouldContinue = True
    
    if LOGGING:
        print("Starting main game loop")
    while shouldContinue:
        shouldContinue = graphics.handleEvents(world)
        graphics.draw()
        
        world.doTurn()
        
        graphics.advanceClock()
        # print("In main game loop")
        
    graphics.quit()