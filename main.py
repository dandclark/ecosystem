#!/usr/bin/python
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
import organism
from util import LOGGING

if __name__ == "__main__":
    print("Starting Ecosystem...")
    
    graphics.initialize()
    
    world.spawnOrganisms(organism.Plant, config.NUM_STARTING_PLANTS, False)
    world.spawnOrganisms(organism.Herbivore, config.NUM_STARTING_HERBIVORES, False)
    world.spawnOrganisms(organism.Carnivore, config.NUM_STARTING_CARNIVORES, False)
    
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

