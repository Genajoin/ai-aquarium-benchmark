# 18 t/s, 2 min. ошибка выхода за границы. исправил.

#!/usr/bin/env python3
import curses
import random
import time
import sys

FISH_TYPES = [
    "<[]>", "<===>", "<o-o>", "<*-*>", "<~.~>"
]
BUBBLES = ["o", "O", "°"]
SEAWEED_FRAGS = ["|||", "|/|", "/|\\", "|||", "|\\|"]
CORAL_FRAGS = ["^^^", "/^\\", "^~^", "/~\\", "^^^"]

class Fish:
    def __init__(self, y, x, direction=1):
        self.y = y
        self.x = x
        self.direction = direction
        self.type = random.choice(FISH_TYPES)
        self.speed = random.uniform(0.05, 0.2)
        self.last_move = 0.0

    def update(self, width):
        self.x += self.direction * self.speed
        # Отскок — с учётом длины строки
        if self.x <= 0 or self.x >= width - len(self.type):
            self.direction *= -1
        if random.random() < 0.01:
            self.direction *= -1

    def draw(self, stdscr, width):
        # Проверка границ
        x_int = int(self.x)
        if 0 <= x_int < width and len(self.type) <= width - x_int:
            stdscr.addstr(int(self.y), x_int, self.type, curses.color_pair(3))


class Bubble:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.speed = random.uniform(0.03, 0.15)
        self.char = random.choice(BUBBLES)

    def update(self):
        self.y -= self.speed

    def draw(self, stdscr, width):
        if 0 <= self.x < width and self.y >= 0:
            stdscr.addstr(int(self.y), self.x, self.char, curses.color_pair(4))


class Seaweed:
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.segments = [random.choice(SEAWEED_FRAGS) for _ in range(height // 3)]
        self.phase = random.uniform(0, 2 * 3.14159)

    def draw(self, stdscr, frame_time, width):
        sway = int(2 * (frame_time + self.phase) % 3) - 1  # -1, 0, 1
        for i, seg in enumerate(self.segments):
            y = self.height - i * 3 - 1
            # Проверка границ
            if 0 <= y < curses.LINES and 0 <= self.x + sway < width:
                try:
                    stdscr.addstr(y, self.x + sway, seg, curses.color_pair(2))
                except curses.error:
                    pass  # Игнорируем, если вышли за границы


class Coral:
    def __init__(self, x, height):
        self.x = x
        self.height = height
        self.type = random.choice(CORAL_FRAGS)

    def draw(self, stdscr, y_base, width):
        if 0 <= y_base < curses.LINES and 0 <= self.x < width:
            try:
                stdscr.addstr(y_base, self.x, self.type, curses.color_pair(5))
            except curses.error:
                pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_BLUE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)

    height, width = stdscr.getmaxyx()

    # Инициализация с учётом границ
    fishes = [Fish(random.randint(3, height - 5), random.randint(1, width - 10), random.choice([1, -1])) for _ in range(min(5, width // 4))]
    bubbles = [Bubble(height, random.randint(2, width - 2)) for _ in range(10)]
    seaweeds = [Seaweed(x, random.randint(5, height // 2)) for x in range(2, width - 4, max(5, width // 10))]
    corals = [Coral(x, random.randint(5, 10)) for x in range(5, width - 5, max(8, width // 8))]

    start_time = time.time()

    try:
        while True:
            stdscr.clear()
            frame_time = time.time() - start_time

            # Фон
            for y in range(1, height - 1):
                try:
                    stdscr.addstr(y, 0, " " * width, curses.color_pair(1))
                except curses.error:
                    pass

            # Рыбки
            for fish in fishes:
                fish.update(width)
                fish.draw(stdscr, width)

            # Пузырьки
            for b in bubbles[:]:
                b.update()
                b.draw(stdscr, width)
                if b.y <= 1:
                    bubbles.remove(b)
            if len(bubbles) < 15 and random.random() < 0.1:
                bubbles.append(Bubble(height, random.randint(2, width - 2)))

            # Водоросли
            for w in seaweeds:
                w.draw(stdscr, frame_time, width)

            # Кораллы
            for c in corals:
                c.draw(stdscr, height - 4, width)

            # Песок — безопасно
            sand_len = min(width, 100)  # не больше 100 символов
            sand = "'" * sand_len
            try:
                stdscr.addstr(height - 1, 0, sand, curses.color_pair(4))
            except curses.error:
                pass

            key = stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break

            stdscr.refresh()
            time.sleep(0.03)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
