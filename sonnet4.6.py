"""
🐠 Aquarium Terminal Screensaver
Псевдографический аквариум в терминале
"""

import curses
import random
import time
import math

# ─── Спрайты ───────────────────────────────────────────────────────────────────

FISH_RIGHT = [
    ("><(((°>",   0),
    ("><(('>",    0),
    ("><>",       0),
    ("><))°>",    0),
    ("°><((",     0),  # маленькая
]

FISH_LEFT = [
    ("<°)))><",   0),
    ("<'((><",    0),
    ("<><",       0),
    ("<°((<><",   0),
    ("))<°",      0),
]

BUBBLES = ["o", "O", "°", "·", "∘"]

SEAWEED = ["}", "{", ")", "(", "¿", "?"]

CORAL_SHAPES = [
    ["  /\\  ", " /\\/\\ ", "/    \\"],
    ["  )(  ", " )()( ", "((  ))"],
    ["  **  ", " **** ", "******"],
    [" /||\\  ", " ||||  ", "/||||\\"],
]

SAND_CHARS = [".", ",", "`", "'", "~", "_"]

FISH_COLORS = [
    curses.COLOR_YELLOW,
    curses.COLOR_CYAN,
    curses.COLOR_GREEN,
    curses.COLOR_MAGENTA,
    curses.COLOR_RED,
    curses.COLOR_WHITE,
]

# ─── Классы ────────────────────────────────────────────────────────────────────

class Fish:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        idx = random.randint(0, len(FISH_RIGHT) - 1)
        self.sprite_r = FISH_RIGHT[idx][0]
        self.sprite_l = FISH_LEFT[idx][0]
        self.dir = random.choice([-1, 1])
        self.sprite = self.sprite_r if self.dir == 1 else self.sprite_l
        self.length = len(self.sprite)
        self.x = random.randint(0, max(1, width - self.length))
        self.y = random.randint(2, max(3, height - 6))
        self.speed = random.uniform(0.3, 1.2)
        self.timer = 0.0
        self.color = random.randint(1, 6)
        self.wobble = 0
        self.wobble_speed = random.uniform(0.05, 0.15)

    def update(self, dt):
        self.timer += dt
        self.wobble += self.wobble_speed
        if self.timer >= (1.0 / self.speed):
            self.timer = 0.0
            self.x += self.dir
            # Разворот у стен
            if self.x + self.length >= self.width - 1:
                self.dir = -1
                self.sprite = self.sprite_l
                self.x = self.width - self.length - 1
            elif self.x <= 0:
                self.dir = 1
                self.sprite = self.sprite_r
                self.x = 0
            # Лёгкое вертикальное колебание
            offset = int(math.sin(self.wobble) * 0.7)
            new_y = self.y + offset
            if 2 <= new_y <= self.height - 6:
                self.y = new_y

    def draw(self, stdscr):
        try:
            stdscr.addstr(self.y, self.x, self.sprite,
                          curses.color_pair(self.color) | curses.A_BOLD)
        except curses.error:
            pass


class Bubble:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.x = random.randint(1, max(2, width - 2))
        self.y = height - 4
        self.char = random.choice(BUBBLES)
        self.speed = random.uniform(0.4, 1.0)
        self.timer = 0.0
        self.wobble = random.uniform(0, 6.28)
        self.wobble_speed = random.uniform(0.08, 0.2)
        self.base_x = self.x

    def update(self, dt):
        self.timer += dt
        self.wobble += self.wobble_speed
        if self.timer >= (1.0 / self.speed):
            self.timer = 0.0
            self.y -= 1
            self.x = self.base_x + int(math.sin(self.wobble) * 1.5)
            self.x = max(0, min(self.width - 1, self.x))

    def is_dead(self):
        return self.y < 1

    def draw(self, stdscr):
        try:
            stdscr.addstr(self.y, self.x, self.char,
                          curses.color_pair(7) | curses.A_DIM)
        except curses.error:
            pass


class Seaweed:
    def __init__(self, height, width, x):
        self.height = height
        self.x = x
        self.segs = random.randint(3, min(8, height - 5))
        self.phase = random.uniform(0, 6.28)
        self.speed = random.uniform(0.02, 0.06)
        self.color = random.choice([2, 3])  # зелёный / голубой

    def update(self, dt):
        self.phase += self.speed

    def draw(self, stdscr):
        base_y = self.height - 4
        for i in range(self.segs):
            y = base_y - i
            if y < 1:
                break
            offset = int(math.sin(self.phase + i * 0.7) * 1.5)
            x = self.x + offset
            x = max(0, min(stdscr.getmaxyx()[1] - 1, x))
            char = SEAWEED[i % len(SEAWEED)]
            try:
                stdscr.addstr(y, x, char,
                              curses.color_pair(self.color) | curses.A_BOLD)
            except curses.error:
                pass


