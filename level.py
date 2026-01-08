from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Trees, Interaction, Particle
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from random import randint
from menu import Menu, Pause

class Level:
    def __init__(self, screen_width, screen_height):
        self.display_surface = pygame.display.get_surface()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # sprite groups
        self.all_sprites = CameraGroup(self.screen_width, self.screen_height)
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
    
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player, self.screen_width, self.screen_height)
        self.transition = Transition(self.reset, self.player, self.screen_width, self.screen_height)
        
        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0, 10) < 3
        self.soil_layer.raining = self.raining
        self.sky = Sky(self.screen_width, self.screen_height)
        
        # shop
        self.shop_active = False
        self.menu = Menu(self.player, self.toggle_shop, self.screen_width, self.screen_height)
        
        # sound
        self.pickup = pygame.mixer.Sound(join('audio', 'success.wav'))
        self.pickup.set_volume(0.3)
        self.music = pygame.mixer.Sound(join('audio', 'music.mp3'))
        self.music.set_volume(0.3)
        self.music.play(loops = -1)
        
        # pause
        self.pause_active = False
        self.pause = Pause(self.toggle_pause, self.screen_width, self.screen_height)
            
    def setup(self):
        tmx_data = load_pygame(join('data', 'map.tmx'))
        
        # house
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(self.all_sprites, (x * TILE_SIZE, y * TILE_SIZE), surf, LAYERS['house bottom'])
                
        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic(self.all_sprites, (x * TILE_SIZE, y * TILE_SIZE), surf)
        
        # fence
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((self.all_sprites, self.collision_sprites), (x * TILE_SIZE, y * TILE_SIZE), surf)
            
        # water
        water_frames = import_folder(join('graphics', 'water'))
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water(self.all_sprites, (x * TILE_SIZE, y * TILE_SIZE), water_frames)
            
        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((self.all_sprites, self.collision_sprites), (obj.x, obj.y), obj.image)
            
        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Trees(
                groups = (self.all_sprites, self.collision_sprites, self.tree_sprites),
                pos = (obj.x, obj.y),
                surf = obj.image,
                name = obj.name,
                player_add = self.player_add)
        
        # ground
        Generic(
            groups = self.all_sprites,
            pos = (0,0),
            surf = pygame.image.load(join('graphics', 'world', 'ground.png')).convert_alpha(),
            z = LAYERS['ground']
        )
        
        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(self.collision_sprites, (x * TILE_SIZE, y * TILE_SIZE), surf)
        
        # player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(self.all_sprites, (obj.x, obj.y), self.collision_sprites, self.tree_sprites, self.interaction_sprites, self.soil_layer, self.toggle_shop, self.toggle_pause)
                
            if obj.name == 'Bed':
                Interaction(self.interaction_sprites, (obj.x, obj.y), (obj.width, obj.height), obj.name)
                
            if obj.name == 'Trader':
                Interaction(self.interaction_sprites, (obj.x, obj.y), (obj.width, obj.height), obj.name)
    
    def player_add(self, item):
        self.player.item_inventory[item] += 1
        self.pickup.play()
    
    def toggle_shop(self):
        self.shop_active = not self.shop_active
    
    def toggle_pause(self):
        self.pause_active = not self.pause_active
    
    def reset(self):
        # plants
        self.soil_layer.update_plants()
        
        # soil
        self.soil_layer.remove_water()
        self.raining = randint(0, 10) < 3
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()
        
        # apples
        for tree in self.tree_sprites:
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()
            
        # sky
        self.sky.start_color = [255, 255, 255]
    
    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(self.all_sprites, plant.rect.topleft, plant.image, LAYERS['main'])
                    self.soil_layer.grid[int(plant.rect.centery // TILE_SIZE)][int(plant.rect.centerx // TILE_SIZE)].remove('P')
    
    def on_resize(self, new_width, new_height):
        self.screen_width = new_width
        self.screen_height = new_height
        
        # menu
        self.menu.on_resize(self.screen_width, self.screen_height)     
        
        # sky
        self.sky.on_resize(self.screen_width, self.screen_height)
        
        # transition
        self.transition.on_resize(self.screen_width, self.screen_height)
        
        # overlay
        self.overlay.on_resize(self.screen_width, self.screen_height)
        
        # camera
        self.all_sprites.screen_width = self.screen_width        
        self.all_sprites.screen_height = self.screen_height  
    
    def run(self, dt, events):
        # drawing
        self.display_surface.fill('black')
        self.all_sprites.draw(self.player)
        
        # updates
        if self.shop_active:
            self.menu.update()
            
        elif self.pause_active:
            self.pause.update()
            
        else:
            self.all_sprites.update(dt, events)
            self.plant_collision()
        
        # rain
        if self.raining and not self.shop_active:
            self.rain.update()
            
        # day-night cycle
        self.sky.display(dt)
        
        # transition
        self.overlay.display()
        
        if self.player.sleep:
            self.transition.play()
        
        # print(self.shop_active)
        
class CameraGroup(pygame.sprite.Group):
    def __init__(self, screen_width, screen_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
    def draw(self, player):
        self.offset.x = -(player.rect.centerx - self.screen_width / 2)
        self.offset.y = -(player.rect.centery - self.screen_height / 2)
        for sprite in sorted(self.sprites(), key = lambda sprite: (sprite.z, sprite.rect.centery)):
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
            
            # analytics
            # if sprite == player:
                # offset_rect = sprite.rect.copy()
                # offset_rect.topleft = sprite.rect.topleft + self.offset
                # pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                # hitbox_rect = player.hitbox.copy()
                # hitbox_rect.center = sprite.rect.center + self.offset
                # pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                # target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                # pygame.draw.circle(self.display_surface, 'green', target_pos, 5)
                
        