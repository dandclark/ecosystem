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
from util import clip
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
        if abs(self.location.x - self.destination.x) <= self.speed:
            self.location.x = self.destination.x
        else:
            self.location.x += self.speed if self.location.x < self.destination.x \
                    else -self.speed if self.location.x > self.destination.x else 0
        if abs(self.location.y - self.destination.y) <= self.speed:
            self.location.y = self.destination.y
        self.location.y += self.speed if self.location.y < self.destination.y \
                else -self.speed if self.location.y > self.destination.y else 0
    
    # Returns true if the Animal has arrived at their destination, false otherwise
    def hasArrivedAtDestination(self):
        return (abs(self.location.x - self.destination.x) < config.Animal.REACHED_LOCATION_TOLERANCE
                and abs(self.location.y - self.destination.y) < config.Animal.REACHED_LOCATION_TOLERANCE)
    
    # Returns true if the Animal will try to eat if there is food available
    def isHungry(self):
        return self.timeSinceLastEaten >= self.timeToHunger
    
    # End the Animal's life if it has starved
    def dieIfStarved(self):
        if self.timeSinceLastEaten >= self.timeToStarvation:
            assert self.isHungry()
            self.isAlive = False
            
    def drawStatusBars(self):
        bottomStatusBarLocation = Location(self.location.x, int(self.location.y - 1.5 * self.size))
        graphics.drawStatusBar(bottomStatusBarLocation,
                int(2.0 * self.size),
                clip((self.timeToStarvation - self.timeSinceLastEaten) / (self.timeToStarvation - self.timeToHunger), 0.0, 1.0))
        graphics.drawStatusBar(Location(bottomStatusBarLocation.x, int(bottomStatusBarLocation.y - 1.2 * graphics.STATUS_BAR_HEIGHT)),
                int(2.0 * self.size),
                clip((self.timeToHunger - self.timeSinceLastEaten) / self.timeToHunger, 0.0, 1.0))
    
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
        self.prey = None # Is the Herbivore chasing a particular prey organism
        
        self.lastReproductionAge = 0
        self.maxTimeBetweenReproduction = config.Herbivore.MAX_TIME_BETWEEN_REPRODUCTION
        self.reproductionRadius = config.Herbivore.REPRODUCTION_RADIUS # Radius within which children are created
        self.maxAttemptsToReproduce = config.Herbivore.MAX_ATTEMPTS_TO_REPRODUCE
        
    def draw(self):
        assert self.isAlive
        assert self.prey is None or self.isHungry()
        if self.isHungry() and not self.prey is None:
            color = graphics.COLORS['blue']
            graphics.pygame.draw.line(graphics.screen, graphics.COLORS['red'],
                    [self.location.x, self.location.y],
                    [self.prey.location.x, self.prey.location.y], 1)
        elif self.isHungry():
            # Fade between colors as the Herbivore gets hungrier
            color = graphics.getTransitionColor(graphics.COLORS['blue'],
                    graphics.COLORS['grey'],
                    float(self.timeSinceLastEaten) / self.timeToStarvation)
        else:
            color = graphics.COLORS['blue']
        graphics.pygame.draw.circle(graphics.screen, color,
            [self.location.x, self.location.y], self.size)
        self.drawStatusBars()
            
    def doTurn(self):
        super().doTurn()
        
        if self.shouldReproduce():
            if LOGGING:
                print("Herbivore", self, "reproducing")
            self.lastReproductionAge = self.age
            self.reproduce()
        
        # Stop chasing prey if it's not there anymore
        if not self.prey is None:
            if not self.prey.isAlive:
                self.prey = None
        
        self.takeStep()
        self.timeSinceLastEaten += 1
        assert self.prey is None or self.isHungry()
        if self.isHungry():
            atePrey = self.tryToEat()
            if atePrey and not self.prey is None:
                # If the Herbivore successfully chased down and ate prey, now it needs
                # something else to do.
                self.prey = None
                self.destination = self.getNewDestination()
            
        if self.isHungry() and (self.prey is None or self.hasArrivedAtDestination()):
            # Look for prey to chase down.
            potentialPrey = self.findPrey()
            if len(potentialPrey) > 0:
                self.destination = potentialPrey[0].location
                self.prey = potentialPrey[0]
            else:
                self.prey = None
                
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
        
