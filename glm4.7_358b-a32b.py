#!/usr/bin/env python3

import curses
import random
import time
import math
import sys

# --- Конфигурация ---
REFRESH_RATE = 0.05  # Задержка между кадрами (сек)
BUBBLE_CHANCE = 0.1  # Вероятность появления нового пузырька

# Символы (Псевдографика)
FISH_RIGHT = ["<°)))><", "><(((°>"]
FISH_LEFT = ["><(((°>", "<°)))><"] # Просто отражаем, но можно менять если нужно
GRASS_CHARS = ["'", "`", "|", "╱", "╲"]
CORAL_CHARS = ["*", "░", "▒", "▓", "█"]
BUBBLE_CHARS = ["o", "O", "°"]

# Цвета (будут инициализированы в curses)
C_WATER = 1
C_FISH_1 = 2
C_FISH_2 = 3
C_GRASS = 4
C_CORAL = 5
C_BUBBLE = 6

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bubble(Entity):
    def __init__(self, max_y, max_x):
        x = random.randint(1, max_x - 2)
        y = max_y - 2
        super().__init__(x, y)
        self.speed = random.uniform(0.2, 0.5)
        self.wobble_phase = random.random() * math.pi * 2
        self.char = random.choice(BUBBLE_CHARS)

    def update(self):
        self.y -= self.speed
        # Движение зигзагом
        self.wobble_phase += 0.2
        self.x += math.sin(self.wobble_phase) * 0.5

    def draw(self, stdscr):
        if self.y < 0: return
        try:
            stdscr.addch(int(self.y), int(self.x), self.char, curses.color_pair(C_BUBBLE))
        except curses.error:
            pass

class Fish(Entity):
    def __init__(self, max_y, max_x):
        y = random.randint(2, max_y - 5)
        direction = random.choice([-1, 1]) # -1 влево, 1 вправо
        if direction == 1:
            x = 1
        else:
            x = max_x - 8
        
        super().__init__(x, y)
        self.direction = direction
        self.speed_y = random.uniform(0.05, 0.15)
        self.speed_x = random.uniform(0.2, 0.4) * direction
        self.color = random.choice([C_FISH_1, C_FISH_2])
        self.tail_phase = 0
        # Выбираем спрайт
        self.sprites = FISH_RIGHT if direction == 1 else FISH_LEFT

    def update(self, max_y, max_x):
        self.x += self.speed_x
        self.y += math.sin(self.y * 0.1) * 0.1 # Легкое плавание вверх-вниз
        self.tail_phase += 0.5

        # Разворот на границах
        width = 8 # Длина рыбки
        if self.x > max_x - width:
            self.direction = -1
            self.speed_x = abs(self.speed_x) * -1
            self.sprites = FISH_LEFT
        elif self.x < 1:
            self.direction = 1
            self.speed_x = abs(self.speed_x)
            self.sprites = FISH_RIGHT

        # Границы по Y
        if self.y < 1: self.y = 1
        if self.y > max_y - 2: self.y = max_y - 2

    def draw(self, stdscr):
        # Анимация хвоста (меняем спрайт)
        sprite_idx = int(self.tail_phase) % len(self.sprites)
        sprite = self.sprites[sprite_idx]
        
        try:
            stdscr.addstr(int(self.y), int(self.x), sprite, curses.color_pair(self.color))
        except curses.error:
            pass

