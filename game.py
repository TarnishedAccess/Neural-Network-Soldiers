import math
import pygame
import json
import os

#Load the map data from the JSON file
with open("walker_map.json", "r") as f:
    map_data = json.load(f)

class Character():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "char.png")), (tile_size * scale, tile_size * scale))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3 * scale
        self.turn_speed = 5 * scale
        self.o = 0

    def move(self, map_data):
        dx, dy = 0, 0
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            self.o += self.turn_speed

        if key[pygame.K_RIGHT]:
            self.o -= self.turn_speed

        if key[pygame.K_UP]:

            radians = math.radians(self.o)
            dx += self.speed * math.cos(radians)
            dy -= self.speed * math.sin(radians)

        if key[pygame.K_DOWN]:

            radians = math.radians(self.o)
            dx -= self.speed * math.cos(radians)
            dy += self.speed * math.sin(radians)

        next_x = self.rect.x + dx
        next_y = self.rect.y + dy
        next_tile_x = int((next_x + (3 * scale)) // (tile_size * scale))
        next_tile_y = int((next_y + (3 * scale)) // (tile_size * scale))

        if (map_data[next_tile_y][next_tile_x] == 0):
            self.rect.x = next_x
            self.rect.y = next_y

        #self.rect.x += dx
        #self.rect.y += dy
        print(self.rect.x, self.rect.y, dx, dy)
    
    def draw_arrow(self, screen):

        arrow_length = 20
        radians = math.radians(self.o)
        end_x = self.rect.centerx + arrow_length * math.cos(radians)
        end_y = self.rect.centery - arrow_length * math.sin(radians)

        pygame.draw.line(screen, (255, 0, 0), self.rect.center, (end_x, end_y), 2)
        pygame.draw.polygon(screen, (255, 0, 0), [(end_x, end_y), 
                                                  (end_x - 5 * math.cos(radians + math.pi / 6), end_y + 5 * math.sin(radians + math.pi / 6)),
                                                  (end_x - 5 * math.cos(radians - math.pi / 6), end_y + 5 * math.sin(radians - math.pi / 6))])

#Parameters
tile_folder = "tiles"
scale = 2
tile_size = 16

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

running = True

#Spawning
for i in range(1,height):
    for j in range(1,width):
        if map_data[i][j] == 0:
            character_1 = Character(j*tile_size*scale, i*tile_size*scale)
            break

#Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    draw_map()
    character_1.move(map_data)
    character_1.draw_arrow(screen)
    screen.blit(character_1.image, character_1.rect)
    pygame.display.update()
    pygame.time.Clock().tick(30)

pygame.quit()
