import pygame
import random
import os

WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
DARK_RED = (139, 0, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (100, 100, 100)
LIGHT_GREEN = (170, 215, 81)
DARK_GREEN = (162, 209, 73)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_img(name, is_apple=False, color=RED):
    try:
        full_path = os.path.join(CURRENT_DIR, name)
        img = pygame.image.load(full_path)
        return pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))
    except FileNotFoundError:
        surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        if is_apple:
            pygame.draw.circle(surface, color, (BLOCK_SIZE//2, BLOCK_SIZE//2), BLOCK_SIZE//2)
        else:
            pygame.draw.rect(surface, color, [0, 0, BLOCK_SIZE, BLOCK_SIZE], border_radius=4)
        return surface

# Картинки еды
food_img_1 = load_img('apple.png', is_apple=True, color=RED)
food_img_2 = load_img('berry.png', is_apple=True, color=BLUE)
food_img_3 = load_img('gold_apple.png', is_apple=True, color=GOLD)
poison_img = load_img('poison.png', is_apple=True, color=DARK_RED) # Яд

# Картинки змеи
head_up = load_img('head_up.png', color=(70, 116, 233))
head_down = load_img('head_down.png', color=(70, 116, 233))
head_left = load_img('head_left.png', color=(70, 116, 233))
head_right = load_img('head_right.png', color=(70, 116, 233))
tail_up = load_img('tail_up.png', color=(70, 116, 233))
tail_down = load_img('tail_down.png', color=(70, 116, 233))
tail_left = load_img('tail_left.png', color=(70, 116, 233))
tail_right = load_img('tail_right.png', color=(70, 116, 233))
body_vertical = load_img('body_vertical.png', color=(70, 116, 233))
body_horizontal = load_img('body_horizontal.png', color=(70, 116, 233))
corner_tl = load_img('body_topleft.png', color=(70, 116, 233))
corner_tr = load_img('body_topright.png', color=(70, 116, 233))
corner_bl = load_img('body_bottomleft.png', color=(70, 116, 233))
corner_br = load_img('body_bottomright.png', color=(70, 116, 233))

class SmartEntity:
    def __init__(self, is_poison=False):
        self.is_poison = is_poison
        self.x, self.y = 0, 0
        self.timer = 0
        self.max_time = 100
        self.weight = -2 if is_poison else 1
        self.img = poison_img

    def respawn(self, snake_body, obstacles):
        if not self.is_poison:
            choices = [(1, food_img_1), (2, food_img_2), (3, food_img_3)]
            self.weight, self.img = random.choices(choices, weights=[70, 20, 10])[0]
        self.timer = self.max_time
        while True:
            self.x = random.randrange(0, WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            self.y = random.randrange(0, HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            if [self.x, self.y] not in snake_body and [self.x, self.y] not in obstacles:
                break

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))
        if not self.is_poison:
            timer_width = (self.timer / self.max_time) * BLOCK_SIZE
            pygame.draw.rect(surface, WHITE, [self.x, self.y - 5, timer_width, 3])

class PowerUp:
    def __init__(self):
        self.active = False
        self.x, self.y = 0, 0
        self.type = None
        self.spawn_time = 0

    def spawn(self, snake_body, obstacles):
        self.active = True
        self.type = random.choice(["SPEED", "SLOW", "SHIELD"])
        self.spawn_time = pygame.time.get_ticks()
        while True:
            self.x = random.randrange(0, WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            self.y = random.randrange(0, HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            if [self.x, self.y] not in snake_body and [self.x, self.y] not in obstacles:
                break

    def draw(self, surface):
        if not self.active: return
        color = MAGENTA if self.type == "SPEED" else (BLUE if self.type == "SLOW" else CYAN)
        pygame.draw.circle(surface, color, (self.x + BLOCK_SIZE//2, self.y + BLOCK_SIZE//2), BLOCK_SIZE//2)

def draw_checkerboard(surface, show_grid):
    for row in range(HEIGHT // BLOCK_SIZE):
        for col in range(WIDTH // BLOCK_SIZE):
            color = LIGHT_GREEN if (row + col) % 2 == 0 else DARK_GREEN
            rect = [col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE]
            pygame.draw.rect(surface, color, rect)
            if show_grid:
                pygame.draw.rect(surface, (140, 180, 60), rect, 1)

def draw_smart_snake(surface, snake_body, snake_color_rgb, shield_active):
    for index, segment in enumerate(snake_body):
        x, y = segment[0], segment[1]
        if index == len(snake_body) - 1:
            if len(snake_body) > 1:
                prev_seg = snake_body[index - 1]
                if prev_seg[0] < x: img = head_right
                elif prev_seg[0] > x: img = head_left
                elif prev_seg[1] < y: img = head_down
                else: img = head_up
            else: img = head_right 
            surface.blit(img, (x, y))
            if shield_active: # Неоновая обводка головы при щите
                pygame.draw.rect(surface, CYAN, [x-2, y-2, BLOCK_SIZE+4, BLOCK_SIZE+4], 2, border_radius=4)
        elif index == 0:
            next_seg = snake_body[1]
            if next_seg[0] < x: img = tail_right
            elif next_seg[0] > x: img = tail_left
            elif next_seg[1] < y: img = tail_down
            else: img = tail_up
            surface.blit(img, (x, y))
        else:
            prev_seg = snake_body[index - 1]
            next_seg = snake_body[index + 1]
            if prev_seg[0] == next_seg[0]: img = body_vertical
            elif prev_seg[1] == next_seg[1]: img = body_horizontal
            else:
                if (prev_seg[0] < x and next_seg[1] < y) or (next_seg[0] < x and prev_seg[1] < y): img = corner_tl
                elif (prev_seg[0] > x and next_seg[1] < y) or (next_seg[0] > x and prev_seg[1] < y): img = corner_tr
                elif (prev_seg[0] < x and next_seg[1] > y) or (next_seg[0] < x and prev_seg[1] > y): img = corner_bl
                else: img = corner_br
            surface.blit(img, (x, y))

def generate_obstacles(level, snake_body):
    obstacles = []
    if level < 3: return obstacles # Препятствия с 3 уровня
    num_blocks = min(15, level * 2)
    for _ in range(num_blocks):
        while True:
            ox = random.randrange(0, WIDTH // BLOCK_SIZE) * BLOCK_SIZE
            oy = random.randrange(0, HEIGHT // BLOCK_SIZE) * BLOCK_SIZE
            # Не ставим блоки близко к голове змеи при старте
            head_x, head_y = snake_body[-1]
            if [ox, oy] not in snake_body and abs(ox - head_x) > BLOCK_SIZE * 3 and abs(oy - head_y) > BLOCK_SIZE * 3:
                obstacles.append([ox, oy])
                break
    return obstacles