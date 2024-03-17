import pygame
import json
import random

#Load the map data from the JSON file
#with open("walker_map.json", "r") as f:
with open("walker_map.json", "r") as f:
    map_data = json.load(f)

#Parameters
scale = 2
tile_size = 16

width = len(map_data[0])
height = len(map_data)

pygame.init()

#Load images
innerwall_img = pygame.transform.scale(pygame.image.load("rock.png"), (tile_size * scale, tile_size * scale))
floor_img = pygame.transform.scale(pygame.image.load("floor.png"), (tile_size * scale, tile_size * scale))

box_img = pygame.transform.scale(pygame.image.load("box.png"), (tile_size * scale, tile_size * scale))
box_img2 = pygame.transform.scale(pygame.image.load("box2.png"), (tile_size * scale, tile_size * scale))
box_img3 = pygame.transform.scale(pygame.image.load("box3.png"), (tile_size * scale, tile_size * scale))
boxes = [box_img, box_img2, box_img3]

wall_img = pygame.transform.scale(pygame.image.load("wall.png"), (tile_size * scale, tile_size * scale))
pillar_img = pygame.transform.scale(pygame.image.load("pillar.png"), (tile_size * scale, tile_size * scale))

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
                screen.blit(random.choice(boxes), (x * tile_size * scale, y * tile_size * scale))

#Main loop
draw_map()
pygame.display.update()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
