import pygame
import sys
import json
import os
import random
from db import init_db, save_score, get_top_10, get_personal_best
from game import WIDTH, HEIGHT, BLOCK_SIZE, BLACK, WHITE, RED, GRAY, MAGENTA, CYAN, SmartEntity, PowerUp, draw_checkerboard, draw_smart_snake, generate_obstacles

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake TSIS 4")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Verdana", 24)
title_font = pygame.font.SysFont("Verdana", 40, bold=True)

# --- УПРАВЛЕНИЕ НАСТРОЙКАМИ (TSIS 4) ---
SETTINGS_FILE = 'settings.json'
default_settings = {"color": [70, 116, 233], "grid": False, "sound": True}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f: return json.load(f)
    return default_settings.copy()

def save_settings(s):
    with open(SETTINGS_FILE, 'w') as f: json.dump(s, f)

settings = load_settings()

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = (200, 200, 200) if self.rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        text_surf = font.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

class InputBox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN: return self.text
            elif event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            else:
                if len(self.text) < 15: self.text += event.unicode
        return None

    def draw(self, surface):
        color = WHITE if self.active else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        surface.blit(font.render(self.text, True, BLACK), (self.rect.x + 5, self.rect.y + 5))

def draw_text(text, font_obj, color, x, y, center=False):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)

# --- ИГРОВОЙ ЦИКЛ ---
def game_loop(username):
    pb = get_personal_best(username)
    score, level = 0, 1
    base_speed = 8
    
    x1, y1 = (WIDTH // 2 // BLOCK_SIZE) * BLOCK_SIZE, (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
    dx, dy = BLOCK_SIZE, 0
    snake_body = [[x1 - 2*BLOCK_SIZE, y1], [x1 - BLOCK_SIZE, y1], [x1, y1]]
    length_of_snake = 3

    obstacles = generate_obstacles(level, snake_body)
    
    food = SmartEntity()
    food.respawn(snake_body, obstacles)
    
    poison = SmartEntity(is_poison=True)
    poison.respawn(snake_body, obstacles)
    
    powerup = PowerUp()
    active_effect = None
    effect_end_time = 0
    shield_active = False

    while True:
        current_time = pygame.time.get_ticks()
        
        # Завершение эффектов
        if active_effect and current_time > effect_end_time:
            active_effect = None
        
        # Пропажа поверапа с поля (8 секунд)
        if powerup.active and current_time - powerup.spawn_time > 8000:
            powerup.active = False
            
        # Спавн поверапа (рандомно)
        if not powerup.active and active_effect is None and random.randint(1, 200) == 1:
            powerup.spawn(snake_body, obstacles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0: dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0: dx, dy = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and dy == 0: dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0: dx, dy = 0, BLOCK_SIZE

        x1 += dx
        y1 += dy

        # СТОЛКНОВЕНИЕ СО СТЕНОЙ
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            if shield_active:
                x1 = x1 % WIDTH
                y1 = y1 % HEIGHT
                shield_active = False
            else:
                save_score(username, score, level)
                return {"score": score, "level": level, "pb": pb}

        # СТОЛКНОВЕНИЕ С ПРЕПЯТСТВИЕМ
        if [x1, y1] in obstacles:
            if shield_active: shield_active = False
            else:
                save_score(username, score, level)
                return {"score": score, "level": level, "pb": pb}

        snake_head = [x1, y1]
        snake_body.append(snake_head)

        # СТОЛКНОВЕНИЕ С СОБОЙ
        for segment in snake_body[:-1]:
            if segment == snake_head:
                if shield_active: shield_active = False
                else:
                    save_score(username, score, level)
                    return {"score": score, "level": level, "pb": pb}

        # ПОЕДАНИЕ ЕДЫ
        if x1 == food.x and y1 == food.y:
            length_of_snake += 1
            score += food.weight
            if score // 5 + 1 > level:
                level += 1
                obstacles = generate_obstacles(level, snake_body) # Новые стены на новом уровне
            food.respawn(snake_body, obstacles)
        else:
            if len(snake_body) > length_of_snake:
                del snake_body[0]

        # ПОЕДАНИЕ ЯДА
        if x1 == poison.x and y1 == poison.y:
            length_of_snake -= 2
            if length_of_snake <= 1: # Смерть от яда
                save_score(username, score, level)
                return {"score": score, "level": level, "pb": pb}
            snake_body = snake_body[-length_of_snake:]
            poison.respawn(snake_body, obstacles)

        # СБОР ПОВЕРАПА
        if powerup.active and x1 == powerup.x and y1 == powerup.y:
            powerup.active = False
            if powerup.type == "SHIELD":
                shield_active = True
            else:
                active_effect = powerup.type
                effect_end_time = current_time + 5000

        # Таймер еды
        food.timer -= 1
        if food.timer <= 0: food.respawn(snake_body, obstacles)

        # ОТРИСОВКА
        draw_checkerboard(screen, settings["grid"])
        for obs in obstacles:
            pygame.draw.rect(screen, GRAY, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])
            pygame.draw.rect(screen, BLACK, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE], 2)

        food.draw(screen)
        poison.draw(screen)
        powerup.draw(screen)
        draw_smart_snake(screen, snake_body, settings["color"], shield_active)

        # UI
        pygame.draw.rect(screen, BLACK, [0, 0, WIDTH, 30])
        draw_text(f"Score: {score} | Lvl: {level} | PB: {pb}", font, WHITE, 10, 0)
        if active_effect: draw_text(f"EFFECT: {active_effect}", font, MAGENTA, WIDTH - 180, 0)
        if shield_active: draw_text("SHIELD ON", font, CYAN, WIDTH - 180, 0)

        pygame.display.flip()

        # Регулировка скорости
        current_speed = base_speed + (level - 1)
        if active_effect == "SPEED": current_speed += 5
        elif active_effect == "SLOW": current_speed = max(4, current_speed - 5)
        clock.tick(current_speed)


