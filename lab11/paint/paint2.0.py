import pygame
import sys
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600)) # Сделал окно чуть больше для удобства
    pygame.display.set_caption("My Paint - Week 11")
    
    # 1. Создаем "Холст", на котором будут оставаться рисунки
    canvas = pygame.Surface((800, 600))
    canvas.fill((255, 255, 255)) # Белый фон, как в настоящем Paint
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    # Состояния
    radius = 5
    tool = 'brush'       # Выбранный инструмент
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

    # --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Функция для вычисления точек новых фигур ---
    def get_shape_points(tool_type, start, end):
        x1, y1 = start
        x2, y2 = end
        
        # ЗАДАНИЕ 2: Прямоугольный треугольник (один прямой угол)
        if tool_type == 'right_tri':
            return [(x1, y1), (x1, y2), (x2, y2)]
            
        # ЗАДАНИЕ 3: Равносторонний треугольник
        elif tool_type == 'eq_tri':
            mid_x = (x1 + x2) / 2
            return [(mid_x, y1), (x1, y2), (x2, y2)]
            
        # ЗАДАНИЕ 4: Ромб
        elif tool_type == 'rhombus':
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            return [(mid_x, y1), (x2, mid_y), (mid_x, y2), (x1, mid_y)]
            
        return []
    # --------------------------------------------------------------------------

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
                
                # выбор инструмента
                if event.key == pygame.K_1: tool = 'brush'
                if event.key == pygame.K_2: tool = 'rect'
                if event.key == pygame.K_3: tool = 'circle'
                if event.key == pygame.K_4: tool = 'eraser'
                # --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ ---
                if event.key == pygame.K_5: tool = 'square'    # Квадрат
                if event.key == pygame.K_6: tool = 'right_tri' # Прямоугольный треугольник
                if event.key == pygame.K_7: tool = 'eq_tri'    # Равносторонний треугольник
                if event.key == pygame.K_8: tool = 'rhombus'   # Ромб
                # -------------------------------
                
                # выбор цвета
                if event.key in colors:
                    color = colors[event.key]
                    
                # выбор размера
                if event.key == pygame.K_UP:
                    radius = min(100, radius + 1)
                if event.key == pygame.K_DOWN:
                    radius = max(1, radius - 1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    drawing = True
                    start_pos = event.pos
                    last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: 
                    drawing = False
                    
                    # Фиксация фигур на холсте при отпускании мыши
                    if tool == 'rect':
                        rect = pygame.Rect(start_pos[0], start_pos[1], event.pos[0] - start_pos[0], event.pos[1] - start_pos[1])
                        rect.normalize()
                        pygame.draw.rect(canvas, color, rect, radius)
                    
                    # --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Отрисовка новых фигур на холсте ---
                    # ЗАДАНИЕ 1: Идеальный квадрат (стороны всегда равны)
                    elif tool == 'square':
                        dx = event.pos[0] - start_pos[0]
                        dy = event.pos[1] - start_pos[1]
                        side = max(abs(dx), abs(dy)) # Берем самую длинную сторону
                        sign_x = 1 if dx > 0 else -1
                        sign_y = 1 if dy > 0 else -1
                        rect = pygame.Rect(start_pos[0], start_pos[1], side * sign_x, side * sign_y)
                        rect.normalize()
                        pygame.draw.rect(canvas, color, rect, radius)
                        
                    elif tool in ['right_tri', 'eq_tri', 'rhombus']:
                        points = get_shape_points(tool, start_pos, event.pos)
                        if len(points) > 2:
                            pygame.draw.polygon(canvas, color, points, radius)
                    # ----------------------------------------------------------------
                        
                    elif tool == 'circle':
                        dx = event.pos[0] - start_pos[0]
                        dy = event.pos[1] - start_pos[1]
                        r = int(math.hypot(dx, dy)) 
                        pygame.draw.circle(canvas, color, start_pos, r, min(r, radius))

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    if tool == 'brush':
                        pygame.draw.line(canvas, color, last_pos, event.pos, radius * 2)
                        pygame.draw.circle(canvas, color, event.pos, radius) 
                    elif tool == 'eraser':
                        pygame.draw.line(canvas, (255, 255, 255), last_pos, event.pos, radius * 2)
                        pygame.draw.circle(canvas, (255, 255, 255), event.pos, radius)
                last_pos = event.pos
                
        # 2. Отрисовка
        screen.fill((200, 200, 200)) 
        screen.blit(canvas, (0, 0))  
        
        # 3. Предпросмотр фигур (рисуем поверх холста, пока тянем мышь)
        if drawing:
            mouse_pos = pygame.mouse.get_pos()
            if tool == 'rect':
                rect = pygame.Rect(start_pos[0], start_pos[1], mouse_pos[0] - start_pos[0], mouse_pos[1] - start_pos[1])
                rect.normalize()
                pygame.draw.rect(screen, color, rect, radius)
            
            # --- ДОБАВЛЕНО ДЛЯ 11 НЕДЕЛИ: Предпросмотр новых фигур ---
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
            # ----------------------------------------------------------
            
            elif tool == 'circle':
                dx = mouse_pos[0] - start_pos[0]
                dy = mouse_pos[1] - start_pos[1]
                r = int(math.hypot(dx, dy))
                pygame.draw.circle(screen, color, start_pos, r, min(r, radius))

        # 4. Интерфейс: выводим текущий инструмент и размер
        ui_text = font.render(f"Tool (1-8): {tool} | Color (R,G,B,K) | Size: {radius}", True, (50, 50, 50))
        screen.blit(ui_text, (10, 10))

        pygame.display.flip()
        clock.tick(120)

if __name__ == '__main__':
    main()