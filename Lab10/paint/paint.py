import pygame
import sys
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("My Paint")
    
    # 1. Создаем "Холст", на котором будут оставаться рисунки
    canvas = pygame.Surface((640, 480))
    canvas.fill((255, 255, 255)) # Белый фон, как в настоящем Paint
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    # Состояния
    radius = 5
    tool = 'brush'       # Выбранный инструмент: brush, rect, circle, eraser
    color = (0, 0, 0)    # Текущий цвет (по умолчанию черный)
    drawing = False      # Рисуем ли мы прямо сейчас
    start_pos = (0, 0)   # Точка начала для фигур
    last_pos = (0, 0)    # Предыдущая точка для кисти
    
    # Палитра цветов
    colors = {
        pygame.K_r: (255, 0, 0),   # Red
        pygame.K_g: (0, 255, 0),   # Green
        pygame.K_b: (0, 0, 255),   # Blue
        pygame.K_k: (0, 0, 0),     # blacK
    }

    while True:
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held: return
                if event.key == pygame.K_F4 and alt_held: return
                if event.key == pygame.K_ESCAPE: return
                
                # --- ВЫБОР ИНСТРУМЕНТА ---
                if event.key == pygame.K_1: tool = 'brush'
                if event.key == pygame.K_2: tool = 'rect'
                if event.key == pygame.K_3: tool = 'circle'
                if event.key == pygame.K_4: tool = 'eraser'
                
                # --- ВЫБОР ЦВЕТА ---
                if event.key in colors:
                    color = colors[event.key]
                    
                # --- ВЫБОР РАЗМЕРА ---
                if event.key == pygame.K_UP:
                    radius = min(100, radius + 1)
                if event.key == pygame.K_DOWN:
                    radius = max(1, radius - 1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Левый клик
                    drawing = True
                    start_pos = event.pos
                    last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Отпустили левый клик
                    drawing = False
                    
                    # Фиксация фигур на холсте при отпускании мыши
                    if tool == 'rect':
                        rect = pygame.Rect(start_pos[0], start_pos[1], event.pos[0] - start_pos[0], event.pos[1] - start_pos[1])
                        rect.normalize()
                        pygame.draw.rect(canvas, color, rect, radius)
                        
                    elif tool == 'circle':
                        dx = event.pos[0] - start_pos[0]
                        dy = event.pos[1] - start_pos[1]
                        r = int(math.hypot(dx, dy)) # Вычисляем радиус по теореме Пифагора
                        pygame.draw.circle(canvas, color, start_pos, r, min(r, radius))

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    # Кисть и ластик рисуют непрерывно при движении
                    if tool == 'brush':
                        pygame.draw.line(canvas, color, last_pos, event.pos, radius * 2)
                        pygame.draw.circle(canvas, color, event.pos, radius) # Сглаживание краев
                    elif tool == 'eraser':
                        # Ластик - это просто кисть, рисующая белым цветом
                        pygame.draw.line(canvas, (255, 255, 255), last_pos, event.pos, radius * 2)
                        pygame.draw.circle(canvas, (255, 255, 255), event.pos, radius)
                last_pos = event.pos
                
        # 2. Отрисовка
        screen.fill((200, 200, 200)) # Заливаем фон окна серым
        screen.blit(canvas, (0, 0))  # Накладываем наш холст с рисунками
        
        # 3. Предпросмотр фигур (рисуем поверх холста, пока тянем мышь)
        if drawing:
            mouse_pos = pygame.mouse.get_pos()
            if tool == 'rect':
                rect = pygame.Rect(start_pos[0], start_pos[1], mouse_pos[0] - start_pos[0], mouse_pos[1] - start_pos[1])
                rect.normalize()
                pygame.draw.rect(screen, color, rect, radius)
            elif tool == 'circle':
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                r = int(math.hypot(dx, dy))
                pygame.draw.circle(screen, color, start_pos, r, min(r, radius))

        # 4. Интерфейс: выводим текущий инструмент и размер
        ui_text = font.render(f"Tool (1-4): {tool} | Color (R,G,B,K) | Size (Up/Down): {radius}", True, (100, 100, 100))
        screen.blit(ui_text, (10, 10))

        pygame.display.flip()
        clock.tick(120)

if __name__ == '__main__':
    main()