class Carnivore(Animal):
    def __init__(self):
        super().__init__()
        self.size = config.Carnivore.SIZE
        self.speed = config.Carnivore.SPEED
        self.destination = self.getNewDestination()
        self.timeSinceLastEaten = 0
        self.timeToHunger = config.Carnivore.TIME_TO_HUNGER
        self.timeToStarvation = config.Carnivore.TIME_TO_STARVATION
        self.sightRadius = config.Carnivore.SIGHT_RADIUS # The radius within which the Carnivore can see food
        self.maxEatRadius = config.Carnivore.MAX_EAT_RADIUS # The radius within which the Carnivore can reach food
        
        self.lastReproductionAge = 0
        self.maxTimeBetweenReproduction = config.Carnivore.MAX_TIME_BETWEEN_REPRODUCTION
        self.reproductionRadius = config.Carnivore.REPRODUCTION_RADIUS # Radius within which children are created
        self.maxAttemptsToReproduce = config.Carnivore.MAX_ATTEMPTS_TO_REPRODUCE
        self.prey = None
    
    def draw(self):
        assert self.isAlive
        assert self.prey is None or self.isHungry()
        if self.isHungry() and not self.prey is None:
            color = graphics.COLORS['blue']
            graphics.pygame.draw.line(graphics.screen, graphics.COLORS['red'],
                    [self.location.x, self.location.y],
                    [self.prey.location.x, self.prey.location.y], 1)
        elif self.isHungry():
            # Fade between colors as the Carnivore gets hungrier
            color = graphics.getTransitionColor(graphics.COLORS['blue'],
                    graphics.COLORS['grey'],
                    float(self.timeSinceLastEaten) / self.timeToStarvation)
        else:
            color = graphics.COLORS['blue']
        graphics.pygame.draw.circle(graphics.screen, color,
            [self.location.x, self.location.y], self.size)
        self.drawStatusBars()
    
    def doTurn(self):
        super().doTurn()
        
        if self.shouldReproduce():
            if LOGGING:
                print(self.__class__.__name__, self, "reproducing")
            self.lastReproductionAge = self.age
            self.reproduce()
        
        # Continue chasing prey
        if not self.prey is None:
            if not self.prey.isAlive:
                self.prey = None
            else:
                self.destination = self.prey.location
        
        self.takeStep()
        self.timeSinceLastEaten += 1
        assert self.prey is None or self.isHungry()
        if self.isHungry():
            atePrey = self.tryToEat()
            if atePrey:
                # If the Carnivore successfully chased down and ate prey, now it needs
                # something else to do.
                self.destination = self.getNewDestination()
            
        if self.isHungry() and (self.prey is None or self.hasArrivedAtDestination()):
            # Look for prey to chase down.
            potentialPrey = self.findPrey()
            if len(potentialPrey) > 0:
                self.prey = potentialPrey[0]
                self.destination = self.prey.location
            else:
                assert self.prey is None or self.hasArrivedAtDestina
                self.prey = None
                
        self.dieIfStarved()
                
        if self.hasArrivedAtDestination():
            self.destination = self.getNewDestination()
            
        if LOGGING:
            print("Age of", self.__class__.__name__, "is", self.age)
    
    # If there is a prey Organism within range of this Carnivore, remove it from the world
    # and set this Carnivore's timeSinceLastEaten to 0.
    # Returns True if prey was successfully eaten, False otherwise.
    def tryToEat(self):
        nearbyOrganisms = getLivingOrganismsInRadiusWithType(world.organisms, self.location, self.maxEatRadius, Herbivore)
        if len(nearbyOrganisms) > 0:
            # Eat the unfortunate prey
            nearbyOrganisms[0].isAlive = False
            self.timeSinceLastEaten = 0
            self.prey = None
            return True
        else:
            return False
    
    # Returns a new location for the Herbivore.
    def getNewDestination(self):
        return world.randomLocation()
    
    # Returns a list of living prey organisms within sight.
    def findPrey(self):
        return getLivingOrganismsInRadiusWithType(world.organisms, self.location, self.sightRadius, Herbivore)
    
    def createOffspring(self):
        return Carnivore()
    