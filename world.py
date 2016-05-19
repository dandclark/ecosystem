#
#    Dan Clark
#    thedanclark@gmail.com
#    15 June 2013
#
#    world.py
#    Ecosystem
#

from util import Location
from util import LOGGING
import config
import math
import organism
import random

organisms = []

print("Importing world module")
    
# Returns true if there is room at targetLocation for the specified Organism
def canFit(theOrganism, targetLocation):
    for existingOrganism in organisms:
        if (existingOrganism.location.distanceFrom(targetLocation)) \
                < theOrganism.size + existingOrganism.size:
            return False
    return True

# Return a random location (uniformly distributed) in the world
def randomLocation():
    return Location(random.randint(0, config.WORLD_SIZE[0]), random.randint(0, config.WORLD_SIZE[1]))

# Returns a random location (uniformly distributed) in a circle with the specified
# center Location and radius.
def randomLocationInCircle(center, radius):
    orientationRad = random.uniform(0, 2.0 *  math.pi)
    distanceFromCenter = random.uniform(0, radius)
    randomLocation = Location()
    randomLocation.x = int(center.x + radius * math.sin(orientationRad))
    randomLocation.y = int(center.y + radius * math.cos(orientationRad))
    # Bound the new location within the world
    randomLocation.x = max(0, min(config.WORLD_SIZE[0], randomLocation.x))
    randomLocation.y = max(0, min(config.WORLD_SIZE[1], randomLocation.y))
    return randomLocation
    
def spawnOrganisms(organismType, numberToSpawn, createWithSpawnRing):
    for i in range(numberToSpawn):
        newOrganism = organismType(createWithSpawnRing)
        while True:
            potentialLocation = randomLocation()
            if LOGGING:
                print("Attempting to spawn", organismType.__name__, "at", potentialLocation)
            if canFit(newOrganism, potentialLocation):
                newOrganism.location = potentialLocation
                break
        if LOGGING:
            print("Spawning new", organismType.__name__, "at", newOrganism.location)
        organisms.append(newOrganism)
    if LOGGING:
        print("Spawned", numberToSpawn, organismType.__name__ + "s")
        
# Remove all dead organisms from the organism array
# @consider doing this differently.  We're doing a full copy of the Herbivore array
# every clock tick...might be better to either store these as a linked list or do
# this purge less frequently.
def purgeDeadOrganisms():
    global organisms
    survivingOrganisms = []
    for theOrganism in organisms:
        if theOrganism.isAlive:
            survivingOrganisms.append(theOrganism)
    organisms = survivingOrganisms
        
# Pass one unit of time for every Organism in the world
def doTurn():
    for theOrganism in organisms:
        theOrganism.doTurn()
    purgeDeadOrganisms()
