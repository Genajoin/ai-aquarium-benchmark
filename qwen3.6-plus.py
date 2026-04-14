#!/usr/bin/env python3
"""
Терминальный скринсейвер "Аквариум"
Псевдографика: пузырьки, трава, рыбки, кораллы
"""

import curses
import random
import time
import math


class Aquarium:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.bubbles = []
        self.fishes = []
        self.seaweeds = []
        self.corals = []
        self.particles = []
        
        self.init_elements()
        
    def init_elements(self):
        # Инициализация пузырьков
        for _ in range(15):
            self.bubbles.append({
                'x': random.randint(2, self.width - 4),
                'y': random.randint(self.height // 2, self.height - 3),
                'speed': random.uniform(0.3, 0.8),
                'char': random.choice(['○', '∘', '·', '•']),
                'phase': random.uniform(0, 2 * math.pi)
            })
        
        # Инициализация рыбок
        fish_shapes = [
            ['><)))º>', 'º><((><'],
            ['><> ', ' ><><'],
            ['🐟', '🐠'],  # Если терминал поддерживает emoji
            ['>>>', '<<<'],
        ]
        
        for _ in range(5):
            direction = random.choice([-1, 1])
            shape = random.choice(fish_shapes)
            self.fishes.append({
                'x': random.randint(5, self.width - 15),
                'y': random.randint(3, self.height - 8),
                'direction': direction,
                'speed': random.uniform(0.5, 1.5),
                'shape': shape[0] if direction == 1 else shape[1],
                'color': random.randint(1, 6),
                'tail_phase': 0
            })
        
        # Инициализация водорослей
        for i in range(0, self.width, random.randint(8, 15)):
            height = random.randint(4, 8)
            self.seaweeds.append({
                'x': i + random.randint(0, 3),
                'height': height,
                'phase': random.uniform(0, 2 * math.pi)
            })
        
        # Инициализация кораллов
        coral_shapes = ['♠', '♣', '♦', '⊕', '◊']
        for _ in range(8):
            self.corals.append({
                'x': random.randint(5, self.width - 5),
                'y': self.height - 2,
                'height': random.randint(2, 4),
                'shape': random.choice(coral_shapes),
                'color': random.randint(1, 5)
            })
    
    def draw_border(self):
        # Верхняя и нижняя границы
        try:
            self.stdscr.addstr(0, 0, '╔' + '═' * (self.width - 2) + '╗')
            self.stdscr.addstr(self.height - 1, 0, '╚' + '═' * (self.width - 2) + '╝')
            for y in range(1, self.height - 1):
                self.stdscr.addstr(y, 0, '║')
                self.stdscr.addstr(y, self.width - 1, '║')
        except curses.error:
            pass
    
    def draw_water(self):
        # Водная поверхность
        try:
            water_chars = ['≈', '≈', '≈', '≈', '≈']
            for x in range(1, self.width - 1):
                char = water_chars[int(time.time() * 2 + x) % len(water_chars)]
                self.stdscr.addch(1, x, char, curses.color_pair(4))
        except curses.error:
            pass
    
    def update_bubbles(self):
        for bubble in self.bubbles:
            # Движение вверх с колебанием
            bubble['y'] -= bubble['speed']
            bubble['x'] += math.sin(bubble['phase']) * 0.3
            bubble['phase'] += 0.05
            
            # Если пузырёк достиг верха - перезапуск
            if bubble['y'] < 2:
                bubble['y'] = self.height - 3
                bubble['x'] = random.randint(2, self.width - 4)
            
            # Отрисовка
            try:
                x = int(bubble['x'])
                y = int(bubble['y'])
                if 1 < x < self.width - 1 and 1 < y < self.height - 1:
                    self.stdscr.addch(y, x, bubble['char'], curses.color_pair(7))
            except curses.error:
                pass
    
    def update_fishes(self):
        for fish in self.fishes:
            # Движение
            fish['x'] += fish['speed'] * fish['direction']
            fish['tail_phase'] += 0.2
            
            # Разворот у границ
            if fish['x'] >= self.width - 10 or fish['x'] <= 3:
                fish['direction'] *= -1
                # Смена направления "хвоста"
                shapes = ['><)))º>', 'º><((><']
                fish['shape'] = shapes[0] if fish['direction'] == 1 else shapes[1]
            
            # Колебание по вертикали
            fish['y'] += math.sin(fish['tail_phase'] * 0.5) * 0.2
            
            # Отрисовка
            try:
                x = int(fish['x'])
                y = int(fish['y'])
                color = curses.color_pair(fish['color']) | curses.A_BOLD
                for i, char in enumerate(fish['shape']):
                    if 1 < x + i < self.width - 1 and 1 < y < self.height - 1:
                        self.stdscr.addch(y, x + i, char, color)
            except curses.error:
                pass
    
    def update_seaweeds(self):
        time_factor = time.time() * 0.5
        
        for seaweed in self.seaweeds:
            base_x = seaweed['x']
            phase = seaweed['phase']
            
            # Отрисовка сегментов водоросли
            for h in range(seaweed['height']):
                y = self.height - 2 - h
                # Колебание
                offset = math.sin(time_factor + phase + h * 0.4) * 1.5
                x = int(base_x + offset)
                
                if 1 < x < self.width - 1 and 1 < y < self.height - 1:
                    if h == 0:
                        char = '╥'  # Основание
                    elif h == seaweed['height'] - 1:
                        char = '╨'  # Верхушка
                    else:
                        char = '│'  # Стебель
                    
                    self.stdscr.addch(y, x, char, curses.color_pair(2) | curses.A_BOLD)
    
    def update_corals(self):
        for coral in self.corals:
            for h in range(coral['height']):
                y = coral['y'] - h
                width = max(1, coral['height'] - h)
                
                for w in range(width):
                    x = coral['x'] - width // 2 + w
                    try:
                        if h == 0:
                            char = '▓'
                        else:
                            char = coral['shape']
                        
                        if 1 < x < self.width - 1 and 1 < y < self.height - 1:
                            self.stdscr.addch(y, x, char, 
                                           curses.color_pair(coral['color']) | curses.A_BOLD)
                    except curses.error:
                        pass
    
    def draw_info(self):
        # Информация в углу
        try:
            info = f"🐠 {len(self.fishes)} | 💧 {len(self.bubbles)}"
            self.stdscr.addstr(1, self.width - len(info) - 2, info, 
                             curses.color_pair(7) | curses.A_BOLD)
        except curses.error:
            pass
    
    def update(self):
        self.stdscr.clear()
        
        # Фон - вода
        try:
            for y in range(2, self.height - 1):
                for x in range(1, self.width - 1):
                    if random.random() < 0.001:
                        self.stdscr.addch(y, x, '·', curses.color_pair(4))
        except curses.error:
            pass
        
        self.draw_border()
        self.draw_water()
        self.update_corals()
        self.update_seaweeds()
        self.update_bubbles()
        self.update_fishes()
        self.draw_info()
        
        self.stdscr.refresh()


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    
    # Цветовые пары
    curses.init_pair(1, curses.COLOR_RED, -1)      # Красные рыбки
    curses.init_pair(2, curses.COLOR_GREEN, -1)     # Зелёные водоросли
    curses.init_pair(3, curses.COLOR_YELLOW, -1)    # Жёлтые элементы
    curses.init_pair(4, curses.COLOR_CYAN, -1)      # Вода
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)   # Кораллы
    curses.init_pair(6, curses.COLOR_BLUE, -1)      # Синие рыбки
    curses.init_pair(7, curses.COLOR_WHITE, -1)     # Белые пузырьки


def main(stdscr):
    # Настройка curses
    curses.curs_set(0)  # Скрыть курсор
    stdscr.nodelay(True)  # Неблокирующий ввод
    stdscr.timeout(50)  # Таймаут для обновления
    
    init_colors()
    
    # Получение размеров
    curses.update_lines_cols()
    
    aquarium = Aquarium(stdscr)
    
    # Главный цикл
    while True:
        key = stdscr.getch()
        
        if key == ord('q') or key == 27:  # q или Esc для выхода
            break
        
        aquarium.update()


if __name__ == '__main__':
    print("Запуск аквариума... (нажмите 'q' или Esc для выхода)")
    time.sleep(1)
    curses.wrapper(main)
