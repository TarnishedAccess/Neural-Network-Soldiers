import pygame
import json
import os

#Load the map data from the JSON file
with open("walker_map.json", "r") as f:
    map_data = json.load(f)

tile_folder = "tiles"

class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "char.png")), (tile_size * scale, tile_size * scale))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3 * scale

    def move(self, map_data):
        dx, dy = 0, 0
        key = pygame.key.get_pressed()
        #For movement, we check both relevant points for collision detection. (ex: to move left, we check both the top left and the bottom left points.)
        if key[pygame.K_LEFT]:

            next_tile_x = (self.rect.x - self.speed + (3*scale)) // (tile_size * scale)
            next_tile_y_TL = (self.rect.y + (4*scale))// (tile_size * scale)
            next_tile_y_BL = (self.rect.y + (12*scale)) // (tile_size * scale)

            if (map_data[next_tile_y_TL][next_tile_x] == 0 and map_data[next_tile_y_BL][next_tile_x] == 0):
                dx -= self.speed

        if key[pygame.K_RIGHT]:

            next_tile_x = (self.rect.x + self.speed + (12*scale)) // (tile_size * scale)
            next_tile_y_TL = (self.rect.y + (4*scale)) // (tile_size * scale)
            next_tile_y_BL = (self.rect.y + (12*scale)) // (tile_size * scale)

            if (map_data[next_tile_y_TL][next_tile_x] == 0 and map_data[next_tile_y_BL][next_tile_x] == 0):
                dx += self.speed

        if key[pygame.K_UP]:

            next_tile_x_TL = (self.rect.x + (3*scale)) // (tile_size * scale)
            next_tile_x_TR = (self.rect.x + (12*scale)) // (tile_size * scale)
            next_tile_y = (self.rect.y - self.speed + (1*scale)) // (tile_size * scale)

            if (map_data[next_tile_y][next_tile_x_TL] == 0 and map_data[next_tile_y][next_tile_x_TR] == 0):
                dy -= self.speed

        if key[pygame.K_DOWN]:

            next_tile_x_TL = (self.rect.x + (3*scale)) // (tile_size * scale)
            next_tile_x_TR = (self.rect.x + (12*scale)) // (tile_size * scale)
            next_tile_y = (self.rect.y + self.speed + (14*scale)) // (tile_size * scale)

            if (map_data[next_tile_y][next_tile_x_TL] == 0 and map_data[next_tile_y][next_tile_x_TR] == 0):
                dy += self.speed

        self.rect.x += dx
        self.rect.y += dy
        print(self.rect.x, self.rect.y, dx, dy)

#Parameters
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
            player = Player(j*tile_size*scale, i*tile_size*scale)
            break

#Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    draw_map()
    player.move(map_data)
    screen.blit(player.image, player.rect)
    pygame.display.update()
    pygame.time.Clock().tick(30)

pygame.quit()
