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

with open("walker_map.json", "r") as f:
    map_data = json.load(f)

with open("first-names.txt", "r") as f:
    first_names = [x.strip() for x in f.readlines()]

#Start parameters
spawn_player = False
spawn_enemy = True
num_enemy = 25
spawn_friendly = True
num_friendly = 25
highscore_size = 6
elite_num = 8
selection_num = 30
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
next_gen_hardcap = 8
next_gen_softcap = 4

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

    def save(self, filename):
        datetime_now = datetime.now()
        formatted_date = datetime_now.strftime("%d/%m/%Y")
        datetime_now = datetime_now.strftime("%Y%m%d%H%M%S")
        save_path = os.path.join("neural_network", "network_storage", filename)
        data = {
            "name": self.name,
            "time_created": formatted_date,
            "network": self.AI.toList()
        }
        with open(f"{save_path}_{datetime_now}.json", "w") as network_file:
            json.dump(data, network_file)

#Parameters
tile_folder = "tiles"
floors_folder = os.path.join(tile_folder, "floors")
walls_folder = os.path.join(tile_folder, "walls")
team1_folder = os.path.join(tile_folder, "T1")
team2_folder = os.path.join(tile_folder, "T2")
projectile_folder = os.path.join(tile_folder, "projectiles")
obstacle_folder = os.path.join(tile_folder, "obstacles")
fonts_folder = "fonts"
audio_folder = "audio"
network_storage_folder = os.path.join("neural_network", "network_storage")

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

def load_spritesheet(filename, width, height):
    spritesheet = pygame.image.load(filename).convert_alpha()
    image_list = []
    for y in range(0, spritesheet.get_height(), height):
        for x in range(0, spritesheet.get_width(), width):
            image = spritesheet.subsurface((x, y, width, height))
            image = pygame.transform.scale(image, (64 * scale, 64 * scale))
            image_list.append(image)
    return image_list[:len(image_list)-1]

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

text_plate_img = pygame.image.load(os.path.join(tile_folder, "Plate.png"))

animated_torch = load_spritesheet(os.path.join(tile_folder, "torch_anim.png"), 16, 16)

menu_background = pygame.image.load(os.path.join(tile_folder, "menu_background.png"))
image_width, image_height = menu_background.get_size()
screen_width, screen_height = screen.get_size()
scale_x = screen_width / image_width
scale_y = screen_height / image_height
#scale_factor = min(scale_x, scale_y)
menu_background = pygame.transform.scale(menu_background, (int(image_width * scale_x), image_height * scale_y))
menu_background_rect = menu_background.get_rect()
menu_background_rect.x = 0
menu_background_rect.y = 0

