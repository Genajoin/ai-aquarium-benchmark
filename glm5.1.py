"""
╔══════════════════════════════════════╗
║   AI Aquarium — Terminal Screensaver ║
║   glm-5.1 edition                    ║
╚══════════════════════════════════════╝
Выход: любая клавиша или Ctrl+C
"""

import curses
import random
import math
import time

# ── Спрайты рыбок ────────────────────────────────────────────────────────────

FISH_RIGHT = [
    "><>",
    "><))'>",
    "><(((°>",
    ">)°>",
    "><~>",
    ">(",
    ">¬>",
    "><=>",
]

FISH_LEFT = [
    "<><",
    "<'((><",
    "<°)))><",
    "<°(<",
    "<~<",
    ")<",
    "<¬<",
    "<=><",
]

BIG_FISH_RIGHT = [
    ["  _      _  ",
     " / \\    / \\>",
     "|  °   °  | ",
     " \\   ‿   /  ",
     "  `.___,'   "],
    ["   /\\   ",
     " /  ° \\>",
     " \\_‿_/ "],
    ["  ╭─────╮ ",
     "  │ °   │>",
     "  │  ‿  │ ",
     "  ╰─────╯ "],
]

BIG_FISH_LEFT = [
    ["  _      _  ",
     "</ \\    / \\ ",
     " |  °   °  | ",
     "  \\   ‿   /  ",
     "   `.___,'   "],
    ["   /\\   ",
     "</  ° \\ ",
     " \\_‿_/ "],
    [" ╭─────╮  ",
     "<│   ° │  ",
     " │  ‿  │  ",
     " ╰─────╯  "],
]

# ── Кораллы ──────────────────────────────────────────────────────────────────

CORALS = [
    ["   ( )   ",
     "  (/)\\)  ",
     " (//\\\\/) ",
     "(/    \\) "],
    ["   ¥   ",
     "  /|\\  ",
     " /|||\\ ",
     "/||||\\"],
    ["  ╱╲  ",
     " ╱  ╲ ",
     "╱ ✦ ✦ ╲",
     "──┘└──"],
    ["  ♣  ",
     " ╔╩╗ ",
     "╔╩╔╩╗",
     "╚═══╝"],
    [" )()( ",
     ")(  )(",
     " ┘  └ "],
    ["  ░▒▓  ",
     " ░▓▒▓░ ",
     "▓▒░▒▓▒▓",
     "──┘└──"],
]

# ── Песчаное дно ─────────────────────────────────────────────────────────────

FLOOR_CHARS = ["·", ".", ",", "`", "'", "~", "°", "_"]

# ── Водоросли ────────────────────────────────────────────────────────────────

SEAWEED_CHARS = ["}", "{", ")", "(", "¦", "§", "µ"]


# ── Классы ───────────────────────────────────────────────────────────────────

class Bubble:
    def __init__(self, max_y, max_x, start_x=None, start_y=None):
        self.max_x = max_x
        self.max_y = max_y
        self.x = start_x if start_x is not None else random.randint(1, max(2, max_x - 2))
        self.y = start_y if start_y is not None else random.randint(max_y - 5, max_y - 3)
        self.char = random.choice(["°", "o", "O", "∘", "◦", "·"])
        self.size = random.uniform(0.3, 1.2)
        self.tick = random.random()
        self.phase = random.uniform(0, math.tau)
        self.wobble_amp = random.uniform(0.5, 2.0)
        self.wobble_freq = random.uniform(0.04, 0.12)
        self.base_x = self.x

    def update(self):
        self.tick += self.size
        self.phase += self.wobble_freq
        if self.tick >= 1.0:
            self.y -= 1
            self.x = self.base_x + math.sin(self.phase) * self.wobble_amp
            self.x = max(1, min(self.max_x - 2, self.x))
            self.tick -= 1.0
            # пузырёк уменьшается ближе к поверхности
            if self.y < 4 and self.char == "O":
                self.char = "o"
            elif self.y < 2 and self.char == "o":
                self.char = "°"

    def alive(self):
        return self.y > 0

    def draw(self, stdscr, pair):
        ix, iy = int(self.x), int(self.y)
        if 0 < iy < self.max_y - 1 and 0 < ix < self.max_x - 1:
            try:
                stdscr.addstr(iy, ix, self.char, curses.color_pair(pair))
            except curses.error:
                pass


