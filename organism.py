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
from util import getLivingOrganismsInRadiusWithType
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
        
    # Returns an instance of the Organism (a non-abstract subclass).
    # @todo Is there a more pythonic way to do this?
    @abc.abstractmethod
    def createOffspring(self):
        pass
        
    # Run one unit of time for the organism
    def doTurn(self):
        self.age += 1
        
        # Returns true if should reproduce this turn, false othewise.
    def shouldReproduce(self):
        timeSinceLastReproduction = self.age - self.lastReproductionAge
        probabilityOfReproduction = min(1.0, timeSinceLastReproduction / self.maxTimeBetweenReproduction)
        return random.random() < probabilityOfReproduction
        
        
    # Attempt to place a new Organism at a nearby location.  If it's too crowded
    # to place another Organism, give up after a specified number of attempts.
    def reproduce(self):
        newOrganism = self.createOffspring()
        attemptsToReproduce = 0
        while attemptsToReproduce < self.maxAttemptsToReproduce:
            potentialLocation = world.randomLocationInCircle(self.location, self.reproductionRadius)
            if LOGGING:
                print(self, "attempting to reproduce at", potentialLocation)
            if world.canFit(newOrganism, potentialLocation):
                newOrganism = self.createOffspring()
                newOrganism.location = potentialLocation
                world.organisms.append(newOrganism)
                return
            attemptsToReproduce += 1
        
        
class Plant(Organism):
    def __init__(self):
        super().__init__()
        self.size = config.Plant.SIZE
        self.lastReproductionAge = 0
        self.maxTimeBetweenReproduction = config.Plant.MAX_TIME_BETWEEN_REPRODUCTION
        self.reproductionRadius = config.Plant.REPRODUCTION_RADIUS
        self.maxAttemptsToReproduce = config.Plant.MAX_ATTEMPTS_TO_REPRODUCE
        
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
        
    def createOffspring(self):
        return Plant()

        
class Animal(Organism):
    # Take one step in the direction of the Animal's current destination
    def takeStep(self):
        self.location.x += self.speed if self.location.x < self.destination.x \
                else -self.speed if self.location.x > self.destination.x else 0
        self.location.y += self.speed if self.location.y < self.destination.y \
                else -self.speed if self.location.y > self.destination.y else 0
    
    # Returns true if the Animal has arrived at their destination, false otherwise
    def hasArrivedAtDestination(self):
        return (abs(self.location.x - self.destination.x) < config.Animal.REACHED_LOCATION_TOLERANCE
                and abs(self.location.y - self.destination.y) < config.Animal.REACHED_LOCATION_TOLERANCE)
    
    # Returns true if the Herbivore will try to eat if there is food available
    def isHungry(self):
        return self.timeSinceLastEaten >= self.timeToHunger
    
    # End the Animal's life if it has starved
    def dieIfStarved(self):
        if self.timeSinceLastEaten >= self.timeToStarvation:
            assert self.isHungry()
            self.isAlive = False
    
class Herbivore(Animal):
    def __init__(self):
        super().__init__()
        self.size = config.Herbivore.SIZE
        self.speed = config.Herbivore.SPEED
        self.destination = self.getNewDestination()
        self.timeSinceLastEaten = 0
        self.timeToHunger = config.Herbivore.TIME_TO_HUNGER
        self.timeToStarvation = config.Herbivore.TIME_TO_STARVATION
        self.sightRadius = config.Herbivore.SIGHT_RADIUS # The radius within which the Herbivore can see food
        self.maxEatRadius = config.Herbivore.MAX_EAT_RADIUS # The radius within which the Herbivore can reach food
        self.isChasingPrey = False # Is the Herbivore chasing a particular prey organism
        
        self.lastReproductionAge = 0
        self.maxTimeBetweenReproduction = config.Herbivore.MAX_TIME_BETWEEN_REPRODUCTION
        self.reproductionRadius = config.Herbivore.REPRODUCTION_RADIUS # Radius within which children are created
        self.maxAttemptsToReproduce = config.Herbivore.MAX_ATTEMPTS_TO_REPRODUCE
        
    def draw(self):
        assert self.isAlive
        assert not self.isChasingPrey or self.isHungry()
        if self.isHungry() and self.isChasingPrey:
            color = graphics.COLORS['red']
        elif self.isHungry():
            # Fade between colors as the Herbivore gets hungrier
            color = graphics.getTransitionColor(graphics.COLORS['blue'],
                    graphics.COLORS['grey'],
                    float(self.timeSinceLastEaten) / self.timeToStarvation)
        else:
            color = graphics.COLORS['blue']
        graphics.pygame.draw.circle(graphics.screen, color,
            [self.location.x, self.location.y], self.size)
            
    def doTurn(self):
        super().doTurn()
        
        if self.shouldReproduce():
            if LOGGING:
                print("Herbivore", self, "reproducing")
            self.lastReproductionAge = self.age
            self.reproduce()
        
        self.takeStep()
        self.timeSinceLastEaten += 1
        assert not self.isChasingPrey or self.isHungry()
        if self.isHungry():
            atePrey = self.tryToEat()
            if atePrey and self.isChasingPrey:
                # If the Herbivore successfully chased down and ate prey, now it needs
                # something else to do.
                self.isChasingPrey = False
                self.destination = self.getNewDestination()
            
        if self.isHungry() and (not self.isChasingPrey or self.hasArrivedAtDestination()):
            # Look for prey to chase down.
            potentialPrey = self.findPrey()
            if len(potentialPrey) > 0:
                self.destination = potentialPrey[0].location
                self.isChasingPrey = True
            else:
                self.isChasingPrey = False
                
        self.dieIfStarved()
                
        if self.hasArrivedAtDestination():
            self.destination = self.getNewDestination()
            
        if LOGGING:
            print("Age of Herbivore is", self.age)
            
    # Returns a new location for the Herbivore.
    def getNewDestination(self):
        return world.randomLocation()
        
    # Returns a list of living prey organisms within sight.
    def findPrey(self):
        return getLivingOrganismsInRadiusWithType(world.organisms, self.location, self.sightRadius, Plant)
                
    # If there is a prey Organism within range of this Herbivore, remove it from the world
    # and set this Herbivore's timeSinceLastEaten to 0.
    # Returns True if prey was successfully eaten, False otherwise.
    def tryToEat(self):
        nearbyOrganisms = getLivingOrganismsInRadiusWithType(world.organisms, self.location, self.maxEatRadius, Plant)
        if len(nearbyOrganisms) > 0:
            # Eat the unfortunate prey
            nearbyOrganisms[0].isAlive = False
            self.timeSinceLastEaten = 0
            return True
        else:
            return False
    
    def createOffspring(self):
        return Herbivore()