small_image = pygame.transform.smoothscale(menu_background, (menu_background.get_width() // 6, menu_background.get_height() // 6))
menu_background = pygame.transform.smoothscale(small_image, (int(image_width * scale_x), image_height * scale_y))

class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    BANK = 2
    DUNGEONS = 3
    QUIT = 4

game_state = GameState.MAIN_MENU
transitioning = False
transitioning_target = None
fade_speed = 0.5
fade_alpha = 255
current_music_file = None

def set_game_state(x):
    #global game_state
    global transitioning
    global transitioning_target
    transitioning = True
    transitioning_target = x

def play_music(state):
    global current_music_file
    music_mapping = {
        GameState.MAIN_MENU: os.path.join(audio_folder, "menu_theme.mp3"),
        GameState.PLAYING: os.path.join(audio_folder, "game_theme.mp3"),
        GameState.BANK: os.path.join(audio_folder, "bank_theme.mp3"),
        GameState.DUNGEONS: os.path.join(audio_folder, "dungeon_theme.mp3"),
        GameState.QUIT: None
    }
    music_file = music_mapping.get(state)
    if music_file != current_music_file:
        if music_file is not None:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
        current_music_file = music_file

selected_blue = []
selected_red = []

while True:
    if not transitioning:
        fade_alpha = 255
        volume = 0.1
        pygame.mixer.music.set_volume(0.1)
    torch_state = 0
    menu_timer = 0
    #this has to be the single worst way of doing this but i genuinely just do not care to refactor it atp

    while game_state == GameState.MAIN_MENU:
        play_music(game_state)
        menu_timer += 1
        screen.fill((0, 0, 0))
        screen.blit(menu_background, menu_background_rect)
        torch1_rect = animated_torch[torch_state].get_rect()
        torch1_rect.centerx, torch1_rect.centery = screen_width / 2 - 120 * scale, 50 * scale
        torch2_rect = animated_torch[torch_state].get_rect()
        torch2_rect.centerx, torch2_rect.centery = screen_width / 2 + 120 * scale, 50 * scale
        screen.blit(animated_torch[torch_state], torch1_rect)
        screen.blit(animated_torch[torch_state], torch2_rect)

        if menu_timer == fps//8:
            torch_state = (torch_state + 1) % len(animated_torch)
        titleText = font4.render("NEURAL DUNGEON", True, (20, 20, 20))
        titleRect = titleText.get_rect()
        titleRect.centerx = screen_width / 2
        titleRect.centery = 50 * scale

        buttons = []
        startButton_Surface = font2.render("Start", True, (255, 255, 255))
        start_button = Button(66 * scale, 33 * scale, screen_width/2, 200 * scale, button_img, button_pressed_img, startButton_Surface, lambda: set_game_state(GameState.PLAYING), False, os.path.join(audio_folder, "start_sound.mp3"))
        buttons.append(start_button)

        bankButton_Surface = font2.render("Neural Bank", True, (255, 255, 255))
        bank_button = Button(66 * scale, 33 * scale, screen_width/2, 250 * scale, button_img, button_pressed_img, bankButton_Surface, lambda: set_game_state(GameState.BANK), False, os.path.join(audio_folder, "bank_sound.mp3"))
        buttons.append(bank_button)

        dungeonButton_Surface = font2.render("Dungeons", True, (255, 255, 255))
        dungeon_button = Button(66 * scale, 33 * scale, screen_width/2, 300 * scale, button_img, button_pressed_img, dungeonButton_Surface, lambda: set_game_state(GameState.DUNGEONS), False, os.path.join(audio_folder, "dungeon_sound.mp3"))
        buttons.append(dungeon_button)

        quitButton_Surface = font2.render("Quit", True, (255, 255, 255))
        quit_button = Button(66 * scale, 33 * scale, screen_width/2, 350 * scale, button_img, button_pressed_img, quitButton_Surface, lambda: set_game_state(GameState.QUIT), False, os.path.join(audio_folder, "quit_sound.wav"))
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
                        button.play_sound()
                        button.function()

        elements = [titleText, menu_background, animated_torch[torch_state]]
        for button in buttons:
            elements.extend([button.button_sprite_pressed, button.button_sprite_notPressed, button.text_surface])
        if transitioning:
            if fade_alpha != 0:
                for element in elements:
                    fade_alpha = max(0, fade_alpha - fade_speed)
                    element.set_alpha(fade_alpha)
                volume -= 0.001
                pygame.mixer.music.set_volume(volume)
            else:
                game_state = transitioning_target
                transitioning = False
                break
        else:
            for element in elements:
                element.set_alpha(255)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            if button.button_rect.collidepoint(mouse_x, mouse_y):
                button.hovered = True
            button.draw(screen)
        screen.blit(titleText, titleRect)
        pygame.time.Clock().tick(fps)
        pygame.display.flip()
        if menu_timer == fps//8:
            menu_timer = 0

    while game_state == GameState.QUIT:
        pygame.quit()
        exit()

    selected_AI = None
    def assign_selected_AI(i):
        global selected_AI
        selected_AI = characters_data[i]

    def remove_from_blue(i):
        global selected_blue
        selected_blue.pop(i)

    def remove_from_red(i):
        global selected_red
        selected_red.pop(i)

    while game_state == GameState.BANK:
        play_music(game_state)
        screen.fill((157, 124, 13))
        buttons = []
        character_button_width = screen_width // 3 // 4
        character_button_height = screen_height // 3 // 6

        bank_surface = font4.render('Neural Bank', True, (255, 255, 255))
        bank_plate = TextPlate(300, 100, screen_width // 2, 50 * scale, text_plate_img, bank_surface)
        bank_plate.draw(screen)

        i = 0
        start_pos_x = character_button_width // 2 + 10 * scale
        start_pos_y = 100 * scale + character_button_height // 2

        character_description_x = screen_width // 3 * 2 + (screen_width // 6)

        characters_data = []
        for network in os.listdir(network_storage_folder):
            network_path = os.path.join(network_storage_folder, network)
            with open(network_path, "r") as file:
                character_data = json.load(file)
            characters_data.append(character_data)
            text_surface = font2.render(character_data['name'], True, (255, 255, 255))
            character_button = Button(character_button_width, character_button_height, start_pos_x + character_button_width * (i % 7), start_pos_y + character_button_height * (i // 7), button_img, button_pressed_img, text_surface, lambda i=i: assign_selected_AI(i), False, None)
            buttons.append(character_button)
            i += 1

        selectedText = font3.render("Selected AI", True, (20, 20, 20))
        selectedRect = selectedText.get_rect()
        selectedRect.centerx = character_description_x
        selectedRect.centery = 100 * scale + character_button_height // 2
        screen.blit(selectedText, selectedRect)

        if selected_AI == None:
            selectedText = font3.render("No AI Selected", True, (20, 20, 20))
            selectedRect = selectedText.get_rect()
            selectedRect.centerx = character_description_x
            selectedRect.centery = 130 * scale + character_button_height // 2
            screen.blit(selectedText, selectedRect)
        else:
            selectedText = font3.render(f"Name: {selected_AI['name']}", True, (20, 20, 20))
            selectedRect = selectedText.get_rect()
            selectedRect.centerx = character_description_x
            selectedRect.centery = 120 * scale + character_button_height // 2
            screen.blit(selectedText, selectedRect)

            selectedText = font3.render(f"Created: {selected_AI['time_created']}", True, (20, 20, 20))
            selectedRect = selectedText.get_rect()
            selectedRect.centerx = character_description_x
            selectedRect.centery = 140 * scale + character_button_height // 2
            screen.blit(selectedText, selectedRect)

            text_surface = font2.render('Add to Red', True, (255, 255, 255))
            addToRed_Button = Button(character_button_width, character_button_height, character_description_x, 150 * scale + character_button_height, button_img, button_pressed_img, text_surface, lambda: selected_red.append(selected_AI) if len(selected_red) < 8 else None, False, None)
            buttons.append(addToRed_Button)

            text_surface = font2.render('Add to Blue', True, (255, 255, 255))
            addToBlue_Button = Button(character_button_width, character_button_height, character_description_x, 155 * scale + character_button_height * 2, button_img, button_pressed_img, text_surface, lambda: selected_blue.append(selected_AI) if len(selected_blue) < 8 else None, False, None)
            buttons.append(addToBlue_Button)

        redTeamText = font3.render("Red Team:", True, (20, 20, 20))
        redTeamRect = redTeamText.get_rect()
        redTeamRect.centerx = 60 * scale
        redTeamRect.centery = screen_height // 3 * 2 + 50 * scale
        screen.blit(redTeamText, redTeamRect)

        blueTeamText = font3.render("Blue Team:", True, (20, 20, 20))
        blueTeamRect = blueTeamText.get_rect()
        blueTeamRect.centerx = 60 * scale
        blueTeamRect.centery =  screen_height // 3 * 2 + 100 * scale
        screen.blit(blueTeamText, blueTeamRect)

        x = 0
        for blue_member in selected_blue:
            text_surface = font2.render(blue_member['name'], True, (255, 255, 255))
            character_button = Button(character_button_width, character_button_height, 120 * scale + (character_button_width + 5)* x, screen_height // 3 * 2 + 100 * scale, button_img, button_pressed_img, text_surface, lambda x=x: remove_from_blue(x), False, None)
            buttons.append(character_button)
            x += 1

        x = 0
        for red_member in selected_red:
            text_surface = font2.render(red_member['name'], True, (255, 255, 255))
            character_button = Button(character_button_width, character_button_height, 120 * scale + (character_button_width + 5)* x, screen_height // 3 * 2 + 50 * scale, button_img, button_pressed_img, text_surface, lambda x=x: remove_from_red(x), False, None)
            buttons.append(character_button)
            x += 1

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            if button.button_rect.collidepoint(mouse_x, mouse_y):
                button.hovered = True
            button.draw(screen)

        #print(selected_AI)
        pygame.display.update()

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = GameState.QUIT
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.MAIN_MENU        
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for button in buttons:
                        if button.button_rect.collidepoint(mouse_x, mouse_y):
                            button.play_sound()
                            button.function()

    while game_state == GameState.DUNGEONS:
        play_music(game_state)
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = GameState.QUIT

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = GameState.MAIN_MENU

    while game_state == GameState.PLAYING:
        play_music(game_state)
        #Score Parameters
        map_center_y = screen_height//2
        enemy_kill_score = 30
        friendly_kill_score = -50
        bullet_fired_score = -0.1
        time_survived_score = 1
        camping_cutoff = 55 * scale
        camping_timer = 2 * fps
        movement_reward = 0.1
        aggression_reward = 0.05

        staring_wall_score = -1
        wall_staring_timer = 2 * fps

        projectile_max_distance = tile_size * scale * 5

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

        def valid_spawn_team1(world_data):
            world_size = len(world_data)
            cutoff = world_size // 3
            valid_spawns = [tile for tile in world_data[:cutoff] if tile.passable]
            chosen_spawn = random.choice(valid_spawns)
            return [chosen_spawn.rect.x, chosen_spawn.rect.y]
        
        def valid_spawn_team2(world_data):
            world_size = len(world_data)
            cutoff = world_size // 3
            valid_spawns = [tile for tile in world_data[cutoff * 2:] if tile.passable]
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
                    spawn_location = valid_spawn_team1(world)
                else:
                    performers[i].image = random.choice(team2_sprites)
                    spawn_location = valid_spawn_team2(world)
                performers[i].rect = performers[i].image.get_rect()
                performers[i].image = pygame.transform.scale(performers[i].image, (performers[i].rect.width * scale, performers[i].rect.height * scale))
                performers[i].rect = performers[i].image.get_rect()
                performers[i].rect.x = spawn_location[0]
                performers[i].rect.y = spawn_location[1]
                performers[i].score = 0
                performers[i].camping_stopwatch = 0
                performers[i].camping_x = 0
                performers[i].camping_y = 0
                performers[i].wall_staring_stopwatch = 0
                characters.append(performers[i])

            if spawn_friendly:
                for i in range(num_friendly - len(performers)//2):
                    spawn_location = valid_spawn_team1(world)
                    characters.append(Character(spawn_location[0], spawn_location[1], 1, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

            if spawn_enemy:
                for i in range(num_enemy - len(performers)//2):
                    spawn_location = valid_spawn_team2(world)
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
                spawn_location = valid_spawn_team1(world)
                characters.append(Character(spawn_location[0], spawn_location[1], 1, NeuralNetwork(inputs, hidden, hidden_2, outputs)))

        if spawn_enemy:
            for i in range(num_enemy):
                spawn_location = valid_spawn_team2(world)
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
                    if character.team == 1:
                        character.score += (character.rect.y - map_center_y) * aggression_reward
                    elif character.team == 2:
                        character.score += (map_center_y - character.rect.y) * aggression_reward
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
            button = Button(66 * scale, 33 * scale, 40 * scale, screen_height - (110 * scale) + font2_size * 6 + font_offset * 6, button_img, button_pressed_img, text_surface, lambda: characters[0].save(f"{characters[0].name}"), False, None)
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
                combined_characters = characters + graveyard
                combined_characters.sort(key=lambda character: character.score, reverse=True)

                #First portion of the new generation: top 2
                elite = combined_characters[:elite_num]
                for character in elite:
                    combined_characters.remove(character)

                #Second portion of the new generation: 8 crossovers
                performers = selection(combined_characters, selection_num)
                crossedChildren = []
                while len(performers) != 0:
                    parents = random.sample(performers, k=2)
                    siblings = crossing(parents[0].AI.toList(), parents[1].AI.toList())
                    sibling_1_AI = NeuralNetwork(inputs, hidden, hidden_2, outputs)
                    sibling_1_AI.load(*siblings[0])
                    #Position and team don't matter they'll all get reset anyway.
                    crossedChildren.append(Character(1, 1, 1, sibling_1_AI))
                    sibling_2_AI = NeuralNetwork(inputs, hidden, hidden_2, outputs)
                    sibling_2_AI.load(*siblings[1])
                    crossedChildren.append(Character(1, 1, 1, sibling_2_AI))
                    for parent in parents:
                        performers.remove(parent)

                #Mutate half of the children:
                for i in range(len(crossedChildren)//2):
                    #minimum of 2 mutations, max of 5
                    child_AI = crossedChildren[i].AI.toList()
                    mutate(child_AI, 2, 5)
                    crossedChildren[i].AI.load(*child_AI)
                #The remaining 6 characters will be randomly generated.
                reset_world(elite + crossedChildren)
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

            mouse_x, mouse_y = pygame.mouse.get_pos()
            for button in buttons:
                if button.button_rect.collidepoint(mouse_x, mouse_y):
                    button.hovered = True
                button.draw(screen)

            pygame.display.update()
            pygame.time.Clock().tick(fps)

        pygame.quit()
