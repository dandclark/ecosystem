#
#    Dan Clark
#    thedanclark@gmail.com
#    15 June 2013
#
#    graphics.py
#    Ecosystem
#

import config
import pygame
import world
from util import Location

COLORS = {'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'grey': (100, 100, 100),
        'darkGrey': (50, 50, 50),
        'yellow': (255, 255, 0)}

STATUS_BAR_HEIGHT = 3
WORLD_SIZE = config.WORLD_SIZE
STATUS_SECTION_SIZE = config.STATUS_SECTION_SIZE

ORGANISM_STATS_LEFT = WORLD_SIZE[0] + 50
ORGANISM_STATS_TOP = 120
 
# We'll store the graphics state as module-level variables.
initialized = False
screen = None
clock = None

def initialize():
    global initialized, screen, clock
    if not initialized:
        pygame.init()
        
        # Set up the screen
        screen = pygame.display.set_mode(config.SCREEN_SIZE)
        pygame.display.set_caption("Ecosystem")

        clock = pygame.time.Clock()
        
        initialized = True
        
    else:
        raise Exception("Graphics should only be initialized once")
        
def quit():
    print("Exiting...")
    if initialized:
        pygame.quit()
    
def drawMenu():
    # Draw divider between main screen and menu 
    pygame.draw.line(screen, COLORS['darkGrey'], (WORLD_SIZE[0], 0),
        (WORLD_SIZE[0], WORLD_SIZE[1]), 3)

    pygame.draw.circle(screen, COLORS['green'],
        [ORGANISM_STATS_LEFT, ORGANISM_STATS_TOP], config.Plant.SIZE)
    pygame.draw.circle(screen, COLORS['blue'],
        [ORGANISM_STATS_LEFT, ORGANISM_STATS_TOP * 2], config.Herbivore.SIZE)
    pygame.draw.circle(screen, COLORS['blue'],
        [ORGANISM_STATS_LEFT, ORGANISM_STATS_TOP * 3], config.Carnivore.SIZE)
 
def drawOrganisms():
    for organism in world.organisms:
        organism.draw()
    
def draw():
    assert initialized, "Graphics should be initialized"
    assert not screen is None, "Should have a screen"
    screen.fill(COLORS['white'])
    
    drawOrganisms()
  
    # @todo Drawn menu on separate screen so we only have to do it once? 
    drawMenu()
 
    pygame.display.flip()

# Handle user events.  Returns true if process should continue, false otherwise
def handleEvents(world):
    assert initialized, "Graphics should be initialized"
    shouldContinue = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shouldContinue = False
            
    return shouldContinue
    
def advanceClock():
    assert initialized, "Graphics should be initialized"
    assert not clock is None, "Should have a screen"
    clock.tick(20)
    
def getTransitionColor(startColor, endColor, transitionPercentage):
    deltaColor = [end - start for end, start in zip(endColor, startColor)]
    return [start + delta * transitionPercentage for start, delta in zip(startColor, deltaColor)]

# Draw a status bar centered at centerLocation.  width specifies the width of the
# bar in pixels.  amoountFilled is a fraction from 0 to 1.
def drawStatusBar(centerLocation, width, amountFilled):
    assert amountFilled >= 0.0 and amountFilled <= 1.0
    topLeft = Location(int(centerLocation.x - width / 2.0),
            int(centerLocation.y - STATUS_BAR_HEIGHT / 2.0))
    pygame.draw.rect(screen, COLORS['grey'],
            [topLeft.x, topLeft.y, width, STATUS_BAR_HEIGHT])
    pygame.draw.rect(screen, COLORS['yellow'],
            [topLeft.x, topLeft.y, int(width * amountFilled), STATUS_BAR_HEIGHT])
            
