import math
import random
import pygame
import json
import os
import numpy as np
from neural_network.neural_network import *
from genetic_algorithms import *
from auxillary import *
from enum import Enum

class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    QUIT = 2

with open("walker_map.json", "r") as f:
    map_data = json.load(f)

with open("first-names.txt", "r") as f:
    first_names = [x.strip() for x in f.readlines()]

#Start parameters
spawn_player = False
spawn_enemy = True
num_enemy = 8
spawn_friendly = True
num_friendly = 8
highscore_size = 6
#scales everything up or down
#scale = 1.5
tile_size = 16
#this seems to have worked out well enough
fps = 30

generation = 0

team_1_color = (50, 50, 250)
team_2_color = (250, 50, 50)

kill_popup_timer = fps * 2


#Generation Parameters
#every generation will end in "hardcap" no matter what, but will end earlier if no kills happen in a "softcap" interval
next_gen_hardcap = 15
next_gen_softcap = 5

hardcap_timer = 0
softcap_timer = 0

kill_announcements = ["Killed", "Neutralized", "Eliminated", "Terminated", "Exterminated", "Eradicated"]
betrayal_announcements = ["Sabotaged", "Betrayed", "Backstabbed", "Doublecrossed", "Tricked", "Deceived"]

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
        self.distance_travelled = 0
        self.transparency = 255
    def collide(self, x, y):
        global softcap_timer
        for character in characters:
            if character is not self.origin:
                if character.rect.colliderect(x, y, self.width, self.height):
                    if character.team == self.origin.team:
                        self.origin.score += friendly_kill_score
                        choice = random.choice(betrayal_announcements)
                    else:
                        self.origin.score += enemy_kill_score
                        choice = random.choice(kill_announcements)
                    kill_feed.append([self.origin, character, kill_popup_timer, choice])
                    characters.remove(character)
                    graveyard.append(character)
                    softcap_timer = 0
                    if self in projectiles:
                        projectiles.remove(self)
                    return True
        for tile in world:
            if tile.passable == False:
                if tile.rect.colliderect(x, y, self.width, self.height):
                    if self in projectiles:
                        projectiles.remove(self)
                    return True
        return False

    def move(self):
        radians = math.radians(self.o)
        dx = self.speed * math.cos(radians)
        dy = self.speed * math.sin(radians)
        if not self.collide(self.rect.x + dx, self.rect.y + dy):
            self.distance_travelled += math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
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
        self.name = random.choice(first_names)
        self.score = 0

        self.shoot_cd = 0
        self.shoot_max_cd = 5

        self.camping_stopwatch = 0
        self.camping_x = 0
        self.camping_y = 0

        self.wall_staring_stopwatch = 0

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
            if self.team == 1:
                bullet_sprite = bullet_img.copy()
            else:
                bullet_sprite = bullet_img2.copy()
            projectiles.append(Projectile(bullet_sprite, spawn_x, spawn_y, self.o, 5 * scale, self))
            self.score = round(self.score + bullet_fired_score, 3)

    
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
        
        collision_data = [0] * (num_lines * 3)

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

            #Terrain, Enemy, Friendly
            collision_data[i] = (scaled_collision_distance if collided_terrain else 0)
            collision_data[num_lines + i] = (scaled_collision_distance if collided_enemy else 0)
            collision_data[num_lines * 2 + i] = (scaled_collision_distance if collided_friendly else 0)

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
    
    def render_name(self):
        if top_performers[0] == self:
            text_surface = font.render(self.name, True, (255, 215, 0))
        else:
            text_surface = font.render(self.name, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.rect.centerx, self.rect.centery + self.height // 2 + 10)
        screen.blit(text_surface, text_rect)
    
class Character(Player):

    def __init__(self, x, y, team, AI):
        super().__init__(x, y, team)
        #randomized starting orientation
        self.o = random.uniform(0, 360)
        self.AI = AI
        self.prediction_cd = 0
        self.prediction_timer = self.prediction_cd
        self.actions = None

    def move(self):
        dx, dy = 0, 0
        if self.prediction_timer >= self.prediction_cd:
            self.actions = self.AI.predict(np.array(self.collision_data))
            self.actions = [min(action_temp[0], 1) for action_temp in self.actions]
            #print(f"input: {self.collision_data}")
            #print(f"output: {self.actions}")
            self.prediction_timer = 0
        else:
            self.prediction_timer += 1

        #Parts of the score system.
        non_zero_count = sum(1 for i in self.collision_data[0:7] if i != 0)
        if non_zero_count > 5:
            self.wall_staring_stopwatch += 1
        else:
            self.wall_staring_stopwatch = 0

        if self.wall_staring_stopwatch >= wall_staring_timer:
            self.score += staring_wall_score

        if self.camping_stopwatch <= 0:
            self.camping_x = self.rect.centerx
            self.camping_y = self.rect.centery

        self.camping_stopwatch += 1

        if self.camping_stopwatch >= camping_timer:
            distance = math.sqrt(math.pow(self.rect.centerx - self.camping_x, 2) + math.pow(self.rect.centery - self.camping_y, 2))
            distance -= camping_cutoff
            self.score += int(distance * movement_reward)
            self.camping_stopwatch = 0

        #print(self.actions)
        turn_decision = self.actions[1] - 0.5
        if turn_decision < 0:
            self.o -= self.turn_speed * abs(turn_decision * 2)
        else:
            self.o += self.turn_speed * abs(turn_decision * 2)

        radians = math.radians(self.o)

        movement_decision = self.actions[0] - 0.5
        if movement_decision < 0:
            dx -= self.speed * math.cos(radians) * abs(movement_decision * 2)
            dy += self.speed * math.sin(radians) * abs(movement_decision * 2)
        else:
            dx += self.speed * math.cos(radians) * abs(movement_decision * 2)
            dy -= self.speed * math.sin(radians) * abs(movement_decision * 2)

        if self.shoot_cd != 0:
            self.shoot_cd -= 1

        if self.actions[2] >= 0.5:
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

    def render_stats(self):

        text_surface = font2.render(f"Selected: {self.name}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale)
        screen.blit(text_surface, text_rect)

        text_surface = font2.render(f"Score: {self.score}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale) + font2_size + font_offset
        screen.blit(text_surface, text_rect)

        text_surface = font2.render(f"Team: {self.team}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale) + font2_size * 2 + font_offset * 2
        screen.blit(text_surface, text_rect)

        text_surface = font2.render(f"Movement Neuron: {round(self.actions[0], 5)}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale) + font2_size * 3 + font_offset * 3
        screen.blit(text_surface, text_rect)

        text_surface = font2.render(f"Turning Neuron: {round(self.actions[1], 5)}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale) + font2_size * 4 + font_offset * 4
        screen.blit(text_surface, text_rect)

        text_surface = font2.render(f"Shooting Neuron: {round(self.actions[2], 5)}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x, text_rect.y = 10, screen_height - (133 * scale) + font2_size * 5 + font_offset * 5
        screen.blit(text_surface, text_rect)

#Parameters
tile_folder = "tiles"
floors_folder = os.path.join(tile_folder, "floors")
walls_folder = os.path.join(tile_folder, "walls")
team1_folder = os.path.join(tile_folder, "T1")
team2_folder = os.path.join(tile_folder, "T2")
projectile_folder = os.path.join(tile_folder, "projectiles")
obstacle_folder = os.path.join(tile_folder, "obstacles")
fonts_folder = "fonts"

#Neural Network Parameters
inputs = 21
hidden = 14
hidden_2 = 7
outputs = 3

width = len(map_data[0])
height = len(map_data)

pygame.init()

#Display setup
display_info = pygame.display.Info()
display_width = display_info.current_w
display_height = display_info.current_h

game_width = width * tile_size
game_height = height * tile_size

scale = min(display_width/game_width, display_height/game_height)

screen_width = game_width * scale
screen_height = game_height * scale
screen = pygame.display.set_mode((screen_width, screen_height))

#Fonts
fontStyle_medieval = os.path.join(fonts_folder, "Alkhemikal.ttf")
font1_size = 10 * int(scale)
font = pygame.font.Font(fontStyle_medieval, font1_size)
font2_size = 14 * int(scale)
font2 = pygame.font.Font(fontStyle_medieval, font2_size)
font3_size = 22 * int(scale)
font3 = pygame.font.Font(fontStyle_medieval, font3_size)
font4_size = 40 * int(scale)
font4 = pygame.font.Font(fontStyle_medieval, font4_size)
font_offset = 4 * scale

#Load images
upscale_factor = math.ceil(tile_size * scale)

innerwall_img = pygame.transform.scale(pygame.image.load(os.path.join(tile_folder, "rock.png")), (upscale_factor, upscale_factor))

floors = []
for floor_img in os.listdir(floors_folder):
    floors.append(pygame.transform.scale(pygame.image.load(os.path.join(floors_folder, floor_img)), (upscale_factor, upscale_factor)))

walls = []
for wall_img in os.listdir(walls_folder):
    walls.append(pygame.transform.scale(pygame.image.load(os.path.join(walls_folder, wall_img)), (upscale_factor, upscale_factor)))

team1_sprites = []
for team1_img in os.listdir(team1_folder):
    team1_sprites.append(pygame.image.load(os.path.join(team1_folder, team1_img)))

team2_sprites = []
for team2_img in os.listdir(team2_folder):
    team2_sprites.append(pygame.image.load(os.path.join(team2_folder, team2_img)))

bullet_img = pygame.image.load(os.path.join(projectile_folder, "bullet.png")).convert_alpha()
bullet_rect = bullet_img.get_rect()
bullet_img = pygame.transform.scale(bullet_img, (bullet_rect.width * scale, bullet_rect.height * scale))

bullet_img2 = pygame.image.load(os.path.join(projectile_folder, "bullet2.png")).convert_alpha()
bullet_rect2 = bullet_img2.get_rect()
bullet_img2 = pygame.transform.scale(bullet_img2, (bullet_rect2.width * scale, bullet_rect2.height * scale))

obstacles = []
for obstacle_image in os.listdir(obstacle_folder):
    obstacle_img = pygame.image.load(os.path.join(obstacle_folder, obstacle_image))
    obstacle_rect = obstacle_img.get_rect()
    obstacle_image = pygame.transform.scale(obstacle_img, (obstacle_rect.width * scale, obstacle_rect.height * scale))
    obstacles.append(obstacle_image)

button_img = pygame.image.load(os.path.join(tile_folder, "button.png"))
button_pressed_img = pygame.image.load(os.path.join(tile_folder, "button_pressed.png"))


game_state = GameState.MAIN_MENU

def set_game_state(x):
    global game_state
    game_state = x

while True:
    while game_state == GameState.MAIN_MENU:
        screen.fill((0, 0, 0))
        titleText = font4.render("NEURAL DUNGEON", True, (255, 255, 255))
        titleRect = titleText.get_rect()
        titleRect.centerx = screen_width / 2
        titleRect.centery = 50 * scale
        screen.blit(titleText, titleRect)

        buttons = []
        startButton_Surface = font2.render("START", True, (255, 255, 255))
        start_button = Button(66 * scale, 33 * scale, screen_width/2, 200 * scale, button_img, button_pressed_img, startButton_Surface, lambda: set_game_state(GameState.PLAYING))
        start_button.draw(screen)
        buttons.append(start_button)

        quitButton_Surface = font2.render("QUIT", True, (255, 255, 255))
        quit_button = Button(66 * scale, 33 * scale, screen_width/2, 250 * scale, button_img, button_pressed_img, quitButton_Surface, lambda: set_game_state(GameState.QUIT))
        quit_button.draw(screen)
        buttons.append(quit_button)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = GameState.QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = GameState.QUIT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for button in buttons:
                    if button.button_rect.collidepoint(mouse_x, mouse_y):
                        button.function()

        pygame.display.flip()

    while game_state == GameState.QUIT:
        pygame.quit()
        exit()

    while game_state == GameState.PLAYING:

        #Score Parameters
        enemy_kill_score = 30
        friendly_kill_score = -40
        bullet_fired_score = -0.1
        time_survived_score = 1
        camping_cutoff = 50 * scale
        camping_timer = 4 * fps
        movement_reward = 0.25

        staring_wall_score = -0.25
        wall_staring_timer = 3 * fps

        projectile_max_distance = tile_size * scale * 6

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
                    #11 and 12 are the exact same due to a refactor. Will change generation code to remove redundancy later but just cba rn. TODO.
                    elif tile == 11:
                        image = random.choice(floors)
                        obstacle_image = random.choice(obstacles)
                        x_offset = (tile_size * scale - obstacle_image.get_width()) // 2
                        y_offset = (tile_size * scale - obstacle_image.get_height()) // 2
                        world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, True))
                        world.append(Tile(obstacle_image, x * tile_size * scale + x_offset, y * tile_size * scale + y_offset, False))
                    elif tile == 12:
                        image = random.choice(floors)
                        obstacle_image = random.choice(obstacles)
                        #obstacle_image = pygame.transform.rotate(obstacle_image, random.randint(0, 360))
                        x_offset = (tile_size * scale - obstacle_image.get_width()) // 2
                        y_offset = (tile_size * scale - obstacle_image.get_height()) // 2
                        world.append(Tile(image, x * tile_size * scale, y * tile_size * scale, True))
                        world.append(Tile(obstacle_image, x * tile_size * scale + x_offset, y * tile_size * scale + y_offset, False))

        def draw_map():
            for tile in world:
                screen.blit(tile.sprite, tile.rect)

        def valid_spawn(world_data):
            valid_spawns = [tile for tile in world_data if tile.passable]
            chosen_spawn = random.choice(valid_spawns)
            return [chosen_spawn.rect.x, chosen_spawn.rect.y]

        def draw_highscore_list(top_performers):
            start_width = 10
            start_height = 10
            for top_performer in top_performers:
                text_surface = font2.render(f"{top_performer.name}: {top_performer.score}", True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.x = start_width
                text_rect.y = start_height
                screen.blit(text_surface, text_rect)
                start_height += font2_size

        def draw_kill_feed(kill_feed: list):
            start_width = screen_width - (133 * scale)
            start_height = 10
            #[killer, victim, timer, adjective]
            kill_feed.sort(key=lambda x: x[2], reverse=False)
            for i in range(len(kill_feed)):
                if kill_feed[i][0].team == 1:
                    color = team_1_color
                else:
                    color = team_2_color
                text_surface = font2.render(f"{kill_feed[i][0].name}", True, color)
                text_rect = text_surface.get_rect()
                text_rect.x = start_width
                text_rect.y = start_height
                screen.blit(text_surface, text_rect)

                text_surface = font2.render(f"{kill_feed[i][3]}", True, (255, 255, 255))
                text_rect = text_surface.get_rect()
                text_rect.x = start_width + font2_size * len(kill_feed[i][0].name) // 3  + 10
                text_rect.y = start_height
                screen.blit(text_surface, text_rect)

                if kill_feed[i][1].team == 1:
                    color = team_1_color
                else:
                    color = team_2_color
                text_surface = font2.render(f"{kill_feed[i][1].name}", True, color)
                text_rect = text_surface.get_rect()
                text_rect.x = start_width + font2_size * len(kill_feed[i][0].name) // 3 + font2_size * len(kill_feed[i][3]) // 3 + (20 * scale)
                text_rect.y = start_height
                screen.blit(text_surface, text_rect)

                kill_feed[i][2] -= 1
                start_height += font2_size

            for kill in kill_feed:
                if kill[2] == 0:
                    kill_feed.remove(kill)

        def reset_world(performers):

            global characters, graveyard, projectiles, kill_feed, softcap_timer, hardcap_timer

            characters = []
            graveyard = []
            projectiles = []
            kill_feed = []

            softcap_timer = 0
            hardcap_timer = 0

            for i in range(len(performers)):
                #allocate teams so they're not too heavily onesided (this does favor blue though, will fix later)
                performers[i].team = (i % 2) + 1
                if performers[i].team == 1:
                    performers[i].image = random.choice(team1_sprites)
                else:
                    performers[i].image = random.choice(team2_sprites)
                performers[i].rect = performers[i].image.get_rect()
                performers[i].image = pygame.transform.scale(performers[i].image, (performers[i].rect.width * scale, performers[i].rect.height * scale))
                performers[i].rect = performers[i].image.get_rect()
                spawn_location = valid_spawn(world)
                performers[i].rect.x = spawn_location[0]
                performers[i].rect.y = spawn_location[1]
                performers[i].score = 0
                characters.append(performers[i])

            if spawn_friendly:
                for i in range(num_friendly - len(performers)//2):
                    spawn_location = valid_spawn(world)
                    characters.append(Character(spawn_location[0], spawn_location[1], 1, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

            if spawn_enemy:
                for i in range(num_enemy - len(performers)//2):
                    spawn_location = valid_spawn(world)
                    characters.append(Character(spawn_location[0], spawn_location[1], 2, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

        world = []
        create_map()

        #TODO: START GENERATIONAL WORK HERE
        characters = []
        graveyard = []
        projectiles = []
        kill_feed = []

        running = True

        #Spawning
        if spawn_player:
            spawn_location = valid_spawn(world)
            characters.append(Player(spawn_location[0], spawn_location[1], 1))

        if spawn_friendly:
            for i in range(num_friendly):
                spawn_location = valid_spawn(world)
                characters.append(Character(spawn_location[0], spawn_location[1], 1, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

        if spawn_enemy:
            for i in range(num_enemy):
                spawn_location = valid_spawn(world)
                characters.append(Character(spawn_location[0], spawn_location[1], 2, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

        top_performers = characters[:highscore_size]
        fps_counter = 0
        #Main loop
        while running:

            buttons = []

            draw_map()
            fps_counter += 1
            for character in characters:
                character.draw_arrow(screen)
                character.move()  
                character.render_name()
                screen.blit(character.image, character.rect)
                if fps_counter == fps:
                    character.score += time_survived_score

            if fps_counter == fps:
                    hardcap_timer += 1
                    softcap_timer += 1
                    fps_counter = 0

            for projectile in projectiles:
                if projectile.distance_travelled > projectile_max_distance:
                    projectile.sprite.fill((255, 255, 255, projectile.transparency), None, pygame.BLEND_RGBA_MULT)
                    projectile.transparency -= 50
                
                if projectile.transparency <= 0:
                    projectiles.remove(projectile)

                projectile.move()
                screen.blit(projectile.sprite, projectile.rect)

            characters[0].draw_sight_lines(screen)
            characters[0].render_stats()

            screen_height - (133 * scale) + font2_size * 6 + font_offset * 6

            text_surface = font2.render("SAVE", True, (255, 255, 255))
            button = Button(66 * scale, 33 * scale, 40 * scale, screen_height - (110 * scale) + font2_size * 6 + font_offset * 6, button_img, button_pressed_img, text_surface, lambda: characters[0].AI.save(f"{characters[0].name}"))
            button.draw(screen)
            buttons.append(button)

            top_performers = sorted(characters + graveyard, key=lambda x: x.score, reverse=True)[:highscore_size]
            draw_highscore_list(top_performers)
            draw_kill_feed(kill_feed)
            
            text_surface = font3.render(f"Generation: {generation}", True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen_width // 2
            text_rect.y = 10
            screen.blit(text_surface, text_rect)

            text_surface = font2.render(f"Soft timer: {softcap_timer} / {next_gen_softcap}", True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen_width // 3.5
            text_rect.y = 10
            screen.blit(text_surface, text_rect)

            text_surface = font2.render(f"Hard timer: {hardcap_timer} / {next_gen_hardcap}", True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.centerx = screen_width // 3.5
            text_rect.y = 10 + font2_size
            screen.blit(text_surface, text_rect)

            if softcap_timer == next_gen_softcap or hardcap_timer == next_gen_hardcap:
                #Genetic Algorithms
                performers = selection(characters, graveyard, 2)

                #pass characters that are going to carry over as parameter into the function
                reset_world(performers)
                generation += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    game_state = GameState.QUIT
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        game_state = GameState.QUIT

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.button_rect.collidepoint(mouse_x, mouse_y):
                            button.function()
                    else:
                        for i in range(len(characters)):
                            if characters[i].rect.collidepoint(mouse_x, mouse_y):
                                characters[i], characters[0] = characters[0], characters[i]
                                break

            pygame.display.update()
            pygame.time.Clock().tick(fps)

        pygame.quit()
