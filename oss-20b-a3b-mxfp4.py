"""
terminal_aquarium.py
~~~~~~~~~~~~~~~~~~~~

Псевдографический скринсейвер «аквариум» для терминала.

Тема: пузырьки, трава, рыбки, кораллы – всё в движении.
Используется стандартный модуль `curses`.  
Поддержка Windows возможна при установке `windows-curses`.

Запуск:
    python3 terminal_aquarium.py

Выход: любая клавиша.
"""

import curses
import random
import time
import sys

# ────────────────────────────────────────────────────────────────────────
# Константы
# ────────────────────────────────────────────────────────────────────────

# Цвета (если терминал их поддерживает)
COLOR_WATER = 1
COLOR_GRASS = 2
COLOR_FISH   = 3
COLOR_CORAL  = 4
COLOR_BUBBLE = 5

# Скорость анимации (кадры в секунду)
FPS = 15
FRAME_DELAY = 1.0 / FPS

# Количество объектов
NUM_FISH    = 6
NUM_BUBBLES = 20
NUM_GRASS   = 15
NUM_CORAL   = 8

# Псевдографика
GRASS_SHAPES = ['|', '‖', '‖', '‖', '‖', '‖', '‖']
BUBBLE_SHAPE = 'O'
FISH_SHAPES  = ['><>', '><>', '><>', '><>', '><>', '><>']
CORAL_SHAPES = ['^', 'v', 'v', 'v', 'v', '^']

# ────────────────────────────────────────────────────────────────────────
# Классы объектов
# ────────────────────────────────────────────────────────────────────────

class BaseObject:
    """Базовый класс. Отрисовка оборачивается в try/except."""
    def draw(self, stdscr):
        try:
            stdscr.addstr(
                self.y,
                self.x,
                self.shape,
                curses.color_pair(self.color) if self.color else 0
            )
        except curses.error:
            pass  # иногда выходит за пределы – игнорируем


class Fish(BaseObject):
    """Простая рыбка, двигающаяся по горизонтали."""
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.y = random.randint(1, max_y - 2)
        self.x = random.randint(1, max_x - 4)
        self.direction = random.choice([-1, 1])  # -1: ←, 1: →
        self.shape = random.choice(FISH_SHAPES)
        self.color = COLOR_FISH

    def move(self):
        self.x += self.direction
        # Откат от стенок
        if self.x <= 1:
            self.x = 1
            self.direction = 1
        elif self.x + len(self.shape) >= self.max_x - 1:
            self.x = self.max_x - len(self.shape) - 2
            self.direction = -1


class Bubble(BaseObject):
    """Пузырек, поднимающийся вверх."""
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - 2
        self.shape = BUBBLE_SHAPE
        self.color = COLOR_BUBBLE

    def move(self):
        self.y -= 1
        if self.y <= 1:
            self.y = self.max_y - 2
            self.x = random.randint(1, self.max_x - 2)


class Grass(BaseObject):
    """Трава у дна."""
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - 1
        self.shape = random.choice(GRASS_SHAPES)
        self.color = COLOR_GRASS


class Coral(BaseObject):
    """Кораллы у дна."""
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - 1
        self.shape = random.choice(CORAL_SHAPES)
        self.color = COLOR_CORAL


# ────────────────────────────────────────────────────────────────────────
# Основная функция
# ────────────────────────────────────────────────────────────────────────

def main(stdscr):
    # Инициализация curses
    curses.curs_set(0)          # скрыть курсор (если поддерживается)
    stdscr.nodelay(True)        # неблокирующий ввод
    stdscr.timeout(0)           # без ожидания

    # Цвета
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(COLOR_WATER, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(COLOR_GRASS, curses.COLOR_GREEN, curses.COLOR_BLUE)
        curses.init_pair(COLOR_FISH,   curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(COLOR_CORAL,  curses.COLOR_MAGENTA, curses.COLOR_BLUE)
        curses.init_pair(COLOR_BUBBLE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        # Устанавливаем фон «воды»
        stdscr.bkgd(' ', curses.color_pair(COLOR_WATER))
    else:
        # Если цвета не поддерживаются – просто очищаем экран
        stdscr.erase()

    max_y, max_x = stdscr.getmaxyx()

    # Создаём объекты
    fish_list   = [Fish(max_y, max_x)   for _ in range(NUM_FISH)]
    bubble_list = [Bubble(max_y, max_x) for _ in range(NUM_BUBBLES)]
    grass_list  = [Grass(max_y, max_x)  for _ in range(NUM_GRASS)]
    coral_list  = [Coral(max_y, max_x) for _ in range(NUM_CORAL)]

    # Основной цикл
    while True:
        # Проверка ввода (выход при любой клавише)
        if stdscr.getch() != -1:
            break

        # Очистка экрана (фон уже установлен)
        stdscr.erase()

        # Отрисовка объектов
        for g in grass_list:
            g.draw(stdscr)
        for c in coral_list:
            c.draw(stdscr)
        for b in bubble_list:
            b.draw(stdscr)
        for f in fish_list:
            f.draw(stdscr)

        stdscr.refresh()

        # Перемещаем объекты
        for b in bubble_list:
            b.move()
        for f in fish_list:
            f.move()

        # Пауза
        time.sleep(FRAME_DELAY)


# ────────────────────────────────────────────────────────────────────────
# Точка входа
# ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except curses.error as e:
        # Если терминал не поддерживает необходимые функции
        print("Ошибка терминала:", e, file=sys.stderr)
        sys.exit(1)
