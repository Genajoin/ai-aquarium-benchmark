"""
🐠 Terminal Aquarium Screensaver 🐠
Псевдографика: рыбки, пузырьки, водоросли, кораллы.
Выход: любая клавиша или Ctrl+C
"""

import curses
import random
import time
import signal
import sys

# ── Рыбки (направление вправо) ──────────────────────────────────────────────
FISH_RIGHT = [
    "><>",
    "><))'>",
    "><<°>",
    "><(((º>",
    "≈><ᵒ>",
    "><##'>",
    ">=>",
    "><))))*>",
    ">°)))彡",
    "⊂ᵒ͜ᵒ⊃",
]

FISH_LEFT = [
    "<><",
    "<'((<>",
    "<°>><",
    "<º)))><",
    "<ᵒ><≈",
    "<'##><",
    "<=<",
    "<*))))><",
    "彡((( °<",
    "⊂ᵒ͜ᵒ⊃",
]

BIG_FISH_RIGHT = [
    [" ______  ", "/      \\ ", "| °    |>", "\\______/ "],
    ["  _//_ ", " / °  \\>", " \\_‿_/ "],
    [" ,__,  ", "( °  )>", " `--'  "],
]

BIG_FISH_LEFT = [
    ["  ______  ", " /      \\ ", "<|    ° | ", " \\______/ "],
    ["  _\\\\_ ", "</ °  \\ ", " \\_‿_/ "],
    ["  ,__,  ", "<(  ° ) ", "  `--'  "],
]

# ── Цвета рыб ───────────────────────────────────────────────────────────────
FISH_COLORS = [
    curses.COLOR_YELLOW,
    curses.COLOR_RED,
    curses.COLOR_GREEN,
    curses.COLOR_CYAN,
    curses.COLOR_MAGENTA,
    curses.COLOR_WHITE,
]

# ── Кораллы ──────────────────────────────────────────────────────────────────
CORALS = [
    ["  (/)  ", " (/\\/) ", "(//\\\\/)"],
    [" \\|/ ", "\\\\|// ", "─┘└─"],
    [" Y ", "/|\\ ", "─┘└─"],
    ["  ¥  ", " /|\\ ", "/|||\\"],
    [" ♣ ", "/|\\ ", "─┤├─"],
    [" ∞ ", "╱|╲ ", "┘ └"],
]

# ── Декор дна ────────────────────────────────────────────────────────────────
FLOOR_CHARS = ["~", "≈", "_", ".", ",", "'", "`", "⌂"]

# ── Классы ───────────────────────────────────────────────────────────────────

class Bubble:
    def __init__(self, max_y, max_x):
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - random.randint(3, 8)
        self.char = random.choice(["°", "o", "O", "◦", "∘", "•"])
        self.speed = random.uniform(0.3, 1.0)
        self.drift = random.choice([-1, 0, 0, 1])
        self.tick = 0

    def update(self):
        self.tick += self.speed
        if self.tick >= 1.0:
            self.y -= 1
            if random.random() < 0.3:
                self.x += self.drift
            self.tick = 0

    def alive(self):
        return self.y > 0


class Seaweed:
    def __init__(self, x, max_y, height=None):
        self.x = x
        self.base_y = max_y - 2
        self.height = height or random.randint(4, 10)
        self.phase = random.random() * 6.28
        self.speed = random.uniform(0.02, 0.06)
        self.color_id = random.choice([10, 11])

    def draw(self, stdscr, tick):
        import math
        for i in range(self.height):
            y = self.base_y - i
            offset = int(math.sin(self.phase + tick * self.speed + i * 0.5) * 1.5)
            x = self.x + offset
            if 0 < y < self.base_y + 1 and 0 < x < curses.COLS - 1:
                ch = random.choice(["}", "{", "|", ")", "(", "¦"]) if random.random() < 0.1 else (")" if offset > 0 else "(")
                try:
                    stdscr.addstr(y, x, ch, curses.color_pair(self.color_id))
                except curses.error:
                    pass


