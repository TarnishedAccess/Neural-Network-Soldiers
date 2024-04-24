import math
import random
import pygame
import json
import os
import numpy as np
from neural_network.neural_creator_scratch import *

with open("walker_map.json", "r") as f:
    map_data = json.load(f)

#Start parameters
spawn_player = False
spawn_enemy = True
num_enemy = 5
spawn_friendly = True
num_friendly = 5

class Tile():
    def __init__(self, sprite, x, y, passable):
        self.sprite = sprite
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.passable = passable

class Projectile():
    def __init__(self, sprite, x, y, o, speed, origin):
        self.sprite = sprite
        self.rect = self.sprite.get_rect()
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.rect.x = x - self.width//2
        self.rect.y = y - self.height//2
        self.o = o
        self.speed = speed
        self.origin = origin

    def collide(self, x, y):
        for character in characters:
            if character is not self.origin:
                if character.rect.colliderect(x, y, self.width, self.height):
                    characters.remove(character)
                    projectiles.remove(self)
                    return True
        for tile in world:
            if tile.passable == False:
                if tile.rect.colliderect(x, y, self.width, self.height):
                    projectiles.remove(self)
                    return True
        return False

    def move(self):
        radians = math.radians(self.o)
        dx = self.speed * math.cos(radians)
        dy = self.speed * math.sin(radians)
        if not self.collide(self.rect.x + dx, self.rect.y + dy):
            self.rect.x += dx
            self.rect.y -= dy

