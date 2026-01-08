from settings import *

class Transition():
    def __init__(self, reset, player, screen_width, screen_height):
        
        # setup
        self.display_surface = pygame.display.get_surface()    
        self.reset = reset
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # overlay image
        self.image = pygame.Surface((self.screen_width, self.screen_height))
        self.color = 255
        self.speed = -2
        
    def on_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        self.image = pygame.Surface((self.screen_width, self.screen_height))
        
    def play(self):
        self.color += self.speed
        if self.color <= 0:
            self.speed *= -1
            self.color = 0
            self.reset()
        if self.color > 255:
            self.color = 255
            self.player.sleep = False
            self.speed = -2
            
        self.image.fill((self.color,self.color,self.color))
        self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGB_MULT)