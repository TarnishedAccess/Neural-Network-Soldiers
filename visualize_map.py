import pygame
import json

#Load the map data from the JSON file
with open("walker_map.json", "r") as f:
    map_data = json.load(f)

#Parameters
tile_size = 16

width = len(map_data[0])
height = len(map_data)

pygame.init()

#Load images
innerwall_img = pygame.image.load("rock.png")
floor_img = pygame.image.load("floor.png")
box_img = pygame.image.load("box.png")
wall_img = pygame.image.load("wall.png")

#Display setup
screen_width = width * tile_size
screen_height = height * tile_size
screen = pygame.display.set_mode((screen_width, screen_height))

#Drawing the map
def draw_map():
    for y in range(height):
        for x in range(width):
            tile = map_data[y][x]
            if tile == -1:
                screen.blit(innerwall_img, (x * tile_size, y * tile_size))
            elif tile == 0:
                screen.blit(floor_img, (x * tile_size, y * tile_size))
            elif tile == 1:
                screen.blit(box_img, (x * tile_size, y * tile_size))
            elif tile == 2:
                screen.blit(wall_img, (x * tile_size, y * tile_size))

#Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_map()
    pygame.display.update()

pygame.quit()
