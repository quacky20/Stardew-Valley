from settings import *
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Stardew Valley')
        self.clock = pygame.Clock()
        # # Display loading message
        # font = pygame.font.Font(None, 36)
        # text = font.render('Loading...', True, (255, 255, 255))
        # text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        # self.display_surface.fill((0, 0, 0))
        # self.display_surface.blit(text, text_rect)
        # pygame.display.update()
        self.level = Level()
        
    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            dt = self.clock.tick() / 1000
            self.level.run(dt, events)
            pygame.display.update()
            
if __name__ == '__main__':
    game = Game()
    game.run()