class Player():
    def __init__(self, x, y, team):

        if team == 1:
            self.image = random.choice(team1_sprites)
        else:
            self.image = random.choice(team2_sprites)

        #Do it twice so it updates the hitbox with the new dimensions
        self.rect = self.image.get_rect()
        self.image = pygame.transform.scale(self.image, (self.rect.width * scale, self.rect.height * scale))
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 3 * scale
        self.turn_speed = 5 * scale
        self.o = 0
        self.team = team
        self.collision_data = [0] * 21

        self.shoot_cd = 0
        self.shoot_max_cd = 5

    def move(self):
        dx, dy = 0, 0
        if self.shoot_cd != 0:
            self.shoot_cd -= 1

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

        if key[pygame.K_SPACE]:
            self.shoot()

        for tile in world:
            #Collision detection.
            #TODO: There's a bug here somewhere.
            if tile.passable == False:
                if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                elif tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = 0

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cd == 0:
            self.shoot_cd = self.shoot_max_cd
            radians = math.radians(self.o)
            spawn_x = self.rect.centerx + 15 * math.cos(radians)
            spawn_y = self.rect.centery - 15 * math.sin(radians)
            projectiles.append(Projectile(bullet_img, spawn_x, spawn_y, self.o, 5 * scale, self))

    
    #front-facing arrow
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
        #line properties
        line_length = 6 * tile_size * scale
        num_lines = 7
        angle_offset = 15
        starting_offset = self.o - (num_lines // 2) * angle_offset

        red = (255, 0, 0)
        white = (255, 255, 255)
        blue = (0, 0, 255)
        green = (0, 255, 0)
        
        collision_data = []

        for i in range(num_lines):

            radians = math.radians(starting_offset + angle_offset * i)
            end_x = self.rect.centerx
            end_y = self.rect.centery
            color = white

            num_segments = 20

            dx = line_length * math.cos(radians) / num_segments
            dy = line_length * math.sin(radians) / num_segments

            collided_friendly = collided_enemy = collided_terrain = False

            for j in range(num_segments):
                if collided_enemy or collided_friendly or collided_terrain:
                    break
                
                #More or less so that the ray stops at the first object hit
                end_x += line_length // num_segments * math.cos(radians)
                end_y -= line_length // num_segments * math.sin(radians)

                x = self.rect.centerx + j * dx
                y = self.rect.centery - j * dy

                #Terrain detection
                for tile in world:
                    if not tile.passable:
                        if tile.rect.collidepoint(int(x), int(y)):
                            collided_terrain = True
                            color = blue
                            break

                for character in characters:
                    if character is not self:
                        #Friendly detection
                        if character.rect.collidepoint(int(x), int(y)) and character.team == self.team:
                            collided_friendly = True
                            color = green
                            break

                        #Enemy detection
                        if character.rect.collidepoint(int(x), int(y)) and character.team != self.team:
                            collided_enemy = True
                            color = red
                            break
            
            collision_distance = math.sqrt((end_x - self.rect.centerx)**2 + (end_y - self.rect.centery)**2)
            max_collision_distance = 80
            scaled_collision_distance = collision_distance / max_collision_distance

            data = []
            data.append(scaled_collision_distance if collided_enemy else 0)
            data.append(scaled_collision_distance if collided_friendly else 0)
            data.append(scaled_collision_distance if collided_terrain else 0)
            #(E, F, T)

            collision_data.extend(data)

            pygame.draw.line(screen, color, self.rect.center, (end_x, end_y), 2)
        self.collision_data = collision_data

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
    
class Character(Player):

    def __init__(self, x, y, team, AI):
        super().__init__(x, y, team)
        #randomized starting orientation
        self.o = random.uniform(0, 360)
        self.AI = AI
        self.prediction_cd = 2
        self.prediction_timer = self.prediction_cd
        self.actions = None

    def move(self):
        dx, dy = 0, 0
        if self.prediction_timer == self.prediction_cd:
            self.actions = self.AI.predict(np.array(self.collision_data))
            print(f"input: {self.collision_data}")
            print(f"output: {self.actions}")
            self.prediction_timer = 0
        else:
            self.prediction_timer += 1

        print(self.actions)
        turn_decision = self.actions[1][0] - 0.5
        if turn_decision < 0:
            self.o -= self.turn_speed * abs(turn_decision * 2)
        else:
            self.o += self.turn_speed * abs(turn_decision * 2)

        """
        if self.actions[0][1] <= 0.33:
            self.o -= self.turn_speed
        elif self.actions[0][1] >= 0.66:
            self.o += self.turn_speed
        """

        radians = math.radians(self.o)

        """
        if self.actions[0][0] <= 0.33:
            dx -= self.speed * math.cos(radians)
            dy += self.speed * math.sin(radians)
        elif self.actions[0][0] >= 0.66:
            dx += self.speed * math.cos(radians)
            dy -= self.speed * math.sin(radians)
        """
        movement_decision = self.actions[0][0] - 0.5
        if movement_decision < 0:
            dx -= self.speed * math.cos(radians) * abs(movement_decision * 2)
            dy += self.speed * math.sin(radians) * abs(movement_decision * 2)
        else:
            dx += self.speed * math.cos(radians) * abs(movement_decision * 2)
            dy -= self.speed * math.sin(radians) * abs(movement_decision * 2)

        if self.shoot_cd != 0:
            self.shoot_cd -= 1

        if self.actions[2][0] <= 0.5:
            Character.shoot(self)

        for tile in world:
            #Collision detection.
            #TODO: There's a bug here somewhere.
            if tile.passable == False:
                if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                elif tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = 0

        self.rect.x += dx
        self.rect.y += dy
        
        #placeholder movement function for AIs that is just completely random movement

#Parameters
tile_folder = "tiles"
floors_folder = os.path.join(tile_folder, "floors")
walls_folder = os.path.join(tile_folder, "walls")
team1_folder = os.path.join(tile_folder, "T1")
team2_folder = os.path.join(tile_folder, "T2")

#scales everything up or down
scale = 2
tile_size = 16
#this seems to have worked out well enough
fps = 60

#Neural Network Parameters
inputs = 21
hidden = 14
outputs = 3

width = len(map_data[0])
height = len(map_data)

pygame.init()

font = pygame.font.Font(None, 13)

#Load images
innerwall_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "rock.png")), (tile_size * scale, tile_size * scale))

floors = []
for floor_img in os.listdir(floors_folder):
    floors.append(pygame.transform.scale(pygame.image.load(os.path.join(floors_folder, floor_img)), (tile_size * scale, tile_size * scale)))

