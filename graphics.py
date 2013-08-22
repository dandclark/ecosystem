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

COLORS = {'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'grey': (100, 100, 100)}


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
    print("Goodbye!")
    if initialized:
        pygame.quit()
    
    
def drawOrganisms():
    for organism in world.organisms:
        organism.draw()
    
def draw():
    assert initialized, "Graphics should be initialized"
    assert not screen is None, "Should have a screen"
    screen.fill(COLORS['white'])
    
    drawOrganisms()
    
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