class Fish:
    def __init__(self, max_y, max_x, big=False):
        self.big = big
        self.direction = random.choice([-1, 1])
        self.color_pair = random.randint(1, 6)
        self.speed = random.uniform(0.2, 0.7) if not big else random.uniform(0.1, 0.4)
        self.tick = 0

        if big:
            idx = random.randint(0, len(BIG_FISH_RIGHT) - 1)
            self.sprite_r = BIG_FISH_RIGHT[idx]
            self.sprite_l = BIG_FISH_LEFT[idx]
            sprite = self.sprite_r
            self.width = max(len(s) for s in sprite)
            self.height = len(sprite)
        else:
            idx = random.randint(0, len(FISH_RIGHT) - 1)
            self.sprite_r = FISH_RIGHT[idx]
            self.sprite_l = FISH_LEFT[idx]
            self.width = max(len(self.sprite_r), len(self.sprite_l))
            self.height = 1

        self.y = random.randint(2, max(3, max_y - 6 - self.height))
        if self.direction == 1:
            self.x = -self.width
        else:
            self.x = max_x

        self.max_x = max_x
        self.max_y = max_y
        self.wobble = random.uniform(0.01, 0.04)
        self.wobble_phase = random.random() * 6.28

    def update(self, tick):
        import math
        self.tick += self.speed
        if self.tick >= 1.0:
            self.x += self.direction
            self.tick = 0
        # вертикальное покачивание
        self.y_offset = int(math.sin(self.wobble_phase + tick * self.wobble) * 1)

    def alive(self):
        if self.direction == 1:
            return self.x < self.max_x + 5
        else:
            return self.x > -self.width - 5

    def draw(self, stdscr):
        sprite = self.sprite_r if self.direction == 1 else self.sprite_l
        if self.big:
            for i, line in enumerate(sprite):
                py = self.y + i + self.y_offset
                px = self.x
                if 0 < py < self.max_y - 2:
                    for j, ch in enumerate(line):
                        cx = px + j
                        if 0 < cx < self.max_x - 1 and ch != ' ':
                            try:
                                stdscr.addstr(py, cx, ch, curses.color_pair(self.color_pair) | curses.A_BOLD)
                            except curses.error:
                                pass
        else:
            py = self.y + self.y_offset
            if 0 < py < self.max_y - 2:
                for j, ch in enumerate(sprite):
                    cx = self.x + j
                    if 0 < cx < self.max_x - 1:
                        try:
                            stdscr.addstr(py, cx, ch, curses.color_pair(self.color_pair) | curses.A_BOLD)
                        except curses.error:
                            pass


class Coral:
    def __init__(self, x, max_y, max_x):
        idx = random.randint(0, len(CORALS) - 1)
        self.sprite = CORALS[idx]
        self.x = x
        self.max_y = max_y
        self.color_pair = random.choice([3, 4, 5, 6])
        self.width = max(len(s) for s in self.sprite)
        # убедимся что коралл помещается
        if self.x + self.width >= max_x:
            self.x = max_x - self.width - 1

    def draw(self, stdscr):
        base = self.max_y - 2
        for i, line in enumerate(reversed(self.sprite)):
            y = base - i
            for j, ch in enumerate(line):
                cx = self.x + j
                if ch != ' ' and 0 < y and 0 < cx < curses.COLS - 1:
                    try:
                        stdscr.addstr(y, cx, ch, curses.color_pair(self.color_pair))
                    except curses.error:
                        pass


