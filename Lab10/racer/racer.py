import pygame
import sys
import random

pygame.init()
# настройки экрана и игры
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
FPS = 60

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255) # Цвет для встречной машины, если нет картинки

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maserati Racer")
FramePerSec = pygame.time.Clock()

# Попытка загрузить шрифт Verdana, если он недоступен, используем шрифт по умолчанию
try:
    font = pygame.font.SysFont("Verdana", 30)
    game_over_font = pygame.font.SysFont("Verdana", 60) # Шрифт для Game Over
except:
    font = pygame.font.SysFont(None, 30)
    game_over_font = pygame.font.SysFont(None, 60)

SCORE = 0

# переменная для анимации фона
bg_y = 0 

# загрузка заднего фона
try:
    background = pygame.image.load("Lab10/racer/background.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except FileNotFoundError:
    background = None

# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        
        try:
            self.image = pygame.image.load("Lab10/racer/player_car.png")
            self.image = pygame.transform.scale(self.image, (80, 100)) 
        except FileNotFoundError:
            self.image = pygame.Surface((80, 100))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520) 

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 45: 
              if pressed_keys[pygame.K_LEFT]:
                  self.rect.move_ip(-SPEED, 0)
        if self.rect.right < 355:        
              if pressed_keys[pygame.K_RIGHT]:
                  self.rect.move_ip(SPEED, 0)
                  
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# класс врага (встречка)
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        try:
            # 1. Загружаем картинку
            self.image = pygame.image.load("Lab10/racer/enemy_car.png")
            
            # 2. Подгоняем размер (как у игрока)
            self.image = pygame.transform.scale(self.image, (70, 80)) 
            
            # 3. ПЕРЕВОРАЧИВАЕМ КАРТИНКУ НА 180 ГРАДУСОВ
            
        except FileNotFoundError:
            self.image = pygame.Surface((70, 80))
            self.image.fill(BLUE)
            
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(50, 350), -100) 
        self.speed = 7# Встречка едет чуть быстрее

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.center = (random.randint(50, 350), -100)
                  
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# класс монетки
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GOLD, (15, 15), 15)
        
        self.rect = self.image.get_rect()
        # 2. ГРАНИЦЫ: Монеты появляются только на проезжей части (от x=50 до x=350)
        self.rect.center = (random.randint(50, 350), -20)
        self.speed = 6# Чуть ускорили падение монет

    def move(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.center = (random.randint(50, 350), -20)
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)

# создание игровых объектов
P1 = Player()
C1 = Coin()
E1 = Enemy() # Создаем врага

coins_group = pygame.sprite.Group()
coins_group.add(C1)

enemies_group = pygame.sprite.Group() # Группа для врагов
enemies_group.add(E1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(C1)
all_sprites.add(E1) # Добавляем врага ко всем спрайтам

# главный игровой цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Движение
    P1.move()
    C1.move()
    E1.move() # Двигаем врага

    # Логика столкновений с монетой
    if pygame.sprite.spritecollide(P1, coins_group, True):
        SCORE += 1
        new_coin = Coin()
        C1 = new_coin
        coins_group.add(C1)
        all_sprites.add(C1)

    # Логика столкновений с врагом (Авария)
    if pygame.sprite.spritecollideany(P1, enemies_group):
        # Экран Game Over
        DISPLAYSURF.fill(RED)
        game_over_text = game_over_font.render("CRASHED!", True, BLACK)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        DISPLAYSURF.blit(game_over_text, text_rect)
        pygame.display.update()
        
        # Ждем 2 секунды и закрываем
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    # добавлнение фона и отрисовка всех объектов
    if background:
        # Рисуем фон дважды, чтобы создать бесконечный цикл дороги
        DISPLAYSURF.blit(background, (0, bg_y))
        DISPLAYSURF.blit(background, (0, bg_y - SCREEN_HEIGHT))
        
        # Смещаем фон вниз
        bg_y += SPEED 
        
        # Если фон уехал слишком далеко, возвращаем его назад
        if bg_y >= SCREEN_HEIGHT:
            bg_y = 0
    else:
        DISPLAYSURF.fill(WHITE)
    
    # Отрисовка машины и монет
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
    
    # Отрисовка текста (Счетчика)
    score_text = font.render(f"Coins: {SCORE}", True, BLACK)
    text_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(score_text, text_rect)
    
    # Обновление экрана
    pygame.display.update()
    FramePerSec.tick(FPS)