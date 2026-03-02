#!/usr/bin/env python3
# пришлось вручную править - пыталась обрабатывать случай отсутствия библиотеки curses


import os
import sys
import time
import random
import math
import curses

# Определение класса Fish
class Fish:
    def __init__(self, x, y, color, direction):
        self.x = x
        self.y = y
        self.color = color
        self.direction = direction
        self.speed = random.uniform(0.1, 0.3)
        self.shape = random.choice(['><>', '><>', '><>', '<<>'])
        self.wave_offset = random.uniform(0, 2 * math.pi)
        
    def update(self, width, height):
        self.x += self.direction * self.speed
        self.wave_offset += 0.1
        self.y += math.sin(self.wave_offset) * 0.2
        
        if self.x <= 1 or self.x >= width - len(self.shape) - 1:
            self.direction *= -1
            self.shape = self.shape[::-1]
            
        if self.y < 3:
            self.y = 3
        elif self.y > height - 3:
            self.y = height - 3
            
    def draw(self, aquarium, win):
        try:
            if aquarium.has_colors and win:
                win.addstr(int(self.y), int(self.x), self.shape, curses.color_pair(self.color))
            else:
                aquarium.put_char(int(self.y), int(self.x), self.shape[0])
        except:
            pass

# Определение класса Bubble
class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.1, 0.3)
        self.size = random.choice(['o', 'O', '0'])
        self.wobble = random.uniform(0, 2 * math.pi)
        
    def update(self, height):
        self.y -= self.speed
        self.wobble += 0.1
        self.x += math.sin(self.wobble) * 0.3
        
    def draw(self, aquarium, win):
        if 0 < self.y < aquarium.height - 1:
            if aquarium.has_colors and win:
                win.addstr(int(self.y), int(self.x), self.size, curses.color_pair(7))
            else:
                aquarium.put_char(int(self.y), int(self.x), self.size)

# Определение класса Seaweed
class Seaweed:
    def __init__(self, x, y, height):
        self.x = x
        self.base_y = y
        self.height = height
        self.sway_offset = random.uniform(0, 2 * math.pi)
        self.character = random.choice(['~', 'v', '^', '|'])
        
    def draw(self, aquarium, win, time_offset):
        sway = math.sin(time_offset + self.sway_offset) * 0.5
        segments = int(self.height)
        
        for i in range(segments):
            y = self.base_y - i
            if y > 0:
                x_offset = int(sway * (i / segments))
                if aquarium.has_colors and win:
                    win.addstr(y, self.x + x_offset, self.character, curses.color_pair(2))
                else:
                    aquarium.put_char(y, self.x + x_offset, self.character)

# Определение класса Coral
class Coral:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice([3, 4, 5])
        
    def draw(self, aquarium, win):
        for i, line in enumerate(self.shape.split('\n')):
            if self.y - i > 0:
                if aquarium.has_colors and win:
                    win.addstr(self.y - i, self.x, line, curses.color_pair(self.color))
                else:
                    for j, char in enumerate(line):
                        if char != ' ':
                            aquarium.put_char(self.y - i, self.x + j, char)

