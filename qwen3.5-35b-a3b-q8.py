# 25 t/s, 2 min. работало но с ошибкой определения границ через пару секунд. Поправил немного упростив. 
# но есть еще ошибка в пузырьках, хоть и работает дольше.

import curses
import random
import time
import math
import sys

# Проверка размера терминала
MIN_HEIGHT = 20
MIN_WIDTH = 50

class Bubble:
    def __init__(self, max_x, max_y):
        self.x = random.randint(0, int(max_x * 0.9))
        self.y = random.randint(int(max_y * 0.8), int(max_y * 0.95))
        self.speed = random.uniform(0.05, 0.2)
        self.char = random.choice(['o', 'O', '●', '·'])

    def update(self, max_y):
        self.y -= self.speed
        if self.y < -2:
            self.y = max_y
            self.x = random.randint(0, int(max_x * 0.9))

    def draw(self, stdscr, color_pair):
        if 0 <= int(self.y) < stdscr.getmaxyx()[0] and 0 <= int(self.x) < stdscr.getmaxyx()[1]:
            stdscr.addstr(int(self.y), int(self.x), self.char, curses.color_pair(1))

class Fish:
    def __init__(self, max_x, max_y):
        self.x = random.randint(0, int(max_x * 0.9))
        self.y = random.randint(2, int(max_y * 0.9))
        self.speed = random.uniform(0.05, 0.15)
        self.direction = random.choice([1, -1])
        self.char = '»' if self.direction == 1 else '«'

    def update(self, max_x):
        self.x += self.speed * self.direction
        if self.x > max_x + 2:
            self.x = -2
            self.direction = -1
            self.char = '«'
        elif self.x < -2:
            self.x = max_x + 2
            self.direction = 1
            self.char = '»'

    def draw(self, stdscr, color_pair):
        y = int(self.y)
        x = int(self.x)
        if 0 <= y < stdscr.getmaxyx()[0] and 0 <= x < stdscr.getmaxyx()[1]:
            stdscr.addstr(y, x, self.char, curses.color_pair(2) | curses.A_BOLD)

class Plant:
    def __init__(self, x, height):
        self.x = x
        self.height = height

    def draw(self, stdscr, color_pair):
        y = stdscr.getmaxyx()[0]
        for i in range(self.height):
            draw_y = y - i - 1
            sway = 0
            if i > 2 and time.time() > 0:
                sway = int(math.sin(time.time() * 1.5 + self.x) * 1)
            draw_x = self.x + sway
            if 0 <= draw_y < stdscr.getmaxyx()[0] and 0 <= draw_x < stdscr.getmaxyx()[1]:
                stdscr.addstr(draw_y, draw_x, '|', curses.color_pair(3))

def main(stdscr):
    # Проверка размеров перед инициализацией цветов
    h, w = stdscr.getmaxyx()
    if h < MIN_HEIGHT or w < MIN_WIDTH:
        # Если слишком мелко, пробуем переключиться в полноэкранный режим или выходим
        stdscr.clear()
        stdscr.addstr(0, 0, f"Минимальный размер: {MIN_WIDTH}x{MIN_HEIGHT}")
        stdscr.refresh()
        stdscr.getch()
        return

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)

    max_y, max_x = stdscr.getmaxyx()

    # Инициализация сущностей
    bubbles = [Bubble(max_x, max_y) for _ in range(40)]
    fish = [Fish(max_x, max_y) for _ in range(6)]
    
    plants = []
    corals = []
    
    # Растения и кораллы по низу
    for x in range(0, max_x, 20):
        if random.random() > 0.4:
            h_plant = random.randint(3, 10)
            plants.append(Plant(x, h_plant))
        else:
            h_coral = random.randint(2, 8)
            corals.append(Plant(x, h_coral))

    # Основной цикл
    try:
        while True:
            key = stdscr.getch()
            if key in [ord('q'), ord('Q'), 27]:
                break

            stdscr.clear()
            
            # Рисуем фон (темно-синий)
            for y in range(max_y):
                for x in range(max_x):
                    try:
                        stdscr.addstr(y, x, ' ', curses.color_pair(4) | curses.A_DIM)
                    except curses.error:
                        pass

            # Рисуем кораллы
            for coral in corals:
                coral.draw(stdscr, curses.color_pair(3))

            # Рисуем растения
            for plant in plants:
                plant.draw(stdscr, curses.color_pair(3) | curses.A_BOLD)

            # Обновляем и рисуем пузырьки
            for bubble in bubbles:
                bubble.update(max_y)
                bubble.draw(stdscr, curses.color_pair(1) | curses.A_BOLD)

            # Обновляем и рисуем рыбок
            for fish_item in fish:
                fish_item.update(max_x)
                fish_item.draw(stdscr, curses.color_pair(2) | curses.A_BOLD)

            stdscr.refresh()
            time.sleep(0.05)
            
    except curses.error:
        pass
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
