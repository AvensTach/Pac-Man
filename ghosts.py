import pygame


class Ghost():

    def __init__(self, x:int, y:int, color:tuple, image:str):
    """ Class to represent a ghost """

    def __init__(self, x: int, y: int, color: tuple, image: str):
        self.x = x
        self.y = y
        self.color = color
        self.speed = 0
        self.image = image
        self.frightened = False
        self.timer = 0

        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def draw(self, screen):

        """ Draw the ghost """
        draw_color = (0, 0, 255) if self.frightened else self.color
        pygame.draw.rect(screen, draw_color, self.rect)
