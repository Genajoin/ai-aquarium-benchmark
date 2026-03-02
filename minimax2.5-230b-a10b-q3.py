# 12 t/s, 0 min. С первого раза хоть и q3


import curses
import random
import time
import math

# Конфигурация
WIDTH = 120
HEIGHT = 40
BUBBLE_COUNT = 12
FISH_COUNT = 9
CORAL_COUNT = 5

# Символы для псевдографики
BUBBLE_CHARS = ['o', 'O', '●', '○']
FISH_CHARS = ['><>', '><>', '🐟']
GRASS_CHARS = ['\\', '|', '/']
WAVE_CHARS = ['~', '≈', '≋']

class Bubble:
    def __init__(self, width, height):
        self.x = random.randint(1, width - 2)
        self.y = height - 1
        self.size = random.choice([1, 2, 3])
        self.speed = random.uniform(0.5, 1.5)
        self.char = random.choice(BUBBLE_CHARS)
    
    def move(self):
        self.y -= self.speed
        self.x += random.uniform(-0.2, 0.2)
        return self.y > 0
    
    def draw(self, stdscr):
        if 0 < self.x < WIDTH - 1 and 0 < self.y < HEIGHT - 1:
            stdscr.addstr(int(self.y), int(self.x), self.char)

class Fish:
    def __init__(self, width, height):
        self.x = random.randint(5, width - 5)
        self.y = random.randint(5, height - 6)
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(0.3, 0.8)
        self.color = random.randint(1, 7)
        self.char = '><>' if self.direction > 0 else '<><'
    
    def move(self, width, height):
        self.x += self.speed * self.direction
        if self.x < 2 or self.x > width - 3:
            self.direction *= -1
            self.char = '><>' if self.direction > 0 else '<><'
        # Немного изменяем высоту
        self.y += random.uniform(-0.1, 0.1)
        self.y = max(3, min(height - 3, self.y))
    
    def draw(self, stdscr):
        if 0 < self.x < WIDTH - 1 and 0 < self.y < HEIGHT - 1:
            try:
                stdscr.addstr(int(self.y), int(self.x), self.char, curses.color_pair(self.color))
            except curses.error:
                pass

class Aquarium:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.width = WIDTH
        self.height = HEIGHT
        self.bubbles = [Bubble(self.width, self.height) for _ in range(BUBBLE_COUNT)]
        self.fish = [Fish(self.width, self.height) for _ in range(FISH_COUNT)]
        self.frame = 0
    
    def draw_background(self):
        # Небо и вода
        for y in range(self.height):
            for x in range(self.width):
                if y < 2:
                    self.stdscr.addch(y, x, '~', curses.color_pair(8))
                elif y == 2:
                    self.stdscr.addch(y, x, '≈', curses.color_pair(8))
                else:
                    self.stdscr.addch(y, x, ' ', curses.color_pair(9))
        
        # Водоросли
        for i in range(CORAL_COUNT):
            coral_x = 5 + i * 25
            coral_height = random.randint(3, 6)
            for j in range(coral_height):
                y = self.height - 2 - j
                sway = math.sin(self.frame / 10 + j) * 0.5
                char = '\\' if j % 3 == 0 else ('|' if j % 3 == 1 else '/')
                if 0 <= coral_x + sway < self.width - 1:
                    try:
                        self.stdscr.addstr(y, int(coral_x + sway), char, curses.color_pair(10))
                    except curses.error:
                        pass
    
    def draw_sand(self):
        # Песок на дне
        for x in range(self.width):
            y = self.height - 1
            char = random.choice(['_', '.', ',', '`'])
            try:
                self.stdscr.addstr(y, x, char, curses.color_pair(11))
            except curses.error:
                pass
    
    def update(self):
        self.frame += 1
        
        # Обновление пузырей
        for bubble in self.bubbles:
            if not bubble.move():
                # Перемещаем на дно
                bubble.x = random.randint(1, self.width - 2)
                bubble.y = self.height - 2
        
        # Обновление рыбок
        for fish in self.fish:
            fish.move(self.width, self.height)
    
    def draw(self):
        self.stdscr.clear()
        self.draw_background()
        self.draw_sand()
        
        # Рисуем рыбок
        for fish in self.fish:
            fish.draw(self.stdscr)
        
        # Рисуем пузыри
        for bubble in self.bubbles:
            bubble.draw(self.stdscr)
        
        self.stdscr.refresh()

def main(stdscr):
    # Настройка curses
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(10, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    aquarium = Aquarium(stdscr)
    
    # Главный цикл
    while True:
        aquarium.draw()
        aquarium.update()
        time.sleep(0.1)
        
        # Выход по нажатию любой клавиши
        stdscr.nodelay(True)
        key = stdscr.getch()
        if key != -1:
            break

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
