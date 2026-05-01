import pygame
from collections import deque

def flood_fill(surface, pos, fill_color):
    """
    Алгоритм заливки (Flood-Fill).
    Использует get_at() и set_at() согласно требованиям TSIS 2.
    """
    # Получаем цвет пикселя, на который кликнули
    start_color = surface.get_at(pos)
    
    # Если цвет пикселя уже совпадает с цветом заливки, ничего не делаем
    if start_color == fill_color:
        return

    width, height = surface.get_size()
    queue = deque([pos])
    visited = set([pos])

    # Пока очередь не пуста, проверяем соседние пиксели
    while queue:
        x, y = queue.popleft()
        
        # Красим текущий пиксель
        surface.set_at((x, y), fill_color)

        # Проверяем 4 соседних пикселя (верх, низ, лево, право)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            
            # Убеждаемся, что не вышли за границы экрана
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    # Если цвет соседа совпадает со стартовым цветом, добавляем его в очередь
                    if surface.get_at((nx, ny)) == start_color:
                        visited.add((nx, ny))
                        queue.append((nx, ny))