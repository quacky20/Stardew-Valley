from os import walk
from os.path import join
from settings import *

def import_folder(*path):
    surface_list = []
    
    for _, _, file_names in walk(join(*path)):
        for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
            full_path = join(*path, file_name)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
            
    return surface_list

def import_folder_dict(*path):
    surface_dict = {}
    
    for _, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(*path, file_name)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[file_name.split('.')[0]] = image_surf
            
    return surface_dict