# --- СЦЕНЫ ---
def main_menu():
    init_db() # Инициализация БД при запуске
    input_box = InputBox(WIDTH//2 - 100, 150, 200, 40)
    btn_play = Button(WIDTH//2 - 100, 200, 200, 40, "Play")
    btn_leader = Button(WIDTH//2 - 100, 250, 200, 40, "Leaderboard")
    btn_settings = Button(WIDTH//2 - 100, 300, 200, 40, "Settings")
    btn_quit = Button(WIDTH//2 - 100, 350, 200, 40, "Quit")

    while True:
        screen.fill(WHITE)
        draw_text("SNAKE DB EDITION", title_font, BLACK, WIDTH//2, 80, center=True)
        draw_text("Username:", font, BLACK, WIDTH//2 - 100, 120)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            name = input_box.handle_event(event)
            if name: return "PLAYING", name
            
            if btn_play.is_clicked(event): return "PLAYING", input_box.text if input_box.text else "Guest"
            if btn_leader.is_clicked(event): return "LEADERBOARD", ""
            if btn_settings.is_clicked(event): return "SETTINGS", ""
            if btn_quit.is_clicked(event): pygame.quit(); sys.exit()

        input_box.draw(screen)
        for b in [btn_play, btn_leader, btn_settings, btn_quit]: b.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def leaderboard_screen():
    btn_back = Button(20, 350, 100, 40, "Back")
    top_10 = get_top_10()

    while True:
        screen.fill(WHITE)
        draw_text("TOP 10 PLAYERS", title_font, BLACK, WIDTH//2, 40, center=True)
        
        y = 100
        for i, row in enumerate(top_10):
            # row: username, score, level, date
            txt = f"{i+1}. {row[0][:10]} | Score: {row[1]} | Lvl: {row[2]} | {row[3]}"
            draw_text(txt, font, BLACK, 50, y)
            y += 25
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_back.is_clicked(event): return "MENU"

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def settings_screen():
    btn_grid = Button(WIDTH//2 - 100, 150, 200, 40, f"Grid: {'ON' if settings['grid'] else 'OFF'}")
    btn_sound = Button(WIDTH//2 - 100, 200, 200, 40, f"Sound: {'ON' if settings['sound'] else 'OFF'}")
    btn_back = Button(WIDTH//2 - 100, 300, 200, 40, "Save & Back")

    while True:
        screen.fill(WHITE)
        draw_text("SETTINGS", title_font, BLACK, WIDTH//2, 80, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_grid.is_clicked(event):
                settings['grid'] = not settings['grid']
                btn_grid.text = f"Grid: {'ON' if settings['grid'] else 'OFF'}"
            if btn_sound.is_clicked(event):
                settings['sound'] = not settings['sound']
                btn_sound.text = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
            if btn_back.is_clicked(event):
                save_settings(settings)
                return "MENU"

        for b in [btn_grid, btn_sound, btn_back]: b.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(stats):
    btn_retry = Button(WIDTH//2 - 100, 250, 200, 40, "Retry")
    btn_menu = Button(WIDTH//2 - 100, 300, 200, 40, "Main Menu")

    while True:
        screen.fill(WHITE)
        draw_text("GAME OVER", title_font, RED, WIDTH//2, 100, center=True)
        draw_text(f"Final Score: {stats['score']}", font, BLACK, WIDTH//2, 150, center=True)
        draw_text(f"Level Reached: {stats['level']}", font, BLACK, WIDTH//2, 180, center=True)
        draw_text(f"Personal Best: {max(stats['score'], stats['pb'])}", font, BLACK, WIDTH//2, 210, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event): return "RETRY"
            if btn_menu.is_clicked(event): return "MENU"

        btn_retry.draw(screen)
        btn_menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# --- ГЛАВНАЯ ЛОГИКА ---
current_state = "MENU"
username = ""
stats = None

while True:
    if current_state == "MENU":
        current_state, username = main_menu()
    elif current_state == "LEADERBOARD":
        current_state = leaderboard_screen()
    elif current_state == "SETTINGS":
        current_state = settings_screen()
    elif current_state == "PLAYING":
        stats = game_loop(username)
        current_state = "GAME_OVER"
    elif current_state == "GAME_OVER":
        res = game_over_screen(stats)
        current_state = "PLAYING" if res == "RETRY" else "MENU"