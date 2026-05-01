import pygame
import sys
import math
import datetime
import tools # Импортируем наш файл с заливкой

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("My Paint - TSIS 2")
    
    canvas = pygame.Surface((800, 600))
    canvas.fill((255, 255, 255)) 
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    text_font = pygame.font.SysFont("Arial", 36) # Шрифт для инструмента "Текст"
    
    # Состояния
    radius = 5           # Текущая толщина (по умолчанию 5)
    tool = 'pencil'      # Выбранный инструмент
    color = (0, 0, 0)    
    drawing = False      
    start_pos = (0, 0)   
    last_pos = (0, 0)    
    
    # Переменные для текстового инструмента
    is_typing = False
    text_content = ""
    text_pos = (0, 0)
    
    colors = {
        pygame.K_r: (255, 0, 0),   
        pygame.K_g: (0, 255, 0),   
        pygame.K_b: (0, 0, 255),   
        pygame.K_k: (0, 0, 0),     
    }

    def get_shape_points(tool_type, start, end):
        x1, y1 = start
        x2, y2 = end
        if tool_type == 'right_tri':
            return [(x1, y1), (x1, y2), (x2, y2)]
        elif tool_type == 'eq_tri':
            mid_x = (x1 + x2) / 2
            return [(mid_x, y1), (x1, y2), (x2, y2)]
        elif tool_type == 'rhombus':
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            return [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
        return []

    while True:
        pressed = pygame.key.get_pressed()
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                # --- ИНСТРУМЕНТ ТЕКСТА (Печать) ---
                if is_typing:
                    if event.key == pygame.K_RETURN:
                        # Enter подтверждает текст и печатает его на canvas
                        text_surface = text_font.render(text_content, True, color)
                        canvas.blit(text_surface, text_pos)
                        is_typing = False
                    elif event.key == pygame.K_ESCAPE:
                        # Escape отменяет ввод
                        is_typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        # Удаление последнего символа
                        text_content = text_content[:-1]
                    else:
                        # Добавление символа
                        text_content += event.unicode
                    continue # Пропускаем остальные горячие клавиши во время ввода текста
                
                # --- СОХРАНЕНИЕ ХОЛСТА (Ctrl+S) ---
                if event.key == pygame.K_s and ctrl_held:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"canvas_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Saved as {filename}")
                
                # --- ВЫБОР РАЗМЕРА КИСТИ ---
                if event.key == pygame.K_z: radius = 2   # Small
                if event.key == pygame.K_x: radius = 5   # Medium
                if event.key == pygame.K_c: radius = 10  # Large
                
                # --- ВЫБОР ИНСТРУМЕНТА ---
                if event.key == pygame.K_1: tool = 'pencil'
                if event.key == pygame.K_2: tool = 'rect'
                if event.key == pygame.K_3: tool = 'circle'
                if event.key == pygame.K_4: tool = 'eraser'
                if event.key == pygame.K_5: tool = 'square'    
                if event.key == pygame.K_6: tool = 'right_tri' 
                if event.key == pygame.K_7: tool = 'eq_tri'    
                if event.key == pygame.K_8: tool = 'rhombus'
                if event.key == pygame.K_9: tool = 'line'      # Прямая линия
                if event.key == pygame.K_0: tool = 'fill'      # Заливка
                if event.key == pygame.K_t: tool = 'text'      # Текст
                
                # ВЫБОР ЦВЕТА
                if event.key in colors:
                    color = colors[event.key]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    # Если выбран инструмент Заливки
                    if tool == 'fill':
                        # Вызываем функцию из tools.py
                        tools.flood_fill(canvas, event.pos, color)
                    # Если выбран инструмент Текст
                    elif tool == 'text':
                        is_typing = True
                        text_content = ""
                        text_pos = event.pos
                    else:
                        drawing = True
                        start_pos = event.pos
                        last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing: 
                    drawing = False
                    
                    if tool == 'rect':
                        rect = pygame.Rect(start_pos[0], start_pos[1], event.pos[0] - start_pos[0], event.pos[1] - start_pos[1])
                        rect.normalize()
                        pygame.draw.rect(canvas, color, rect, radius)
                    elif tool == 'square':
                        dx = event.pos[0] - start_pos[0]
                        dy = event.pos[1] - start_pos[1]
                        side = max(abs(dx), abs(dy))
                        sign_x = 1 if dx > 0 else -1
                        sign_y = 1 if dy > 0 else -1
                        rect = pygame.Rect(start_pos[0], start_pos[1], side * sign_x, side * sign_y)
                        rect.normalize()
                        pygame.draw.rect(canvas, color, rect, radius)
                    elif tool in ['right_tri', 'eq_tri', 'rhombus']:
                        points = get_shape_points(tool, start_pos, event.pos)
                        if len(points) > 2:
                            pygame.draw.polygon(canvas, color, points, radius)
                    elif tool == 'circle':
                        dx = event.pos[0] - start_pos[0]
                        dy = event.pos[1] - start_pos[1]
                        r = int(math.hypot(dx, dy)) 
                        pygame.draw.circle(canvas, color, start_pos, r, min(r, radius))
                    # --- ИНСТРУМЕНТ ПРЯМАЯ ЛИНИЯ ---
                    elif tool == 'line':
                        pygame.draw.line(canvas, color, start_pos, event.pos, radius)

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    # --- ИНСТРУМЕНТ КАРАНДАШ (Свободное рисование) ---
                    if tool == 'pencil':
                        pygame.draw.line(canvas, color, last_pos, event.pos, radius)
                    elif tool == 'eraser':
                        pygame.draw.line(canvas, (255, 255, 255), last_pos, event.pos, radius * 2)
                last_pos = event.pos
                
        # 2. Отрисовка
        screen.fill((200, 200, 200)) 
        screen.blit(canvas, (0, 0))  
        
        # 3. Предпросмотр фигур
        if drawing:
            mouse_pos = pygame.mouse.get_pos()
            if tool == 'rect':
                rect = pygame.Rect(start_pos[0], start_pos[1], mouse_pos[0] - start_pos[0], mouse_pos[1] - start_pos[1])
                rect.normalize()
                pygame.draw.rect(screen, color, rect, radius)
            elif tool == 'square':
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                side = max(abs(dx), abs(dy))
                sign_x = 1 if dx > 0 else -1
                sign_y = 1 if dy > 0 else -1
                rect = pygame.Rect(start_pos[0], start_pos[1], side * sign_x, side * sign_y)
                rect.normalize()
                pygame.draw.rect(screen, color, rect, radius)
            elif tool in ['right_tri', 'eq_tri', 'rhombus']:
                points = get_shape_points(tool, start_pos, mouse_pos)
                if len(points) > 2:
                    pygame.draw.polygon(screen, color, points, radius)
            elif tool == 'circle':
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                r = int(math.hypot(dx, dy))
                pygame.draw.circle(screen, color, start_pos, r, min(r, radius))
            # Предпросмотр прямой линии
            elif tool == 'line':
                pygame.draw.line(screen, color, start_pos, mouse_pos, radius)

        # 4. Предпросмотр текста, если мы его сейчас печатаем
        if is_typing:
            text_surface = text_font.render(text_content + "|", True, color) # Добавляем курсор "|"
            screen.blit(text_surface, text_pos)

        # 5. Интерфейс
        ui_text = font.render(f"Tool: {tool} | Size (Z=2, X=5, C=10): {radius} | 9:Line | 0:Fill | T:Text | Ctrl+S:Save", True, (50, 50, 50))
        screen.blit(ui_text, (10, 10))

        pygame.display.flip()
        clock.tick(120)

if __name__ == '__main__':
    main()