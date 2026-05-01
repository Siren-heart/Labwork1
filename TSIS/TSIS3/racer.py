import pygame
import random
import os

# Автоматически определяем папку, где лежит этот файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Цвета
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 215, 0)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        try:
            # Ищем картинку строго в текущей папке
            img_path = os.path.join(CURRENT_DIR, "player_car.png")
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, (80, 100))
        except FileNotFoundError:
            self.image = pygame.Surface((50, 80), pygame.SRCALPHA)
            color = RED if color_name == "RED" else (GREEN if color_name == "GREEN" else BLUE)
            pygame.draw.rect(self.image, color, [0, 0, 50, 80], border_radius=5)
            
        self.rect = self.image.get_rect(center=(200, 500))
        self.shield_active = False

    def update(self, speed):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 20:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and self.rect.right < 380:
            self.rect.x += 5

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.shield_active:
            pygame.draw.rect(surface, CYAN, self.rect.inflate(10, 10), 3, border_radius=8)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, base_speed):
        super().__init__()
        try:
            # Ищем картинку врага строго в текущей папке
            img_path = os.path.join(CURRENT_DIR, "enemy_car.png")
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, (70, 80))
        except FileNotFoundError:
            self.image = pygame.Surface((50, 80))
            self.image.fill(BLUE)
            
        self.rect = self.image.get_rect(center=(random.randint(50, 350), -100))
        self.speed = base_speed + random.randint(0, 2)

    def update(self, speed_multiplier):
        self.rect.y += self.speed * speed_multiplier
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 20))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(random.randint(50, 350), -50))

    def update(self, speed_multiplier):
        self.rect.y += 5 * speed_multiplier 
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["NITRO", "SHIELD", "REPAIR"])
        self.image = pygame.Surface((30, 30))
        
        if self.type == "NITRO": 
            self.image.fill(MAGENTA)
        elif self.type == "SHIELD": 
            self.image.fill(CYAN)
        elif self.type == "REPAIR": 
            self.image.fill(GREEN)
            
        self.rect = self.image.get_rect(center=(random.randint(50, 350), -50))

    def update(self, speed_multiplier):
        self.rect.y += 5 * speed_multiplier
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.weight = random.choices([1, 2, 5], weights=[70, 20, 10])[0]
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        
        color = YELLOW if self.weight == 1 else (GREEN if self.weight == 2 else MAGENTA)
        pygame.draw.circle(self.image, color, (10, 10), 10)
        
        self.rect = self.image.get_rect(center=(random.randint(50, 350), -30))

    def update(self, speed_multiplier):
        self.rect.y += 5 * speed_multiplier
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()