class Decor:
    """Статичные объекты: Трава и Кораллы"""
    def __init__(self, x, max_y, type_):
        self.x = x
        self.max_y = max_y
        self.type = type_ # 'grass' or 'coral'
        self.height = random.randint(3, 7)
        self.color = C_GRASS if type_ == 'grass' else C_CORAL
        self.sway_offset = random.random() * math.pi * 2

    def draw(self, stdscr, time_counter):
        if self.type == 'grass':
            # Рисуем траву снизу вверх
            for i in range(self.height):
                y = self.max_y - 1 - i
                # Симуляция покачивания
                sway = int(math.sin(time_counter + self.sway_offset + i) * 1)
                char = GRASS_CHARS[i % len(GRASS_CHARS)]
                try:
                    stdscr.addch(y, self.x + sway, char, curses.color_pair(self.color))
                except curses.error:
                    pass
        elif self.type == 'coral':
            # Рисуем кораллы (куча символов)
            for i in range(self.height):
                y = self.max_y - 1 - i
                # Кораллы шире снизу
                width = 1 if i > self.height // 2 else 2
                char = random.choice(CORAL_CHARS)
                try:
                    stdscr.addch(y, self.x, char, curses.color_pair(self.color))
                    if width == 2:
                         stdscr.addch(y, self.x + 1, char, curses.color_pair(self.color))
                except curses.error:
                    pass

def main(stdscr):
    # Настройка curses
    curses.curs_set(0) # Скрыть курсор
    stdscr.nodelay(1)  # Не ждать ввода
    stdscr.timeout(50)

    # Инициализация цветов
    curses.start_color()
    curses.use_default_colors()
    
    # Инициализация палитры (если терминал поддерживает цвета)
    # Формат: init_pair(id, foreground, background)
    # -1 означает "цвет по умолчанию" (прозрачный фон)
    try:
        curses.init_pair(C_WATER, curses.COLOR_CYAN, -1) # Вода (текст не используется, но для фона в некоторых терминалах)
        curses.init_pair(C_FISH_1, curses.COLOR_RED, -1)
        curses.init_pair(C_FISH_2, curses.COLOR_YELLOW, -1)
        curses.init_pair(C_GRASS, curses.COLOR_GREEN, -1)
        curses.init_pair(C_CORAL, curses.COLOR_MAGENTA, -1)
        curses.init_pair(C_BUBBLE, curses.COLOR_WHITE, curses.COLOR_BLUE) # Белый на синем (или просто светло-синий)
    except:
        # Если цветов мало, будет монохром
        pass

    # Получаем размеры терминала
    max_y, max_x = stdscr.getmaxyx()

    # Создаем объекты
    fishes = [Fish(max_y, max_x) for _ in range(4)]
    bubbles = []
    decors = []

    # Генерация дна
    for x in range(1, max_x - 1, 2):
        r = random.random()
        if r < 0.3:
            decors.append(Decor(x, max_y, 'grass'))
        elif r < 0.45:
            decors.append(Decor(x, max_y, 'coral'))

    time_counter = 0.0

    while True:
        # Обработка ввода (выход по любой клавише)
        key = stdscr.getch()
        if key != -1:
            break

        # Очистка экрана
        stdscr.clear()
        
        # Обновление времени для анимации качания
        time_counter += 0.2

        # 1. Рисуем дно (трава и кораллы)
        for decor in decors:
            decor.draw(stdscr, time_counter)

        # 2. Рисуем и обновляем рыбок
        for fish in fishes:
            fish.update(max_y, max_x)
            fish.draw(stdscr)

        # 3. Генерация и рисование пузырьков
        if random.random() < BUBBLE_CHANCE:
            bubbles.append(Bubble(max_y, max_x))
        
        # Обновляем пузырьки и удаляем те, что улетели
        for b in bubbles[:]:
            b.update()
            b.draw(stdscr)
            if b.y < 0:
                bubbles.remove(b)

        # Обновление экрана
        stdscr.refresh()
        time.sleep(REFRESH_RATE)
        
        # Проверка изменения размера терминала (простой сброс)
        new_max_y, new_max_x = stdscr.getmaxyx()
        if new_max_y != max_y or new_max_x != max_x:
            # При изменении размера просто выходим, чтобы не ломать логику координат
            # В полноценной программе нужно бы пересоздавать объекты
            break

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        # Для корректного выхода по Ctrl+C
        pass