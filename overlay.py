from settings import *
from os.path import join

class Overlay:
    def __init__(self, player):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        
        # imports
        overlay_path = join('graphics', 'overlay')
        self.tools_surfs = {tool: pygame.image.load(join(overlay_path, (tool + '.png'))).convert_alpha() for tool in player.tools}
        self.seeds_surfs = {seed: pygame.image.load(join(overlay_path, (seed + '.png'))).convert_alpha() for seed in player.seeds}
        
    def display(self):
        # tools
        tool_surf = self.tools_surfs[self.player.selected_tool]
        tool_rect = tool_surf.get_frect(midbottom = OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)
        
        # seeds
        seed_surf = self.seeds_surfs[self.player.selected_seed]
        seed_rect = seed_surf.get_frect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)