class Seaweed:
    def __init__(self, x, max_y):
        self.x = x
        self.base_y = max_y - 2
        self.height = random.randint(4, min(12, max_y - 5))
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.015, 0.045)
        self.color = random.choice([10, 11, 12])
        self.chars = [random.choice(SEAWEED_CHARS) for _ in range(self.height)]

    def update(self):
        self.phase += self.speed

    def draw(self, stdscr, max_x):
        for i in range(self.height):
            y = self.base_y - i
            if y < 1:
                break
            offset = math.sin(self.phase + i * 0.6) * (1.0 + i * 0.15)
            x = int(self.x + offset)
            if 0 < x < max_x - 1:
                try:
                    stdscr.addstr(y, x, self.chars[i % len(self.chars)],
                                  curses.color_pair(self.color))
                except curses.error:
                    pass


class Fish:
    def __init__(self, max_y, max_x, big=False):
        self.big = big
        self.max_x = max_x
        self.max_y = max_y
        self.direction = random.choice([-1, 1])
        self.color = random.randint(1, 6)
        self.speed = random.uniform(0.15, 0.6) if not big else random.uniform(0.08, 0.3)
        self.tick = random.random()
        self.wobble_phase = random.uniform(0, math.tau)
        self.wobble_speed = random.uniform(0.02, 0.06)
        self.y_offset = 0

        if big:
            idx = random.randint(0, len(BIG_FISH_RIGHT) - 1)
            self.sprite_r = BIG_FISH_RIGHT[idx]
            self.sprite_l = BIG_FISH_LEFT[idx]
            self.w = max(len(line) for line in self.sprite_r)
            self.h = len(self.sprite_r)
        else:
            idx = random.randint(0, len(FISH_RIGHT) - 1)
            self.sprite_r = FISH_RIGHT[idx]
            self.sprite_l = FISH_LEFT[idx]
            self.w = max(len(self.sprite_r), len(self.sprite_l))
            self.h = 1

        self.y = random.randint(3, max(4, max_y - 7 - self.h))
        if self.direction == 1:
            self.x = -self.w - random.randint(0, 10)
        else:
            self.x = max_x + random.randint(0, 10)

    def update(self):
        self.tick += self.speed
        self.wobble_phase += self.wobble_speed
        self.y_offset = int(math.sin(self.wobble_phase) * 1.5)
        if self.tick >= 1.0:
            self.x += self.direction
            self.tick -= 1.0

    def alive(self):
        if self.direction == 1:
            return self.x < self.max_x + self.w + 5
        return self.x > -self.w - 5

    def draw(self, stdscr):
        sprite = self.sprite_r if self.direction == 1 else self.sprite_l
        attr = curses.color_pair(self.color) | curses.A_BOLD

        if self.big:
            for i, line in enumerate(sprite):
                py = int(self.y) + i + self.y_offset
                if py < 1 or py >= self.max_y - 2:
                    continue
                for j, ch in enumerate(line):
                    if ch == ' ':
                        continue
                    px = int(self.x) + j
                    if 0 < px < self.max_x - 1:
                        try:
                            stdscr.addstr(py, px, ch, attr)
                        except curses.error:
                            pass
        else:
            py = int(self.y) + self.y_offset
            if 1 <= py < self.max_y - 2:
                for j, ch in enumerate(sprite):
                    px = int(self.x) + j
                    if 0 < px < self.max_x - 1:
                        try:
                            stdscr.addstr(py, px, ch, attr)
                        except curses.error:
                            pass


