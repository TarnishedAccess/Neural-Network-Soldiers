import pygame

class Button():
    def __init__(self, width, height, x, y, sprite, sprite_pressed, text_surface, function):
       
        self.button_sprite = pygame.transform.scale(sprite, (width, height))
        self.button_sprite_pressed = pygame.transform.scale(sprite_pressed, (width, height))
        self.button_rect = self.button_sprite.get_rect()
        self.button_rect.centerx = x
        self.button_rect.centery = y
        self.function = function
        self.text_surface = text_surface

    def draw(self, screen):
        screen.blit(self.button_sprite, self.button_rect)
        text_rect = self.text_surface.get_rect(center=self.button_rect.center)
        screen.blit(self.text_surface, text_rect)
                
        