# ── Основная функция ─────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    # Инициализация цветов
    curses.start_color()
    curses.use_default_colors()

    for i, c in enumerate(FISH_COLORS, 1):
        curses.init_pair(i, c, -1)

    curses.init_pair(7, curses.COLOR_CYAN, -1)     # пузырьки
    curses.init_pair(8, curses.COLOR_BLUE, -1)      # вода
    curses.init_pair(9, curses.COLOR_YELLOW, -1)    # песок
    curses.init_pair(10, curses.COLOR_GREEN, -1)    # водоросли
    curses.init_pair(11, 2, -1)                     # водоросли темнее
    curses.init_pair(12, curses.COLOR_BLUE, curses.COLOR_BLUE)  # верх воды

    max_y, max_x = stdscr.getmaxyx()
    if max_y < 15 or max_x < 40:
        stdscr.addstr(0, 0, "Terminal too small! Need at least 40x15")
        stdscr.getch()
        return

    # Создание водорослей
    seaweeds = []
    for _ in range(random.randint(5, 10)):
        x = random.randint(1, max_x - 3)
        seaweeds.append(Seaweed(x, max_y))

    # Создание кораллов
    corals = []
    num_corals = random.randint(3, 7)
    coral_positions = sorted(random.sample(range(2, max_x - 10), min(num_corals, (max_x - 12) // 8)))
    for pos in coral_positions:
        corals.append(Coral(pos, max_y, max_x))

    # Генерация дна
    floor = []
    for x in range(max_x):
        floor.append(random.choice(FLOOR_CHARS))

    fishes = []
    bubbles = []
    tick = 0

    while True:
        # Проверка нажатия клавиши
        key = stdscr.getch()
        if key != -1:
            break

        max_y, max_x = stdscr.getmaxyx()
        stdscr.erase()

        # ── Рисуем поверхность воды ──
        water_surface = ""
        import math
        for x in range(max_x - 1):
            phase = math.sin(tick * 0.05 + x * 0.3)
            if phase > 0.3:
                water_surface += "~"
            elif phase > -0.3:
                water_surface += "≈"
            else:
                water_surface += "~"
        try:
            stdscr.addstr(0, 0, water_surface, curses.color_pair(8) | curses.A_BOLD)
        except curses.error:
            pass

        # ── Рисуем дно ──
        for x in range(min(len(floor), max_x - 1)):
            try:
                stdscr.addstr(max_y - 1, x, floor[x], curses.color_pair(9))
            except curses.error:
                pass

        # Периодически шевелим дно
        if tick % 60 == 0:
            for i in range(len(floor)):
                if random.random() < 0.05:
                    floor[i] = random.choice(FLOOR_CHARS)

        # ── Кораллы ──
        for coral in corals:
            coral.draw(stdscr)

        # ── Водоросли ──
        for sw in seaweeds:
            sw.draw(stdscr, tick)

        # ── Рыбки ──
        # Спавн новых рыб
        if random.random() < 0.02 and len(fishes) < 15:
            fishes.append(Fish(max_y, max_x, big=False))
        if random.random() < 0.005 and len(fishes) < 15:
            fishes.append(Fish(max_y, max_x, big=True))

        for fish in fishes:
            fish.update(tick)
            fish.draw(stdscr)
            # пузырьки от рыб
            if random.random() < 0.02:
                bx = fish.x + (fish.width if fish.direction == 1 else 0)
                if 0 < bx < max_x:
                    b = Bubble(max_y, max_x)
                    b.x = bx
                    b.y = fish.y - 1
                    bubbles.append(b)

        fishes = [f for f in fishes if f.alive()]

        # ── Пузырьки ──
        if random.random() < 0.08:
            bubbles.append(Bubble(max_y, max_x))

        for bubble in bubbles:
            bubble.update()
            if 0 < bubble.y < max_y - 1 and 0 < bubble.x < max_x - 1:
                try:
                    stdscr.addstr(bubble.y, bubble.x, bubble.char, curses.color_pair(7))
                except curses.error:
                    pass

        bubbles = [b for b in bubbles if b.alive()]

        # ── Заголовок ──
        title = " 🐠 Aquarium Screensaver • Press any key to exit "
        if max_x > len(title) + 4:
            tx = (max_x - len(title)) // 2
            try:
                stdscr.addstr(1, tx, title, curses.color_pair(8) | curses.A_DIM)
            except curses.error:
                pass

        stdscr.refresh()
        tick += 1
        time.sleep(0.05)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🐠 Thanks for watching the aquarium! 🐠")