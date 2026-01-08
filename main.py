from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Stardew Valley')
        self.clock = pygame.Clock()
        self.screen_width = self.display_surface.get_width()
        self.screen_height = self.display_surface.get_height()
        self.fullscreen = False
        self.monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        
        # Display loading message
        font = pygame.font.Font(join('font', 'LycheeSoda.ttf'), 36)
        text = font.render('Loading...', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.display_surface.fill((0, 0, 0))
        self.display_surface.blit(text, text_rect)
        pygame.display.update()
        
        self.level = Level(self.screen_width, self.screen_height)
        
    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.display_surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                        self.level.on_resize(event.w, event.h)
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        
                        if self.fullscreen:
                            self.display_surface = pygame.display.set_mode(self.monitor_size, pygame.FULLSCREEN | pygame.SCALED)
                        else:
                            self.display_surface = pygame.display.set_mode((self.display_surface.get_width(), self.display_surface.get_height()), pygame.RESIZABLE)
                            
                        self.level.on_resize(self.display_surface.get_width(), self.display_surface.get_height())
                    
                        
                    
            dt = self.clock.tick() / 1000
            self.level.run(dt, events)
            pygame.display.update()
            
if __name__ == '__main__':
    game = Game()
    game.run()