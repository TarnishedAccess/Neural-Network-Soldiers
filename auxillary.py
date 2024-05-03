import pygame

class Button():
    def __init__(self, width, height, x, y, sprite, sprite_pressed, text_surface, function, hovered, click_sound):
       
        self.button_sprite_notPressed = pygame.transform.scale(sprite, (width, height))
        self.button_sprite_pressed = pygame.transform.scale(sprite_pressed, (width, height))
        self.hovered = hovered
        self.button_sprite = sprite
        self.button_rect = self.button_sprite_notPressed.get_rect()
        self.button_rect.centerx = x
        self.button_rect.centery = y
        self.function = function
        self.text_surface = text_surface
        self.click_sound = click_sound

    def draw(self, screen):
        if not self.hovered:
            self.button_sprite = self.button_sprite_notPressed
        else:
            self.button_sprite = self.button_sprite_pressed
        screen.blit(self.button_sprite, self.button_rect)
        text_rect = self.text_surface.get_rect(center=self.button_rect.center)
        screen.blit(self.text_surface, text_rect)

    def play_sound(self):
        if self.click_sound:
            button_click_sound = pygame.mixer.Sound(self.click_sound)
            button_click_sound.play()
            
class TextPlate():
    def __init__(self, width, height, x, y, sprite, text_surface):
       
        self.button_sprite = pygame.transform.scale(sprite, (width, height))
        self.button_rect = self.button_sprite.get_rect()
        self.button_rect.centerx = x
        self.button_rect.centery = y
        self.text_surface = text_surface

    def draw(self, screen):
        screen.blit(self.button_sprite, self.button_rect)
        text_rect = self.text_surface.get_rect(center=self.button_rect.center)
        screen.blit(self.text_surface, text_rect)