walls = []
for wall_img in os.listdir(walls_folder):
    walls.append(pygame.transform.scale(pygame.image.load(os.path.join(walls_folder, wall_img)), (tile_size * scale, tile_size * scale)))

team1_sprites = []
for team1_img in os.listdir(team1_folder):
    team1_sprites.append(pygame.image.load(os.path.join(team1_folder, team1_img)))

team2_sprites = []
for team2_img in os.listdir(team2_folder):
    team2_sprites.append(pygame.image.load(os.path.join(team2_folder, team2_img)))

bullet_img = pygame.image.load(os.path.join(tile_folder, "bullet.png"))
bullet_rect = bullet_img.get_rect()
bullet_img = pygame.transform.scale(bullet_img, (bullet_rect.width * scale, bullet_rect.height * scale))

box_img = pygame.image.load(os.path.join(tile_folder, "box.png"))
box_rect = box_img.get_rect()
box_img = pygame.transform.scale(box_img, (box_rect.width * scale, box_rect.height * scale))

pillar_img = pygame.image.load(os.path.join(tile_folder, "pillar.png"))
pillar_rect = pillar_img.get_rect()
pillar_img = pygame.transform.scale(pillar_img, (pillar_rect.width * scale, pillar_rect.height * scale))

#Display setup
screen_width = width * tile_size * scale
screen_height = height * tile_size * scale
screen = pygame.display.set_mode((screen_width, screen_height))

world = []
characters = []
projectiles = []

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
                image = random.choice(floors)
                x_offset = (tile_size * scale - pillar_img.get_width()) // 2
                y_offset = (tile_size * scale - pillar_img.get_height()) // 2
                world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, True))
                world.append(Tile(pillar_img, x * tile_size * scale + x_offset, y * tile_size * scale + y_offset, False))
            elif tile == 12:
                image = random.choice(floors)
                x_offset = (tile_size * scale - box_img.get_width()) // 2
                y_offset = (tile_size * scale - box_img.get_height()) // 2
                world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, True))
                world.append(Tile(box_img, x * tile_size * scale + x_offset, y * tile_size * scale + y_offset, False))

def draw_map():
    for tile in world:
        screen.blit(tile.sprite, tile.rect)

def valid_spawn(world_data):
    valid_spawns = [tile for tile in world_data if tile.passable]
    chosen_spawn = random.choice(valid_spawns)
    return [chosen_spawn.rect.x, chosen_spawn.rect.y]

running = True
create_map()

#Spawning
if spawn_player:
    spawn_location = valid_spawn(world)
    characters.append(Player(spawn_location[0], spawn_location[1], 1))

if spawn_friendly:
    for i in range(num_friendly):
        spawn_location = valid_spawn(world)
        characters.append(Character(spawn_location[0], spawn_location[1], 1, NeuralNetwork(inputs, hidden, outputs)))

if spawn_enemy:
    for i in range(num_enemy):
        spawn_location = valid_spawn(world)
        characters.append(Character(spawn_location[0], spawn_location[1], 2, NeuralNetwork(inputs, hidden, outputs)))
                
#Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            print(mouse_x, mouse_y)
            for i in range(len(characters)):
                if characters[i].rect.collidepoint(mouse_x, mouse_y):
                    characters[i], characters[0] = characters[0], characters[i]
                    break

    draw_map()

    for character in characters:
        character.draw_arrow(screen)
        character.move()  
        screen.blit(character.image, character.rect)

    for projectile in projectiles:
        projectile.move()
        screen.blit(projectile.sprite, projectile.rect)

    characters[0].draw_sight_lines(screen)

    #---Debugging---
    #pygame.draw.rect(screen, (0, 255, 0), player_1.rect, 2)
    #for i in world:
    #    if i.passable:
    #        pygame.draw.rect(screen, (255, 255, 255), i.rect, 2)
    #    else:
    #        pygame.draw.rect(screen, (255, 0, 0), i.rect, 2)
    #---------------
    
    pygame.display.update()
    pygame.time.Clock().tick(fps)

pygame.quit()
