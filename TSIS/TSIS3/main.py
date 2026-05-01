import pygame
import sys
import os
from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import Button, InputBox, FONT, TITLE_FONT, WHITE, BLACK, GRAY
from racer import Player, Enemy, Obstacle, PowerUp, Coin, SCREEN_WIDTH, SCREEN_HEIGHT, YELLOW, RED, MAGENTA

# Автоматически определяем папку, где лежит этот файл
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer TSIS 3")
clock = pygame.time.Clock()

settings = load_settings()

try:
    # Ищем фон строго в текущей папке
    bg_path = os.path.join(CURRENT_DIR, "background.png")
    background = pygame.image.load(bg_path)
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except FileNotFoundError:
    background = None

def draw_text(surface, text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)

# --- ЭКРАНЫ (СЦЕНЫ) ---

def main_menu():
    btn_play = Button(100, 200, 200, 50, "Play")
    btn_leader = Button(100, 270, 200, 50, "Leaderboard")
    btn_settings = Button(100, 340, 200, 50, "Settings")
    btn_quit = Button(100, 410, 200, 50, "Quit")

    while True:
        screen.fill(WHITE)
        draw_text(screen, "RACER 3000", TITLE_FONT, BLACK, SCREEN_WIDTH//2, 100, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_play.handle_event(event): return "NAME_INPUT"
            if btn_leader.handle_event(event): return "LEADERBOARD"
            if btn_settings.handle_event(event): return "SETTINGS"
            if btn_quit.handle_event(event): pygame.quit(); sys.exit()

        for btn in [btn_play, btn_leader, btn_settings, btn_quit]:
            btn.draw(screen)
            
        pygame.display.flip()
        clock.tick(60)

def settings_screen():
    btn_diff = Button(100, 200, 200, 50, f"Diff: {settings['difficulty']}")
    btn_color = Button(100, 270, 200, 50, f"Color: {settings['color']}")
    btn_back = Button(100, 400, 200, 50, "Back")

    difficulties = ["EASY", "NORMAL", "HARD"]
    colors = ["RED", "GREEN", "BLUE"]

    while True:
        screen.fill(WHITE)
        draw_text(screen, "SETTINGS", TITLE_FONT, BLACK, SCREEN_WIDTH//2, 100, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_diff.handle_event(event):
                idx = (difficulties.index(settings['difficulty']) + 1) % 3
                settings['difficulty'] = difficulties[idx]
                btn_diff.text = f"Diff: {settings['difficulty']}"
            if btn_color.handle_event(event):
                idx = (colors.index(settings['color']) + 1) % 3
                settings['color'] = colors[idx]
                btn_color.text = f"Color: {settings['color']}"
            if btn_back.handle_event(event):
                save_settings(settings)
                return "MENU"

        for btn in [btn_diff, btn_color, btn_back]:
            btn.draw(screen)
            
        pygame.display.flip()
        clock.tick(60)

def leaderboard_screen():
    btn_back = Button(100, 500, 200, 50, "Back")
    board = load_leaderboard()

    while True:
        screen.fill(WHITE)
        draw_text(screen, "TOP 10", TITLE_FONT, BLACK, SCREEN_WIDTH//2, 50, center=True)
        
        y = 120
        for i, entry in enumerate(board):
            text = f"{i+1}. {entry['name']} - {entry['score']} pts"
            draw_text(screen, text, FONT, BLACK, 50, y)
            y += 35
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_back.handle_event(event):
                return "MENU"

        btn_back.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def name_input_screen():
    input_box = InputBox(100, 250, 200, 40)
    btn_start = Button(100, 320, 200, 50, "Start Engine")
    
    while True:
        screen.fill(WHITE)
        draw_text(screen, "ENTER NAME:", TITLE_FONT, BLACK, SCREEN_WIDTH//2, 150, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            name = input_box.handle_event(event)
            if name: return name 
            if btn_start.handle_event(event):
                return input_box.text if input_box.text else "Player"

        input_box.draw(screen)
        btn_start.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(stats):
    btn_retry = Button(100, 300, 200, 50, "Retry")
    btn_menu = Button(100, 370, 200, 50, "Main Menu")

    while True:
        screen.fill(WHITE)
        draw_text(screen, "GAME OVER", TITLE_FONT, RED, SCREEN_WIDTH//2, 100, center=True)
        draw_text(screen, f"Score: {stats['score']}", FONT, BLACK, SCREEN_WIDTH//2, 180, center=True)
        draw_text(screen, f"Distance: {int(stats['dist'])}m", FONT, BLACK, SCREEN_WIDTH//2, 220, center=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.handle_event(event): return "RETRY"
            if btn_menu.handle_event(event): return "MENU"

        btn_retry.draw(screen)
        btn_menu.draw(screen)
        pygame.display.flip()
        clock.tick(60)

# --- ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ ---

def game_loop(player_name):
    diff = settings['difficulty']
    base_enemy_speed = 4 if diff == "EASY" else (6 if diff == "NORMAL" else 9)
    spawn_rate = 60 if diff == "EASY" else (40 if diff == "NORMAL" else 25)

    player = Player(settings['color'])
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    score = 0
    distance = 0.0
    lives = 3
    
    nitro_time = 0
    
    frame_count = 0
    bg_y = 0

    while True:
        speed_mult = 1.5 if nitro_time > 0 else 1.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        frame_count += 1
        
        # Спавн
        if frame_count % spawn_rate == 0:
            e = Enemy(base_enemy_speed)
            enemies.add(e); all_sprites.add(e)
        if frame_count % (spawn_rate * 3) == 0:
            obs = Obstacle()
            obstacles.add(obs); all_sprites.add(obs)
        if frame_count % 300 == 0: 
            pw = PowerUp()
            powerups.add(pw); all_sprites.add(pw)
        if frame_count % 50 == 0:
            c = Coin()
            coins.add(c); all_sprites.add(c)

        # Обновление
        player.update(speed_mult)
        enemies.update(speed_mult)
        obstacles.update(speed_mult)
        powerups.update(speed_mult)
        coins.update(speed_mult)

        # Столкновения с бонусами и монетами
        hits = pygame.sprite.spritecollide(player, coins, True)
        for hit in hits: score += hit.weight * 10

        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == "NITRO": 
                nitro_time = 180 
            elif hit.type == "SHIELD": 
                player.shield_active = True
            elif hit.type == "REPAIR": 
                lives = min(3, lives + 1)

        # Аварии (уменьшенный хитбокс 80%)
        hit_enemies = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_rect_ratio(0.8))
        hit_obs = pygame.sprite.spritecollide(player, obstacles, True, pygame.sprite.collide_rect_ratio(0.8))
        
        if hit_enemies or hit_obs:
            if player.shield_active:
                player.shield_active = False 
            else:
                lives -= 1
                if lives <= 0:
                    save_score(player_name, score, distance)
                    return {"score": score, "dist": distance}

        if nitro_time > 0: nitro_time -= 1

        distance += (5 * speed_mult) / 60.0
        score += 1 
        
        bg_y = (bg_y + 5 * speed_mult) % SCREEN_HEIGHT
        
        # Отрисовка
        if background:
            screen.blit(background, (0, bg_y))
            screen.blit(background, (0, bg_y - SCREEN_HEIGHT))
        else:
            screen.fill(GRAY)
            pygame.draw.rect(screen, YELLOW, (20, 0, 5, SCREEN_HEIGHT))
            pygame.draw.rect(screen, YELLOW, (375, 0, 5, SCREEN_HEIGHT))
            for y in range(-100, SCREEN_HEIGHT + 100, 60):
                pygame.draw.rect(screen, WHITE, (195, y + (bg_y % 60), 10, 30))

        for sprite in all_sprites:
            if hasattr(sprite, 'draw'):
                sprite.draw(screen) 
            else:
                screen.blit(sprite.image, sprite.rect)

        # UI
        draw_text(screen, f"Score: {score}", FONT, BLACK, 10, 10)
        draw_text(screen, f"Dist: {int(distance)}m", FONT, BLACK, 10, 40)
        draw_text(screen, f"Lives: {lives}", FONT, RED, 10, 70)
        if nitro_time > 0:
            draw_text(screen, "NITRO BOOST!", FONT, MAGENTA, 10, 100)

        pygame.display.flip()
        clock.tick(60)

# --- МЕНЕДЖЕР СОСТОЯНИЙ (State Machine) ---
current_state = "MENU"
player_name = "Player"
stats = None

while True:
    if current_state == "MENU":
        current_state = main_menu()
    elif current_state == "SETTINGS":
        current_state = settings_screen()
    elif current_state == "LEADERBOARD":
        current_state = leaderboard_screen()
    elif current_state == "NAME_INPUT":
        player_name = name_input_screen()
        current_state = "PLAYING"
    elif current_state == "PLAYING":
        stats = game_loop(player_name)
        current_state = "GAME_OVER"
    elif current_state == "GAME_OVER":
        res = game_over_screen(stats)
        current_state = "PLAYING" if res == "RETRY" else "MENU"