class Coral:
    def __init__(self, x, max_y, max_x):
        self.sprite = random.choice(CORALS)
        self.x = x
        self.max_y = max_y
        self.max_x = max_x
        self.w = max(len(line) for line in self.sprite)
        self.color = random.choice([3, 4, 5, 6, 13, 14])
        if self.x + self.w >= max_x:
            self.x = max(1, max_x - self.w - 1)
        self.phase = random.uniform(0, math.tau)

    def draw(self, stdscr, tick):
        base = self.max_y - 2
        for i, line in enumerate(reversed(self.sprite)):
            y = base - i
            if y < 1:
                break
            # лёгкое покачивание кораллов
            shimmer = math.sin(self.phase + tick * 0.02) * 0.3
            for j, ch in enumerate(line):
                if ch == ' ':
                    continue
                px = self.x + j
                if 0 < px < self.max_x - 1:
                    try:
                        bright = curses.A_BOLD if (tick + i + j) % 40 < 3 else curses.A_NORMAL
                        stdscr.addstr(y, px, ch,
                                      curses.color_pair(self.color) | bright)
                    except curses.error:
                        pass


# ── Световые лучи ────────────────────────────────────────────────────────────

class LightRay:
    def __init__(self, max_y, max_x):
        self.x = random.randint(2, max(3, max_x - 3))
        self.max_y = max_y
        self.max_x = max_x
        self.length = random.randint(5, max_y // 2)
        self.width = random.randint(1, 3)
        self.drift = random.uniform(-0.15, 0.15)
        self.alpha_base = random.uniform(0.3, 0.7)
        self.phase = random.uniform(0, math.tau)

    def update(self):
        self.phase += 0.015
        self.x += self.drift
        if self.x < 1 or self.x >= self.max_x - 1:
            self.drift = -self.drift

    def draw(self, stdscr):
        alpha = self.alpha_base + math.sin(self.phase) * 0.2
        if alpha < 0.15:
            return
        for i in range(self.length):
            y = 1 + i
            if y >= self.max_y - 2:
                break
            # луч расходится книзу
            spread = int(i * 0.3)
            for dx in range(-spread, spread + 1):
                x = int(self.x) + dx
                if 0 < x < self.max_x - 1:
                    try:
                        ch = "░" if (i + dx) % 3 == 0 else "·"
                        stdscr.addstr(y, x, ch, curses.color_pair(15) | curses.A_DIM)
                    except curses.error:
                        pass


# ── Основная программа ───────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    curses.start_color()
    curses.use_default_colors()

    # Цветовые пары: 1–6 — рыбки
    fish_colors = [
        curses.COLOR_YELLOW, curses.COLOR_RED, curses.COLOR_GREEN,
        curses.COLOR_CYAN, curses.COLOR_MAGENTA, curses.COLOR_WHITE,
    ]
    for i, c in enumerate(fish_colors, 1):
        curses.init_pair(i, c, -1)
    # 7 — пузырьки, 8 — вода, 9 — песок
    curses.init_pair(7, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_BLUE, -1)
    curses.init_pair(9, curses.COLOR_YELLOW, -1)
    # 10–12 — водоросли (оттенки зелёного)
    curses.init_pair(10, curses.COLOR_GREEN, -1)
    curses.init_pair(11, 34, -1)    # тёмно-зелёный
    curses.init_pair(12, 82, -1)    # ярко-зелёный
    # 13–14 — кораллы
    curses.init_pair(13, curses.COLOR_MAGENTA, -1)
    curses.init_pair(14, curses.COLOR_RED, -1)
    # 15 — свет
    curses.init_pair(15, curses.COLOR_WHITE, -1)

    max_y, max_x = stdscr.getmaxyx()
    if max_y < 15 or max_x < 40:
        stdscr.addstr(0, 0, "Терминал слишком маленький! Нужно хотя бы 40x15")
        stdscr.getch()
        return

    # ── Инициализация сцены ──────────────────────────────────────────────────

    seaweeds = [Seaweed(random.randint(1, max_x - 3), max_y)
                for _ in range(random.randint(6, max(7, max_x // 15)))]

    coral_positions = sorted(random.sample(
        range(3, max(4, max_x - 12)),
        min(random.randint(3, 6), max(1, (max_x - 15) // 10))
    ))
    corals = [Coral(x, max_y, max_x) for x in coral_positions]

    light_rays = [LightRay(max_y, max_x) for _ in range(random.randint(2, 5))]

    floor = [random.choice(FLOOR_CHARS) for _ in range(max_x)]

    fishes = []
    bubbles = []
    tick = 0

    # ── Главный цикл ─────────────────────────────────────────────────────────

    while True:
        ch = stdscr.getch()
        if ch != -1:
            break

        max_y, max_x = stdscr.getmaxyx()
        stdscr.erase()

        # ── Поверхность воды ─────────────────────────────────────────────────
        wave = ""
        for x in range(max_x - 1):
            v = math.sin(tick * 0.04 + x * 0.25)
            if v > 0.4:
                wave += "~"
            elif v > 0:
                wave += "≈"
            elif v > -0.4:
                wave += "∿"
            else:
                wave += "〜"
        try:
            stdscr.addstr(0, 0, wave, curses.color_pair(8) | curses.A_BOLD)
        except curses.error:
            pass

        # ── Световые лучи ────────────────────────────────────────────────────
        for ray in light_rays:
            ray.update()
            ray.draw(stdscr)

        # ── Дно ──────────────────────────────────────────────────────────────
        for x in range(min(len(floor), max_x - 1)):
            # шевелим песчинки иногда
            if tick % 80 == 0 and random.random() < 0.04:
                floor[x] = random.choice(FLOOR_CHARS)
            try:
                stdscr.addstr(max_y - 1, x, floor[x], curses.color_pair(9))
            except curses.error:
                pass

        # ── Кораллы ──────────────────────────────────────────────────────────
        for coral in corals:
            coral.draw(stdscr, tick)

        # ── Водоросли ────────────────────────────────────────────────────────
        for sw in seaweeds:
            sw.update()
            sw.draw(stdscr, max_x)

        # ── Спавн рыб ────────────────────────────────────────────────────────
        if random.random() < 0.025 and len(fishes) < 14:
            fishes.append(Fish(max_y, max_x, big=False))
        if random.random() < 0.006 and len(fishes) < 14:
            fishes.append(Fish(max_y, max_x, big=True))

        # ── Обновление и отрисовка рыб ───────────────────────────────────────
        for fish in fishes:
            fish.update()
            fish.draw(stdscr)
            # рыбы иногда выпускают пузырьки
            if random.random() < 0.015:
                bx = int(fish.x) + (fish.w if fish.direction == 1 else 0)
                by = int(fish.y) + fish.y_offset
                if 1 < bx < max_x - 2 and 1 < by < max_y - 2:
                    bubbles.append(Bubble(max_y, max_x, start_x=bx, start_y=by))
        fishes = [f for f in fishes if f.alive()]

        # ── Спавн пузырьков от дна ───────────────────────────────────────────
        if random.random() < 0.1 and len(bubbles) < 40:
            bubbles.append(Bubble(max_y, max_x))

        # ── Пузырьки ─────────────────────────────────────────────────────────
        for b in bubbles:
            b.update()
            b.draw(stdscr, 7)
        bubbles = [b for b in bubbles if b.alive()]

        # ── Подпись ──────────────────────────────────────────────────────────
        hint = " ✦ AI Aquarium — glm-5.1 — любая клавиша = выход ✦ "
        if max_x > len(hint) + 4:
            tx = (max_x - len(hint)) // 2
            try:
                stdscr.addstr(max_y - 2, tx, hint,
                              curses.color_pair(8) | curses.A_DIM)
            except curses.error:
                pass

        stdscr.refresh()
        tick += 1
        time.sleep(0.045)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n✦ Aquarium by glm-5.1 — спасибо за просмотр! ✦\n")
