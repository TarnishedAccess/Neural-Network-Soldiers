import pygame
import json
import os

#Load the map data from the JSON file
#with open("walker_map.json", "r") as f:
with open("walker_map.json", "r") as f:
    map_data = json.load(f)

#Parameters
scale = 1
tile_size = 16
tile_folder = "tiles"

width = len(map_data[0])
height = len(map_data)

pygame.init()

#Load images
innerwall_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "rock.png")), (tile_size * scale, tile_size * scale))
floor_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "floor.png")), (tile_size * scale, tile_size * scale))

box_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "box.png")), (tile_size * scale, tile_size * scale))

wall_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "wall.png")), (tile_size * scale, tile_size * scale))
pillar_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "pillar.png")), (tile_size * scale, tile_size * scale))

#Display setup
display_info = pygame.display.Info()
screen_width = width * tile_size * scale
screen_height = height * tile_size * scale
screen = pygame.display.set_mode((screen_width, screen_height))

#Drawing the map
def draw_map():
    for y in range(height):
        for x in range(width):
            tile = map_data[y][x]
            if tile == -1:
                screen.blit(innerwall_img, (x * tile_size * scale, y * tile_size * scale))
            elif tile == 0:
                screen.blit(floor_img, (x * tile_size * scale, y * tile_size * scale))
            elif tile == 2:
                screen.blit(wall_img, (x * tile_size * scale, y * tile_size * scale))
            elif tile == 11:
                screen.blit(pillar_img, (x * tile_size * scale, y * tile_size * scale))
            elif tile == 12:
                screen.blit(box_img, (x * tile_size * scale, y * tile_size * scale))

#Main loop
draw_map()
pygame.display.update()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
