#
#    Dan Clark
#    thedanclark@gmail.com
#    30 June 2013
#
#    config.py
#    Ecosystem
#


WORLD_SIZE = (700, 500)
STATUS_SECTION_SIZE = (200, 500)




# NUM_STARTING_PLANTS = 12
# NUM_STARTING_HERBIVORES = 5
# NUM_STARTING_CARNIVORES = 2

NUM_STARTING_PLANTS = 15
NUM_STARTING_HERBIVORES = 5
NUM_STARTING_CARNIVORES = 2

# Graphics settings
SCREEN_SIZE = (WORLD_SIZE[0] + STATUS_SECTION_SIZE[0], max(WORLD_SIZE[1], STATUS_SECTION_SIZE[1]))

class Organism:
    MAX_ATTEMPTS_TO_REPRODUCE = 1
    SPAWN_RING_STARTING_RADIUS = 3
    SPAWN_RING_MAX_RADIUS = 25
    SPAWN_RING_RADIUS_INCREMENT = 1
    SPAWN_RING_WIDTH = 2
    
class Plant(Organism):
    SIZE = 4
    MAX_TIME_BETWEEN_REPRODUCTION = 50000
    REPRODUCTION_RADIUS = 30 # Radius within which children are created
    
class Animal(Organism):
    # How many units of space in either direction can an Animal be away from its
    # destination Location before we consider it to have reached the Location.
    REACHED_LOCATION_TOLERANCE = 2
    
class Herbivore(Animal):
    SIZE = 6
    SPEED = 1
    TIME_TO_HUNGER = 100 # Time until Herbivore becomes hungry after it has eaten
    TIME_TO_STARVATION = 400 # Time until Herbivore starves after it has eaten
    SIGHT_RADIUS = 50 # The radius within which the Herbivore can see food
    MAX_EAT_RADIUS = SIZE # The radius within which the Herbivore can reach food

    MAX_TIME_BETWEEN_REPRODUCTION = 100000
    REPRODUCTION_RADIUS = 20 # Radius within which children are created
    
class Carnivore(Animal):
    SIZE = 8
    SPEED = 2
    TIME_TO_HUNGER = 350 # Time until Carnivore becomes hungry after it has eaten
    TIME_TO_STARVATION = 750 # Time until Carnivore starves after it has eaten
    SIGHT_RADIUS = 70 # The radius within which the Carnivore can see food
    MAX_EAT_RADIUS = SIZE # The radius within which the Carnivore can reach food

    MAX_TIME_BETWEEN_REPRODUCTION = 600000
    REPRODUCTION_RADIUS = 20 # Radius within which children are created
