from settings import *
from support import *
from gametimer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, pos, collision_sprites, tree_sprites, interaction_sprites, soil_layer):
        super().__init__(groups)
        
        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0
                
        # general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        self.z = LAYERS['main']
        
        # movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 400
        
        # collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites
        
        # timers
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(200)
        }
        
        # tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        
        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        
        # inventory
        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0
        }
        
        # interactions
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.soil_layer = soil_layer
        
    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)
        
        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                
        
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)
    
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
    
    def use_seed(self):
        # print("seed")
        pass
        
    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [], 'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [], 'up_hoe': [], 'down_hoe': [], 'left_hoe': [], 'right_hoe': [], 'up_axe': [], 'down_axe': [], 'left_axe': [], 'right_axe': [], 'up_water': [], 'down_water': [], 'left_water': [], 'right_water': []}
        
        for animation in self.animations.keys():
            full_path = join('graphics', 'character', animation)
            self.animations[animation] = import_folder(full_path)
        
    def animate(self, dt):
        self.frame_index += 4 * dt
        self.image = self.animations[self.status][int(self.frame_index) % len(self.animations[self.status])]
        
    def input(self, events):
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(3)
        
        if not self.timers['tool use'] and not self.sleep:
            # direction
            if keys[pygame.K_UP] | keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] | keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
                
            if keys[pygame.K_LEFT] | keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT] | keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
            
            self.direction = self.direction.normalize() if self.direction else self.direction
            
            # tool use
            if mouse[0]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                
            # change tool
            for event in events:
                if event.type == pygame.MOUSEWHEEL:
                    self.tool_index += event.y
                    self.selected_tool = self.tools[self.tool_index % len(self.tools)]
                    
            if keys[pygame.K_q] and not self.timers['tool switch']:
                self.timers['tool switch'].activate()
                self.tool_index += 1
                self.selected_tool = self.tools[self.tool_index % len(self.tools)]
                
            # seed use
            if mouse[2]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
                
            # change seed
            if keys[pygame.K_e] and not self.timers['seed switch']:
                self.timers['seed switch'].activate()
                self.seed_index += 1
                self.selected_seed = self.seeds[self.seed_index % len(self.seeds)]
                
            # sleep
            if keys[pygame.K_RETURN]:
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name == 'trader':
                        pass
                    else:
                        self.status = 'left_idle'
                        self.sleep = True
        
    def get_status(self):
        # idle
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
            
        # tool use
        if self.timers['tool use']:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery
    
    def move(self, dt):
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = self.pos.x
        self.collision('horizontal')
        self.rect.centerx = self.hitbox.centerx
        
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = self.pos.y
        self.collision('vertical')
        self.rect.centery = self.hitbox.centery
        
    def update(self, dt, events):
        self.input(events)
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        
        self.move(dt)
        self.animate(dt)