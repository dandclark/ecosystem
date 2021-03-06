import pygame


DEFAULT_COLOR = (160, 160, 160)
HOVERED_COLOR = (140, 140, 140)
CLICKED_COLOR = (100, 100, 100)

class Button:
    def __init__(self, rect, text, *onClick):
        self.rect = rect
        self.onClick = onClick
        self.isClicked = False
        self.text = text

    def getEvent(self, event):
        if self.isClicked:
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                # Release the click whether or not the mouse was released within
                # the rect of the button.
                self.isClicked = False

                if self.rect.collidepoint(event.pos):
                    self.onClick[0](*self.onClick[1:])
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

        # Draw the button's text
        font = pygame.font.Font(None, 60)
        textSurface = font.render(self.text, True, (0,0,0)) 
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

