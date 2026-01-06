from settings import *
from random import randint, choice
from gametimer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, groups, pos, surf, z = LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate((-self.rect.width * 0.2, -self.rect.height * 0.75))
        
class Interaction(Generic):
    def __init__(self, groups, pos, size, name):
        surf = pygame.Surface(size)
        super().__init__(groups, pos, surf)
        self.name = name
        
class Water(Generic):
    def __init__(self, groups, pos, frames):
        
        # animation setup
        self.frames = frames
        self.frame_index = 0
        
        super().__init__(groups, pos, self.frames[self.frame_index], z = LAYERS['water'])
        
    def animate(self, dt):
        self.frame_index += 6 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        
    def update(self, dt, _):
        self.animate(dt)
        
class WildFlower(Generic):
    def __init__(self, groups, pos, surf):       
        super().__init__(groups, pos, surf)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)
        
class Particle(Generic):
    def __init__(self, groups, pos, surf, z, duration = 200):
        super().__init__(groups, pos, surf, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        
        # white surface
        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey('black')
        self.image = new_surf
        
    def update(self, dt, _):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

class Trees(Generic):
    def __init__(self, groups, pos, surf, name, player_add):
        super().__init__(groups, pos, surf)
        
        # tree attributes
        self.health = 5
        self.alive = True
        self.stump_surface = pygame.image.load(join('graphics', 'stumps', f'{'small' if name == 'Small' else 'large'}.png')).convert_alpha()
        self.invul_timer = Timer(200)
        
        # apple
        self.apple_surf = pygame.image.load(join('graphics', 'fruit', 'apple.png'))
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()
        
        self.player_add = player_add
        
    def damage(self):
        self.health -= 1
        
        if (len(self.apple_sprites.sprites()) > 0):
            random_apple = choice(self.apple_sprites.sprites())
            Particle(self.groups()[0], random_apple.rect.topleft, random_apple.image, LAYERS['fruit'])
            self.player_add('apple')
            random_apple.kill()
        
    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                Generic((self.apple_sprites, self.groups()[0]), (self.rect.left + pos[0], self.rect.top + pos[1]), self.apple_surf, LAYERS['fruit'])
                
    def check_death(self):
        if self.health <= 0:
            Particle(self.groups()[0], self.rect.topleft, self.image, LAYERS['fruit'], 300)
            self.image = self.stump_surface
            self.rect = self.image.get_frect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.75)
            self.alive = False
            self.player_add('wood')
            
    def update(self, dt, _):
        if self.alive:
            self.check_death()