# Определение класса TerminalAquarium
class TerminalAquarium:
    def __init__(self):
        # Получаем размер терминала
        try:
            self.width, self.height = os.get_terminal_size()
        except:
            self.width, self.height = 80, 24
        
        # Ограничиваем минимальный размер
        self.width = max(30, self.width)
        self.height = max(15, self.height)
        
        # Инициализация переменных
        self.time_offset = 0
        self.fishes = []
        self.bubbles = []
        self.seaweeds = []
        self.corals = []
        self.running = True
        
        # Инициализация curses, если доступно
        self.has_colors = False
        self.stdscr = None
        
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)
        self.has_colors = curses.has_colors()
        if self.has_colors:
            curses.start_color()
            self.init_colors()
        
        # Создаем аквариум
        self.init_aquarium()
    
    def init_colors(self):
        
        # Определение цветов
        colors = [
            (1, curses.COLOR_RED, curses.COLOR_RED),
            (2, curses.COLOR_GREEN, curses.COLOR_GREEN),
            (3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA),
            (4, curses.COLOR_CYAN, curses.COLOR_CYAN),
            (5, curses.COLOR_YELLOW, curses.COLOR_YELLOW),
            (6, curses.COLOR_BLUE, curses.COLOR_BLUE),
            (7, curses.COLOR_WHITE, curses.COLOR_WHITE),
        ]
        
        for i, fg, bg in colors:
            curses.init_pair(i, fg, bg)
    
    def init_aquarium(self):
        print(f"Размер терминала: {self.width}x{self.height}")
        
        # Добавление рыбок
        for _ in range(random.randint(3, 6)):
            x = random.randint(5, self.width - 10)
            y = random.randint(5, self.height - 5)
            color = random.randint(1, 6)
            direction = random.choice([1, -1])
            self.fishes.append(Fish(x, y, color, direction))
        
        # Добавление кораллов
        coral_shapes = [
            "  _ \n /  \\\n/    \\",
            " /\\\n/  \\",
            "  _ \n / \\\n/   \\",
            "  __ \n /  \\ \n/    \\",
        ]
        
        for _ in range(random.randint(3, 5)):
            x = random.randint(2, self.width - 10)
            y = random.randint(self.height - 10, self.height - 2)
            shape = random.choice(coral_shapes)
            self.corals.append(Coral(x, y, shape))
        
        # Добавление водорослей
        for _ in range(random.randint(5, 8)):
            x = random.randint(1, self.width - 1)
            y = random.randint(self.height - 15, self.height - 3)
            height = random.randint(4, 8)
            self.seaweeds.append(Seaweed(x, y, height))
        
        # Добавление пузырьков
        for _ in range(random.randint(10, 20)):
            x = random.randint(2, self.width - 2)
            y = random.randint(self.height // 2, self.height - 2)
            self.bubbles.append(Bubble(x, y))
    
    def draw_frame(self):
        # Очистка экрана
        if self.stdscr:
            self.stdscr.clear()
        else:
            # Без curses - очищаем с помощью управляющих последовательностей
            sys.stdout.write("\033[H\033[J")
        
        # Отрисовка рамки аквариума
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width-1 or y == 0 or y == self.height-1:
                    char = '#'
                else:
                    char = ' '
                
                if self.has_colors and self.stdscr:
                    # Градиент воды
                    intensity = int(10 + (y / self.height) * 40)
                    if curses.can_change_color():
                        curses.init_color(curses.COLOR_BLUE, 0, 0, intensity)
                    color = curses.color_pair(6)
                else:
                    color = 0
                
                self.put_char(y, x, char, color)
        
        # Отрисовка объектов
        for coral in self.corals:
            coral.draw(self, self.stdscr)
        
        for seaweed in self.seaweeds:
            seaweed.draw(self, self.stdscr, self.time_offset)
        
        for bubble in self.bubbles[:]:
            bubble.draw(self, self.stdscr)
            bubble.update(self.height)
            if bubble.y < 0:
                self.bubbles.remove(bubble)
                x = random.randint(2, self.width - 2)
                y = self.height - 2
                self.bubbles.append(Bubble(x, y))
        
        for fish in self.fishes:
            fish.update(self.width, self.height)
            fish.draw(self, self.stdscr)
        
        # Рандомные пузырьки
        if random.random() < 0.02:
            x = random.randint(2, self.width - 2)
            y = random.randint(self.height // 2, self.height - 2)
            self.bubbles.append(Bubble(x, y))
        
        self.time_offset += 0.1
        
        # Заголовок
        title = "🐠 ТЕРМИНАЛЬНЫЙ АКВАРИУМ 🐠"
        self.put_char(0, 2, title, 7 if self.has_colors and self.stdscr else 0)
        self.put_char(0, self.width - 20, "ESC - выход", 7 if self.has_colors and self.stdscr else 0)
        
        # Обновление экрана
        if self.stdscr:
            self.stdscr.refresh()
        else:
            sys.stdout.flush()
    
    def put_char(self, y, x, char, color=0):
        if self.stdscr and self.has_colors:
            try:
                self.stdscr.addstr(y, x, char, curses.color_pair(color))
            except:
                pass
        else:
            sys.stdout.write(f"\033[{y+1};{x+1}H{char}")
    
    def run(self):
        print("Запуск аквариума... Нажмите ESC для выхода")
        
        self.stdscr.nodelay(True) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
        try:
            while self.running:
                
                if self.stdscr.getch() != -1:  # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
                    break
                
                self.draw_frame()
                
                # Небольшая задержка
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\nПрерывание пользователем")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.stdscr:
            try:
                self.stdscr.keypad(False)
                curses.echo()
                curses.nocbreak()
                curses.endwin()
            except:
                pass
        print("\nАквариум завершен")

if __name__ == "__main__":
    try:
        aquarium = TerminalAquarium()
        aquarium.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
