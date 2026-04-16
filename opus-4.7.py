#!/usr/bin/env python3
import curses
import random
import math
import time


FISH_RIGHT = [
    "><>",
    "><(((*>",
    "><((°>",
    "><{{{*>",
]
FISH_LEFT = [
    "<><",
    "<*)))><",
    "<°))><",
    "<*}}}><",
]

BIG_FISH_RIGHT = [
    [
        "   ___",
        "  /o  \\___",
        " <      _>",
        "  \\___/   ",
    ],
    [
        "    _____",
        "  <'_  o \\__",
        "    \\_____/>",
    ],
]
BIG_FISH_LEFT = [
    [
        "    ___   ",
        " ___/  o\\ ",
        " <_      >",
        "    \\___/ ",
    ],
    [
        "   _____    ",
        " __/ o  _'> ",
        " <\\_____/   ",
    ],
]

CORALS = [
    [
        "  \\|/  ",
        " --*-- ",
        "  /|\\  ",
    ],
    [
        "  __   ",
        " (  )  ",
        "  \\/   ",
    ],
    [
        "  /\\  ",
        " /__\\ ",
        " \\  / ",
    ],
]


class Bubble:
    def __init__(self, w, h):
        self.x = random.randint(1, max(1, w - 2))
        self.y = h - 2
        self.char = random.choice("°oO∘")
        self.speed = random.uniform(0.25, 0.7)
        self.offset = 0.0
        self.phase = random.uniform(0, math.tau)

    def update(self):
        self.offset += self.speed
        self.phase += 0.2

    def pos(self):
        x = int(self.x + math.sin(self.phase) * 1.2)
        y = int(self.y - self.offset)
        return x, y


class Fish:
    def __init__(self, w, h, big=False):
        self.big = big
        self.dir = random.choice((-1, 1))
        if big:
            sprites = BIG_FISH_RIGHT if self.dir == 1 else BIG_FISH_LEFT
            self.sprite = random.choice(sprites)
        else:
            self.sprite = random.choice(FISH_RIGHT if self.dir == 1 else FISH_LEFT)
        self.color = random.randint(1, 5)
        self.y = random.randint(2, max(3, h - 6))
        self.x = random.randint(0, w) if self.dir == 1 else random.randint(0, w)
        self.speed = random.uniform(0.2, 0.6) if big else random.uniform(0.3, 1.0)
        self.fx = float(self.x)
        self.bob_phase = random.uniform(0, math.tau)

    def width(self):
        if self.big:
            return max(len(line) for line in self.sprite)
        return len(self.sprite)

    def update(self, w, h):
        self.fx += self.speed * self.dir
        self.bob_phase += 0.15
        if self.dir == 1 and self.fx > w + 2:
            self.fx = -self.width() - 2
            self.y = random.randint(2, max(3, h - 6))
        elif self.dir == -1 and self.fx < -self.width() - 2:
            self.fx = w + 2
            self.y = random.randint(2, max(3, h - 6))


def draw_water_surface(stdscr, w, t):
    for x in range(w):
        ch = "~" if math.sin(x * 0.3 + t * 2) > 0 else "-"
        try:
            stdscr.addstr(0, x, ch, curses.color_pair(6))
        except curses.error:
            pass


def draw_floor(stdscr, w, h, t):
    for x in range(w):
        ch = random.choice(",.'`") if (x + int(t * 5)) % 7 == 0 else random.choice(".,_")
        try:
            stdscr.addstr(h - 1, x, ch, curses.color_pair(7))
        except curses.error:
            pass


def draw_seaweed(stdscr, positions, h, t):
    for i, x in enumerate(positions):
        height = 4 + (i % 4)
        for j in range(height):
            y = h - 2 - j
            sway = int(math.sin(t * 1.5 + i * 0.7 + j * 0.4) * 1.5)
            ch = "(" if sway < 0 else ")" if sway > 0 else "|"
            try:
                stdscr.addstr(y, max(0, x + sway), ch, curses.color_pair(8))
            except curses.error:
                pass


def draw_corals(stdscr, corals, h):
    for x, sprite, color in corals:
        for i, line in enumerate(sprite):
            y = h - 1 - len(sprite) + i
            try:
                stdscr.addstr(y, x, line, curses.color_pair(color))
            except curses.error:
                pass


def draw_fish(stdscr, fish):
    x = int(fish.fx)
    y_bob = int(math.sin(fish.bob_phase) * 0.6)
    if fish.big:
        for i, line in enumerate(fish.sprite):
            try:
                stdscr.addstr(fish.y + i + y_bob, x, line, curses.color_pair(fish.color) | curses.A_BOLD)
            except curses.error:
                pass
    else:
        try:
            stdscr.addstr(fish.y + y_bob, x, fish.sprite, curses.color_pair(fish.color) | curses.A_BOLD)
        except curses.error:
            pass


def draw_bubble(stdscr, bubble):
    x, y = bubble.pos()
    try:
        stdscr.addstr(y, x, bubble.char, curses.color_pair(9))
    except curses.error:
        pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_YELLOW, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)
    curses.init_pair(8, curses.COLOR_GREEN, -1)
    curses.init_pair(9, curses.COLOR_CYAN, -1)
    curses.init_pair(10, curses.COLOR_RED, -1)

    h, w = stdscr.getmaxyx()

    fish = [Fish(w, h, big=(i % 5 == 0)) for i in range(max(6, w // 14))]
    bubbles = []
    seaweed_positions = sorted(random.sample(range(2, max(3, w - 2)), min(w // 6, max(2, w - 4))))
    corals = []
    used = set()
    for _ in range(max(3, w // 20)):
        x = random.randint(2, max(3, w - 10))
        if any(abs(x - u) < 8 for u in used):
            continue
        used.add(x)
        sprite = random.choice(CORALS)
        color = random.choice([2, 3, 10, 1])
        corals.append((x, sprite, color))

    t = 0.0
    start = time.time()
    while True:
        try:
            key = stdscr.getch()
            if key != -1:
                break
        except Exception:
            pass

        nh, nw = stdscr.getmaxyx()
        if (nh, nw) != (h, w):
            h, w = nh, nw
            fish = [Fish(w, h, big=(i % 5 == 0)) for i in range(max(6, w // 14))]
            bubbles = []
            seaweed_positions = sorted(random.sample(range(2, max(3, w - 2)), min(w // 6, max(2, w - 4))))
            corals = []
            used = set()
            for _ in range(max(3, w // 20)):
                x = random.randint(2, max(3, w - 10))
                if any(abs(x - u) < 8 for u in used):
                    continue
                used.add(x)
                sprite = random.choice(CORALS)
                color = random.choice([2, 3, 10, 1])
                corals.append((x, sprite, color))

        stdscr.erase()
        t = time.time() - start

        draw_water_surface(stdscr, w, t)
        draw_corals(stdscr, corals, h)
        draw_seaweed(stdscr, seaweed_positions, h, t)

        for f in fish:
            f.update(w, h)
            draw_fish(stdscr, f)

        if random.random() < 0.3:
            bubbles.append(Bubble(w, h))
        for b in bubbles:
            b.update()
            draw_bubble(stdscr, b)
        bubbles = [b for b in bubbles if b.pos()[1] > 1]

        draw_floor(stdscr, w, h, t)

        stdscr.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
