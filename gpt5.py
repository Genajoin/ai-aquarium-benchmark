#!/usr/bin/env python3
# Точного названия модели не известно 25.02.26. ошибка. исправил.
# выход q

import curses
import random
import time
import math

FPS = 15
FISH_COUNT = 8
BUBBLE_RATE = 0.3

FISH_SHAPES_RIGHT = [
    "><>",
    ">))'>",
    ">)))'>",
    "><))'>",
]

FISH_SHAPES_LEFT = [
    "<><",
    "<'((<",
    "<'(((<",
    "<'((><",
]

CORAL_SHAPES = [
    "Ψ",
    "♣",
    "♠",
    "¶",
]

GRASS_CHAR = "|"


class Fish:
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.reset()

    def reset(self):
        self.y = random.randint(2, self.max_y - 5)
        self.x = random.randint(2, self.max_x - 10)
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(0.2, 0.6)
        self.shape = random.choice(
            FISH_SHAPES_RIGHT if self.dir == 1 else FISH_SHAPES_LEFT
        )
        self.phase = random.random() * math.pi

    def update(self):
        self.x += self.dir * self.speed
        self.y += math.sin(time.time() * 2 + self.phase) * 0.2

        if self.x < 1 or self.x > self.max_x - len(self.shape) - 1:
            self.dir *= -1
            self.shape = random.choice(
                FISH_SHAPES_RIGHT if self.dir == 1 else FISH_SHAPES_LEFT
            )

    def draw(self, stdscr):
        try:
            stdscr.addstr(int(self.y), int(self.x), self.shape)
        except:
            pass


class Bubble:
    def __init__(self, max_y, max_x):
        self.max_y = max_y
        self.max_x = max_x
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - 2
        self.char = random.choice(["o", "O", "°", "."])
        self.speed = random.uniform(0.1, 0.4)

    def update(self):
        self.y -= self.speed
        self.x += random.uniform(-0.2, 0.2)

    def draw(self, stdscr):
        if 0 < self.y < self.max_y - 1:
            try:
                stdscr.addstr(int(self.y), int(self.x), self.char)
            except:
                pass


def draw_seabed(stdscr, max_y, max_x, tick):
    # песок (не трогаем последний столбец)
    for x in range(max_x - 1):
        try:
            stdscr.addstr(max_y - 1, x, "~")
        except curses.error:
            pass

    # трава
    for x in range(0, max_x - 1, 3):
        height = 1 + int((math.sin(tick / 5 + x) + 1))
        for h in range(height):
            y = max_y - 2 - h
            if 0 <= y < max_y - 1:
                try:
                    stdscr.addstr(y, x, GRASS_CHAR)
                except curses.error:
                    pass

    # кораллы
    for x in range(5, max_x - 5, 20):
        try:
            stdscr.addstr(max_y - 2, x, random.choice(CORAL_SHAPES))
        except curses.error:
            pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    max_y, max_x = stdscr.getmaxyx()

    fishes = [Fish(max_y, max_x) for _ in range(FISH_COUNT)]
    bubbles = []

    tick = 0

    while True:
        stdscr.erase()

        key = stdscr.getch()
        if key == ord("q"):
            break

        # обновление рыб
        for fish in fishes:
            fish.update()
            fish.draw(stdscr)

        # создание пузырей
        if random.random() < BUBBLE_RATE:
            bubbles.append(Bubble(max_y, max_x))

        # обновление пузырей
        for bubble in bubbles[:]:
            bubble.update()
            bubble.draw(stdscr)
            if bubble.y < 1:
                bubbles.remove(bubble)

        draw_seabed(stdscr, max_y, max_x, tick)

        stdscr.refresh()
        tick += 1
        time.sleep(1 / FPS)


if __name__ == "__main__":
    curses.wrapper(main)