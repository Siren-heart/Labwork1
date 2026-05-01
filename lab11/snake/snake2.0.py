import pygame
import sys
import random
import os

# --- ИНИЦИАЛИЗАЦИЯ И НАСТРОЙКИ ---
pygame.init()

WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20 # Размер одной клетки

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
SNAKE_FALLBACK = (70, 116, 233) # Запасной цвет змейки (если нет картинок)

# Цвета для шахматной доски Google Snake
LIGHT_GREEN = (170, 215, 81)
DARK_GREEN = (162, 209, 73)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Google Snake (Lab version) - Week 11")
clock = pygame.time.Clock()

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 20)

# загрузка изображений
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- ИЗМЕНЕНО ДЛЯ 11 НЕДЕЛИ: Добавлен аргумент color, чтобы рисовать яблоки разного цвета ---
def load_img(name, is_apple=False, color=RED):
    """Функция загрузки с железобетонными абсолютными путями"""
    try:
        full_path = os.path.join(CURRENT_DIR, name)
        img = pygame.image.load(full_path)
        return pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))
    except FileNotFoundError:
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        if is_apple:
            # Рисуем яблоко переданным цветом (для разных весов)
            pygame.draw.circle(surface, color, (BLOCK_SIZE//2, BLOCK_SIZE//2), BLOCK_SIZE//2)
        else:
            pygame.draw.rect(surface, SNAKE_FALLBACK, [0, 0, BLOCK_SIZE, BLOCK_SIZE], border_radius=4)
        return surface

# --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Картинки для еды разного веса ---
food_img_1 = load_img('apple.png', is_apple=True, color=RED)            # Обычное яблоко (вес 1)
food_img_2 = load_img('berry.png', is_apple=True, color=(0, 0, 255))    # Синяя ягода (вес 2)
food_img_3 = load_img('gold_apple.png', is_apple=True, color=(255, 215, 0)) # Золотое яблоко (вес 3)
# -----------------------------------------------------------------

# Загружаем части змеи
head_up = load_img('head_up.png')
head_down = load_img('head_down.png')
head_left = load_img('head_left.png')
head_right = load_img('head_right.png')

tail_up = load_img('tail_up.png')
tail_down = load_img('tail_down.png')
tail_left = load_img('tail_left.png')
tail_right = load_img('tail_right.png')

body_vertical = load_img('body_vertical.png')
body_horizontal = load_img('body_horizontal.png')

corner_tl = load_img('body_topleft.png')
corner_tr = load_img('body_topright.png')
corner_bl = load_img('body_bottomleft.png')
corner_br = load_img('body_bottomright.png')


# --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Класс для умной еды (Вес + Таймер) ---
class Food:
    def __init__(self, snake_body):
        self.max_time = 80 # Сколько "кадров" живет еда до исчезновения
        self.respawn(snake_body)

    def respawn(self, snake_body):
        # ЗАДАНИЕ 1: Случайная генерация еды с разным весом
        # Шансы: Вес 1 (70%), Вес 2 (20%), Вес 3 (10%)
        choices = [(1, food_img_1), (2, food_img_2), (3, food_img_3)]
        self.weight, self.img = random.choices(choices, weights=[70, 20, 10])[0]
        
        # ЗАДАНИЕ 2: Сброс таймера при спавне новой еды
        self.timer = self.max_time

        # Ищем свободные координаты
        while True:
            self.x = random.randrange(0, WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            self.y = random.randrange(0, HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            if [self.x, self.y] not in snake_body:
                break

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))
        
        # Отрисовка полоски таймера над яблоком
        timer_width = (self.timer / self.max_time) * BLOCK_SIZE
        pygame.draw.rect(surface, WHITE, [self.x, self.y - 5, timer_width, 3])
# -------------------------------------------------------------------


# функции игры
def draw_checkerboard(surface):
    """Рисует двухцветный зеленый фон"""
    for row in range(HEIGHT // BLOCK_SIZE):
        for col in range(WIDTH // BLOCK_SIZE):
            if (row + col) % 2 == 0:
                color = LIGHT_GREEN
            else:
                color = DARK_GREEN
            pygame.draw.rect(surface, color, [col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])

def draw_score_and_level(score, level):
    """Отрисовка текста (Задание 5)"""
    score_text = score_font.render(f"Score: {score}  |  Level: {level}", True, WHITE)
    shadow = score_font.render(f"Score: {score}  |  Level: {level}", True, BLACK)
    screen.blit(shadow, [12, 2])
    screen.blit(score_text, [10, 0])

def draw_smart_snake(surface, snake_body):
    """Сложная логика отрисовки правильных картинок тела змеи"""
    for index, segment in enumerate(snake_body):
        x, y = segment[0], segment[1]

        # 1. ГОЛОВА
        if index == len(snake_body) - 1:
            if len(snake_body) > 1:
                prev_seg = snake_body[index - 1]
                if prev_seg[0] < x: img = head_right
                elif prev_seg[0] > x: img = head_left
                elif prev_seg[1] < y: img = head_down
                else: img = head_up
            else:
                img = head_right 
            surface.blit(img, (x, y))

        # 2. ХВОСТ
        elif index == 0:
            next_seg = snake_body[1]
            if next_seg[0] < x: img = tail_right
            elif next_seg[0] > x: img = tail_left
            elif next_seg[1] < y: img = tail_down
            else: img = tail_up
            surface.blit(img, (x, y))

        # 3. ТЕЛО И УГЛЫ
        else:
            prev_seg = snake_body[index - 1]
            next_seg = snake_body[index + 1]

            if prev_seg[0] == next_seg[0]:
                img = body_vertical
            elif prev_seg[1] == next_seg[1]:
                img = body_horizontal
            else:
                if (prev_seg[0] < x and next_seg[1] < y) or (next_seg[0] < x and prev_seg[1] < y):
                    img = corner_tl
                elif (prev_seg[0] > x and next_seg[1] < y) or (next_seg[0] > x and prev_seg[1] < y):
                    img = corner_tr
                elif (prev_seg[0] < x and next_seg[1] > y) or (next_seg[0] < x and prev_seg[1] > y):
                    img = corner_bl
                else:
                    img = corner_br
                    
            surface.blit(img, (x, y))

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(WIDTH/2, HEIGHT/2))
    pygame.draw.rect(screen, BLACK, mesg_rect.inflate(20, 20))
    screen.blit(mesg, mesg_rect)


# главный игровой цикл
def gameLoop():
    game_over = False
    
    x1 = (WIDTH // 2 // BLOCK_SIZE) * BLOCK_SIZE
    y1 = (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE

    x1_change = BLOCK_SIZE 
    y1_change = 0

    snake_body = []
    length_of_snake = 3 
    
    snake_body.append([x1 - 2*BLOCK_SIZE, y1])
    snake_body.append([x1 - BLOCK_SIZE, y1])

    score = 0
    level = 1
    base_speed = 8 

    # --- ИЗМЕНЕНО ДЛЯ 11 НЕДЕЛИ: Создаем объект еды вместо просто координат ---
    food = Food(snake_body)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_over = True

        x1 += x1_change
        y1 += y1_change

        # --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Логика таймера исчезновения ---
        # Если таймер истек, еда меняет положение
        food.timer -= 1
        if food.timer <= 0:
            food.respawn(snake_body)
        # -------------------------------------------------------------

        # ОТРИСОВКА
        draw_checkerboard(screen)
        
        # --- ИЗМЕНЕНО ДЛЯ 11 НЕДЕЛИ: Отрисовка умной еды с таймером ---
        food.draw(screen)

        snake_head = [x1, y1]
        snake_body.append(snake_head)

        if len(snake_body) > length_of_snake:
            del snake_body[0]

        for segment in snake_body[:-1]:
            if segment == snake_head:
                game_over = True

        draw_smart_snake(screen, snake_body)
        draw_score_and_level(score, level)
        pygame.display.update()

        # ПОЕДАНИЕ ЕДЫ
        # --- ИЗМЕНЕНО ДЛЯ 11 НЕДЕЛИ: Учет веса монеты при поедании ---
        if x1 == food.x and y1 == food.y:
            length_of_snake += food.weight  # Змея растет сильнее от тяжелой еды
            score += food.weight            # Очков дается больше
            level = (score // 3) + 1
            food.respawn(snake_body)        # Спавним новую еду
        # -------------------------------------------------------------

        current_speed = base_speed + (level - 1) * 2
        clock.tick(current_speed)

    message(f"Game Over! Final Score: {score}", RED)
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

gameLoop()