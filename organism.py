#
#    Dan Clark
#    thedanclark@gmail.com
#    15 June 2013
#
#    organism.py
#    Ecosystem
#

from util import Location
from util import LOGGING
from util import getOrganismsInRadius
import graphics
import random
import world
import config
import abc # For abstract base class


class Organism(metaclass=abc.ABCMeta):
    def __init__(self):
        self.isAlive = True
        self.age = 0
        self.location = Location(0,0)
        
    # Draw the Organism
    @abc.abstractmethod
    def draw(self):
        pass
        
    # Run one unit of time for the organism
    def doTurn(self):
        self.age += 1
        
class Plant(Organism):
    def __init__(self):
        super().__init__()
        self.size = 4
        self.lastReproductionAge = 0
        self.maxTimeBetweenReproduction = 50000
        self.reproductionRadius = 20 # Radius within which children are created
        self.maxAttemptsToReproduce = 1
        
    def draw(self):
        assert self.isAlive
        graphics.pygame.draw.circle(graphics.screen, graphics.COLORS['green'],
            [self.location.x, self.location.y], self.size)
            
    def doTurn(self):
        super().doTurn()
        if LOGGING:
            print("Age of plant is", self.age, "lastReproductionAge:", self.lastReproductionAge)
                
        if self.shouldReproduce():
            if LOGGING:
                print("Plant", self, "reproducing")
            self.lastReproductionAge = self.age
            self.reproduce()
        
    # Returns true if should reproduce this turn, false othewise.
    def shouldReproduce(self):
        timeSinceLastReproduction = self.age - self.lastReproductionAge
        probabilityOfReproduction = min(1.0, timeSinceLastReproduction / self.maxTimeBetweenReproduction)
        return random.random() < probabilityOfReproduction
        
        
    # Attempt to place a new plant at a nearby location.  If it's too crowded
    # to place another plant, give up after a specified number of attempts.
    def reproduce(self):
        newPlant = Plant()
        attemptsToReproduce = 0
        while attemptsToReproduce < self.maxAttemptsToReproduce:
            potentialLocation = world.randomLocationInCircle(self.location, self.reproductionRadius)
            if LOGGING:
                print(self, "attempting to reproduce at", potentialLocation)
            if world.canFit(newPlant, potentialLocation):
                newPlant = Plant()
                newPlant.location = potentialLocation
                world.organisms.append(newPlant)
                return
            attemptsToReproduce += 1

        
class Animal(Organism):
    def __init__(self):
        super().__init__()
        self.size = 8
        self.speed = 1
        self.destination = self.getNewDestination()
        self.timeSinceLastEaten = 0
        self.timeToHunger = 50
        self.maxEatRadius = 8 # The radius within which the Animal can reach food
        
    def draw(self):
        assert self.isAlive
        if self.isHungry():
            color = graphics.COLORS['red']
        else:
            color = graphics.COLORS['blue']
        graphics.pygame.draw.circle(graphics.screen, color,
            [self.location.x, self.location.y], self.size)
            
    def doTurn(self):
        super().doTurn()
        self.takeStep()
        if self.hasArrivedAtDestination():
            self.destination = self.getNewDestination()
        self.timeSinceLastEaten += 1
        if self.isHungry():
            self.tryToEat()
        if LOGGING:
            print("Age of Animal is", self.age)
            
    # Take one step in the direction of the Animal's current destination
    def takeStep(self):
        newLocation = Location()
        self.location.x += self.speed if self.location.x < self.destination.x \
                else -self.speed if self.location.x > self.destination.x else 0
        self.location.y += self.speed if self.location.y < self.destination.y \
                else -self.speed if self.location.y > self.destination.y else 0
    
        
    # Returns true if the Animal has arrived at their destination, false otherwise
    def hasArrivedAtDestination(self):
        return (abs(self.location.x - self.destination.x) < config.REACHED_LOCATION_TOLERANCE
                and abs(self.location.y - self.destination.y) < config.REACHED_LOCATION_TOLERANCE)

    # Returns a new, randomly generated location for the Animal
    def getNewDestination(self):
        return world.randomLocation()
        
    # Returns true if the Animal will try to eat if there is food available
    def isHungry(self):
        return self.timeSinceLastEaten >= self.timeToHunger
        
    # If there is a prey Organism within range of this Animal, remove it from the world
    # and set this Animal's timeSinceLastEaten to 0.
    def tryToEat(self):
        nearbyOrganisms = getOrganismsInRadius(world.organisms, self.location, self.maxEatRadius)
        for theOrganism in nearbyOrganisms:
            if isinstance(theOrganism, Plant) and theOrganism.isAlive:
                # Eat the unfortunate prey
                theOrganism.isAlive = False
                self.timeSinceLastEaten = 0
    