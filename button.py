import pygame


DEFAULT_COLOR = (160, 160, 160)
HOVERED_COLOR = (140, 140, 140)
CLICKED_COLOR = (100, 100, 100)

class Button:
    def __init__(self, rect, onClick):
        self.rect = rect
        self.onClick = onClick
        self.isClicked = False

    def getEvent(self, event):
        #print("Button got event", event)
        if self.isClicked:
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                # Release the click whether or not the mouse was released within
                # the rect of the button.
                self.isClicked = False

                if self.rect.collidepoint(event.pos):
                    self.onClick()
        else: # !self.isClicked
            if (event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1 and
                    self.rect.collidepoint(event.pos)):
                self.isClicked = True
    def draw(self, screen):
        isHovered = self.rect.collidepoint(pygame.mouse.get_pos())
        colorForDraw = None
        if isHovered:
            colorForDraw = CLICKED_COLOR if self.isClicked else HOVERED_COLOR 
        else:
            colorForDraw = DEFAULT_COLOR
        pygame.draw.rect(screen, colorForDraw, self.rect)