class Coral:
    def __init__(self, height, width, x):
        self.x = x
        self.height = height
        self.shape = random.choice(CORAL_SHAPES)
        self.color = random.choice([5, 6, 1])  # магента, жёлтый, красный

    def draw(self, stdscr):
        h = self.height
        for i, line in enumerate(self.shape):
            y = h - 3 - (len(self.shape) - 1 - i)
            if 0 < y < h - 1:
                try:
                    stdscr.addstr(y, self.x, line,
                                  curses.color_pair(self.color) | curses.A_BOLD)
                except curses.error:
                    pass


class AquariumApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(0)

        curses.start_color()
        curses.use_default_colors()
        # пары: 1=красный, 2=зелёный, 3=голубой, 4=синий, 5=маджента, 6=жёлтый, 7=белый
        curses.init_pair(1, curses.COLOR_RED,     -1)
        curses.init_pair(2, curses.COLOR_GREEN,   -1)
        curses.init_pair(3, curses.COLOR_CYAN,    -1)
        curses.init_pair(4, curses.COLOR_BLUE,    -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_YELLOW,  -1)
        curses.init_pair(7, curses.COLOR_WHITE,   -1)
        curses.init_pair(8, curses.COLOR_BLUE,    curses.COLOR_BLUE)  # вода

        self.height, self.width = stdscr.getmaxyx()
        self._init_scene()
        self.last_time = time.time()
        self.bubble_spawn_timer = 0.0

    def _init_scene(self):
        h, w = self.height, self.width
        # Рыбки
        n_fish = max(3, w // 20)
        self.fishes = [Fish(h, w) for _ in range(n_fish)]
        # Водоросли
        n_weeds = max(4, w // 15)
        positions = random.sample(range(2, w - 2), min(n_weeds, w - 4))
        self.weeds = [Seaweed(h, w, x) for x in positions]
        # Кораллы
        n_corals = max(3, w // 25)
        coral_x = sorted(random.sample(range(1, w - 10), min(n_corals, w - 11)))
        self.corals = [Coral(h, w, x) for x in coral_x]
        # Пузырьки
        self.bubbles = []

    def _draw_background(self):
        h, w = self.height, self.width
        # Верхняя полоса — поверхность воды
        wave = ""
        for i in range(w):
            phase = time.time() * 1.2 + i * 0.3
            c = "~" if int(math.sin(phase) * 2) >= 0 else "≈"
            wave += c
        try:
            self.stdscr.addstr(0, 0, wave[:w - 1],
                               curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass
        # Дно с песком
        bottom_line = ""
        for i in range(w):
            bottom_line += random.choice(SAND_CHARS)
        try:
            self.stdscr.addstr(h - 2, 0, bottom_line[:w - 1],
                               curses.color_pair(6))
        except curses.error:
            pass
        # Подпись
        hint = " [Q] выход "
        try:
            self.stdscr.addstr(h - 1, max(0, w // 2 - len(hint) // 2), hint,
                               curses.color_pair(7) | curses.A_DIM)
        except curses.error:
            pass

    def run(self):
        while True:
            now = time.time()
            dt = now - self.last_time
            self.last_time = now

            key = self.stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break

            # Проверка изменения размера
            new_h, new_w = self.stdscr.getmaxyx()
            if new_h != self.height or new_w != self.width:
                self.height, self.width = new_h, new_w
                self._init_scene()

            # Спавн пузырьков
            self.bubble_spawn_timer += dt
            if self.bubble_spawn_timer > random.uniform(0.3, 0.8):
                self.bubble_spawn_timer = 0.0
                if len(self.bubbles) < 30:
                    self.bubbles.append(Bubble(self.height, self.width))

            # Обновление
            for f in self.fishes:
                f.update(dt)
            self.bubbles = [b for b in self.bubbles if not b.is_dead()]
            for b in self.bubbles:
                b.update(dt)
            for w in self.weeds:
                w.update(dt)

            # Отрисовка
            self.stdscr.erase()
            self._draw_background()
            for c in self.corals:
                c.draw(self.stdscr)
            for w in self.weeds:
                w.draw(self.stdscr)
            for f in self.fishes:
                f.draw(self.stdscr)
            for b in self.bubbles:
                b.draw(self.stdscr)

            self.stdscr.refresh()
            time.sleep(0.05)


def main():
    curses.wrapper(lambda s: AquariumApp(s).run())


if __name__ == "__main__":
    main()