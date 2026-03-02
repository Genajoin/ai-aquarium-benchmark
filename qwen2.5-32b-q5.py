# 37 t/s, 26s, с первого раза. вручную только выход по кнопке.

import sys, termios, tty, select # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
t,_=termios.tcgetattr(0),tty.setcbreak(0) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!

import curses
import random
import time

# Константы
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 20
FISH_COUNT = 5
BUBBLE_COUNT = 10
GRASS_COUNT = 5

# Символы для рисования
FISH_SYMBOLS = ['><', '<>']
BUBBLE_SYMBOL = '*'
GRASS_SYMBOL = '|'
CORAL_SYMBOL = '#'

# Инициализация curses
stdscr = curses.initscr()
curses.curs_set(0)
curses.noecho()
curses.cbreak()
stdscr.nodelay(1)

# Функция для рисования элементов
def draw_elements(stdscr, elements):
    stdscr.clear()
    for elem in elements:
        y, x, symbol = elem
        stdscr.addstr(y, x, symbol)
    stdscr.refresh()

# Функция для обновления позиции элементов
def update_elements(elements, width, height):
    for elem in elements:
        y, x, symbol = elem
        if symbol == BUBBLE_SYMBOL:
            elem[0] -= 1  # Пузырьки вверх
        elif symbol in FISH_SYMBOLS:
            elem[1] += random.choice([-1, 0, 1])  # Рыбки случайным образом
            elem[0] += random.choice([-1, 0, 1])  # Рыбки случайным образом
        if elem[0] < 0 or elem[0] >= height or elem[1] < 0 or elem[1] >= width:
            reset_element(elem, width, height)

# Функция для сброса позиции элемента
def reset_element(elem, width, height):
    y, x, symbol = elem
    if symbol == BUBBLE_SYMBOL:
        elem[0] = height - 1
        elem[1] = random.randint(0, width - 1)
    elif symbol in FISH_SYMBOLS:
        elem[0] = random.randint(0, height - 1)
        elem[1] = random.randint(0, width - 1)
    elif symbol == GRASS_SYMBOL:
        elem[0] = height - 1
        elem[1] = random.randint(0, width - 1)
    elif symbol == CORAL_SYMBOL:
        elem[0] = height - 1
        elem[1] = random.randint(0, width - 1)

# Инициализация элементов
elements = []
for _ in range(BUBBLE_COUNT):
    elements.append([random.randint(0, SCREEN_HEIGHT - 1), random.randint(0, SCREEN_WIDTH - 1), BUBBLE_SYMBOL])
for _ in range(FISH_COUNT):
    elements.append([random.randint(0, SCREEN_HEIGHT - 1), random.randint(0, SCREEN_WIDTH - 1), random.choice(FISH_SYMBOLS)])
for _ in range(GRASS_COUNT):
    elements.append([random.randint(0, SCREEN_HEIGHT - 1), random.randint(0, SCREEN_WIDTH - 1), GRASS_SYMBOL])
for _ in range(GRASS_COUNT):
    elements.append([random.randint(0, SCREEN_HEIGHT - 1), random.randint(0, SCREEN_WIDTH - 1), CORAL_SYMBOL])

# Основной цикл
try:
    while True:
        if select.select([sys.stdin],[],[],0)[0]:termios.tcsetattr(0,termios.TCSADRAIN,t);break # ЭТО ВСТАВЛЕНО ВРУЧНУЮ!
        draw_elements(stdscr, elements)
        update_elements(elements, SCREEN_WIDTH, SCREEN_HEIGHT)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
