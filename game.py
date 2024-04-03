import math
import random
import pygame
import json
import os

with open("walker_map.json", "r") as f:
    map_data = json.load(f)

class Tile():
    def __init__(self, sprite, x, y, passable):
        self.sprite = sprite
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passable = passable

class Character():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "char.png")), (tile_size * scale, tile_size * scale))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 3 * scale
        self.turn_speed = 5 * scale
        self.o = 0

    def move(self):
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

        for tile in world:
            if tile.passable == False:
                if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                elif tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = 0

        self.rect.x += dx
        self.rect.y += dy
    
    def draw_arrow(self, screen):

        arrow_length = 20
        radians = math.radians(self.o)
        end_x = self.rect.centerx + arrow_length * math.cos(radians)
        end_y = self.rect.centery - arrow_length * math.sin(radians)

        pygame.draw.line(screen, (255, 0, 0), self.rect.center, (end_x, end_y), 2)
        pygame.draw.polygon(screen, (255, 0, 0), [(end_x, end_y), 
                                                  (end_x - 5 * math.cos(radians + math.pi / 6), end_y + 5 * math.sin(radians + math.pi / 6)),
                                                  (end_x - 5 * math.cos(radians - math.pi / 6), end_y + 5 * math.sin(radians - math.pi / 6))])

    def draw_sight_lines(self, screen):
        collision_data = []

        #line properties
        line_length = 3 * tile_size * scale
        num_lines = 7
        angle_offset = 15
        starting_offset = self.o - (num_lines // 2) * angle_offset
        
        for i in range(num_lines):
            radians = math.radians(starting_offset + angle_offset * i)
            end_x = self.rect.centerx + line_length * math.cos(radians)
            end_y = self.rect.centery - line_length * math.sin(radians)
            #green by default, turns red if it collides
            color = (0, 255, 0)
            num_segments = 10

            dx = line_length * math.cos(radians) / num_segments
            dy = line_length * math.sin(radians) / num_segments

            collided = False
            for j in range(num_segments):
                x = self.rect.centerx + j * dx
                y = self.rect.centery - j * dy

                #if a segment of the line collides with a tile, the entire line turns red
                for tile in world:
                    if not tile.passable:
                        if tile.rect.collidepoint(int(x), int(y)):
                            collided = True
                            color = (255, 0, 0)
                            break
                if collided:
                    collision_data.append(0)
                    break
            #this check could probably be done better as there's some redundancy but its minor and I dont care enough to fix it
            if not collided:
                collision_data.append(1)
                #print 1 if it does not collide, 0 if it does. This is just a minor test, will add distance and such later.
            
            pygame.draw.line(screen, color, self.rect.center, (end_x, end_y), 2)
        print(collision_data)

    def line_intersects_rect(self, x1, y1, x2, y2, rect):
        rx1, ry1, rx2, ry2 = rect.x, rect.y, rect.x + rect.width, rect.y + rect.height

        #pygame probably has a collision function for lines and rectangles but they're easy enough to make so might as well
        return (
            self.line_intersects_line(x1, y1, x2, y2, rx1, ry1, rx2, ry1) or
            self.line_intersects_line(x1, y1, x2, y2, rx2, ry1, rx2, ry2) or
            self.line_intersects_line(x1, y1, x2, y2, rx2, ry2, rx1, ry2) or
            self.line_intersects_line(x1, y1, x2, y2, rx1, ry2, rx1, ry1)
        )

    #whole lotta math that i just straight up copied from some documentation i am not that smart
    def line_intersects_line(self, x1, y1, x2, y2, x3, y3, x4, y4):
        denominator = (x4 - x3) * (y1 - y2) - (y4 - y3) * (x1 - x2)
        if denominator != 0:
            numerator1 = (x3 * y4 - x4 * y3) * (x1 - x2) - (x1 * y2 - x2 * y1) * (x3 - x4)
            numerator2 = (x3 * y4 - x4 * y3) * (y1 - y2) - (x1 * y2 - x2 * y1) * (y3 - y4)
            return (numerator1 / denominator, numerator2 / denominator) in ((0, 1), (1, 0))
        return False

#Parameters
tile_folder = "tiles"
floors_folder = os.path.join(tile_folder, "floors")
walls_folder = os.path.join(tile_folder, "walls")

scale = 2
tile_size = 16

width = len(map_data[0])
height = len(map_data)

pygame.init()

#Load images
innerwall_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "rock.png")), (tile_size * scale, tile_size * scale))

floors = []
for floor_img in os.listdir(floors_folder):
    floors.append(pygame.transform.scale(pygame.image.load(os.path.join(floors_folder, floor_img)), (tile_size * scale, tile_size * scale)))

walls = []
for wall_img in os.listdir(walls_folder):
    walls.append(pygame.transform.scale(pygame.image.load(os.path.join(walls_folder, wall_img)), (tile_size * scale, tile_size * scale)))

box_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "box.png")), (tile_size * scale, tile_size * scale))
pillar_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "pillar.png")), (tile_size * scale, tile_size * scale))

#Display setup
screen_width = width * tile_size * scale
screen_height = height * tile_size * scale
screen = pygame.display.set_mode((screen_width, screen_height))

world = []

#Drawing the map
def create_map():
    for y in range(height):
        for x in range(width):
            tile = map_data[y][x]

            if tile == -1:
                world.append(Tile(innerwall_img, x * tile_size * scale, y * tile_size * scale, False))
            elif tile == 0:
                image = random.choice(floors)
                world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, True))
            elif tile == 2:
                image = random.choice(walls)
                world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, False))
            elif tile == 11:
                world.append(Tile(pillar_img, x * tile_size * scale, y * tile_size * scale, False))
            elif tile == 12:
                world.append(Tile(box_img, x * tile_size * scale, y * tile_size * scale, False))

def draw_map():
    for tile in world:
        screen.blit(tile.sprite, tile.rect)

running = True
create_map()
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

    draw_map()
    character_1.move()
    screen.blit(character_1.image, character_1.rect)
    character_1.draw_sight_lines(screen)
    #---Debugging---
    pygame.draw.rect(screen, (0, 255, 0), character_1.rect, 2)
    #for i in world:
    #    if i.passable:
    #        pygame.draw.rect(screen, (255, 255, 255), i.rect, 2)
    #    else:
    #        pygame.draw.rect(screen, (255, 0, 0), i.rect, 2)
    #---------------
    character_1.draw_arrow(screen)
    pygame.display.update()
    pygame.time.Clock().tick(30)

pygame.quit()
