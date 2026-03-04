#!/usr/bin/env python3
"""
Terminal Aquarium Screensaver (ASCII)
- Fish swim with simple animation frames
- Bubbles rise and wobble
- Seaweed sways
- Corals sit on the bottom
Controls:
  q  quit
  p  pause/resume
  +/-  speed up / slow down
"""

import curses
import random
import time
import math
from dataclasses import dataclass

# ---------- Helpers ----------

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def safe_add(stdscr, y, x, s, attr=0):
    """Draw string clipped to screen, ignoring curses errors."""
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h:
        return
    if x >= w or x + len(s) <= 0:
        return
    # clip left
    if x < 0:
        s = s[-x:]
        x = 0
    # clip right
    if x + len(s) > w:
        s = s[: w - x]
    if not s:
        return
    try:
        stdscr.addstr(y, x, s, attr)
    except curses.error:
        pass

# ---------- Entities ----------

FISH_FRAMES_RIGHT = [
    r"><(((('>",
    r"><((((('>",
]
FISH_FRAMES_LEFT = [
    r"<')))))><",
    r"<'))))><",
]

TINY_FISH_RIGHT = [
    r"><>",
    r"><>",
]
TINY_FISH_LEFT = [
    r"<> <",
    r"<> <",
]

BUBBLE_CHARS = ["o", "O", ".", "°"]

SEAWEED_STEMS = ["|", "!", ":", ";"]
SEAWEED_TIPS = ["~", "^", "v", "w"]

CORAL_SHAPES = [
    ["  _/\\_  ",
     " /____\\ ",
     "   ||   "],
    ["  _.._  ",
     " (____) ",
     "  /||\\  "],
    ["  _/\\_  ",
     " _\\__/  ",
     "  /||\\  "],
    ["  __    ",
     " /__\\_  ",
     "   ||   "],
]

@dataclass
class Fish:
    x: float
    y: float
    vx: float
    kind: str          # "big" or "tiny"
    phase: float       # animation phase
    bob_phase: float   # vertical bob
    color: int

    def frames(self):
        right = self.vx > 0
        if self.kind == "big":
            return FISH_FRAMES_RIGHT if right else FISH_FRAMES_LEFT
        return TINY_FISH_RIGHT if right else TINY_FISH_LEFT

    def width(self):
        return max(len(f) for f in self.frames())

@dataclass
class Bubble:
    x: float
    y: float
    vy: float
    wobble: float
    ch: str
    color: int

@dataclass
class Seaweed:
    base_x: int
    height: int
    phase: float
    color: int

@dataclass
class Coral:
    x: int
    shape: list
    color: int

# ---------- Aquarium ----------

class Aquarium:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.rng = random.Random()
        self.fish = []
        self.bubbles = []
        self.seaweed = []
        self.corals = []
        self.paused = False
        self.dt = 0.06  # base frame time
        self.t = 0.0

        self._init_curses()
        self._reset_world()

    def _init_curses(self):
        curses.curs_set(0)
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)

        if curses.has_colors():
            curses.start_color()
            try:
                curses.use_default_colors()
            except curses.error:
                pass

            # A small palette (foreground, background=-1 if supported)
            # IDs: 1..7
            curses.init_pair(1, curses.COLOR_CYAN, -1)     # water accents / bubbles
            curses.init_pair(2, curses.COLOR_YELLOW, -1)   # fish highlight
            curses.init_pair(3, curses.COLOR_GREEN, -1)    # seaweed
            curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # coral
            curses.init_pair(5, curses.COLOR_BLUE, -1)     # deep water text
            curses.init_pair(6, curses.COLOR_WHITE, -1)    # foam
            curses.init_pair(7, curses.COLOR_RED, -1)      # coral alt

    def _reset_world(self):
        h, w = self.stdscr.getmaxyx()
        self.fish.clear()
        self.bubbles.clear()
        self.seaweed.clear()
        self.corals.clear()

        # Create corals along the bottom
        bottom = h - 2
        if bottom < 5:
            return

        x = 2
        while x < w - 10:
            if self.rng.random() < 0.35:
                shape = self.rng.choice(CORAL_SHAPES)
                color = self.rng.choice([4, 7, 4, 4])
                self.corals.append(Coral(x=x, shape=shape, color=color))
                x += len(shape[0]) + self.rng.randint(2, 6)
            else:
                x += self.rng.randint(3, 9)

        # Seaweed
        for _ in range(max(2, w // 14)):
            base_x = self.rng.randint(2, max(2, w - 3))
            height = self.rng.randint(4, max(5, h // 2))
            phase = self.rng.random() * math.tau
            self.seaweed.append(Seaweed(base_x=base_x, height=height, phase=phase, color=3))

        # Fish
        for _ in range(max(4, w // 18)):
            self._spawn_fish()

        # Initial bubbles
        for _ in range(max(10, w // 3)):
            self._spawn_bubble(initial=True)

    def _spawn_fish(self):
        h, w = self.stdscr.getmaxyx()
        bottom = h - 3
        if bottom <= 2 or w <= 10:
            return
        kind = "big" if self.rng.random() < 0.55 else "tiny"
        vx = self.rng.choice([-1, 1]) * self.rng.uniform(6.0, 14.0)  # chars/sec
        y = self.rng.uniform(2, bottom - 2)
        x = -10 if vx > 0 else (w + 10)
        phase = self.rng.random() * 2
        bob_phase = self.rng.random() * math.tau
        color = self.rng.choice([2, 6, 2, 2, 1])
        self.fish.append(Fish(x=x, y=y, vx=vx, kind=kind, phase=phase, bob_phase=bob_phase, color=color))

    def _spawn_bubble(self, initial=False):
        h, w = self.stdscr.getmaxyx()
        if w <= 2 or h <= 2:
            return
        x = self.rng.uniform(1, w - 2)
        if initial:
            y = self.rng.uniform(1, h - 2)
        else:
            y = h - 2
        vy = self.rng.uniform(5.0, 16.0)  # chars/sec upward
        wobble = self.rng.uniform(1.5, 4.0)
        ch = self.rng.choice(BUBBLE_CHARS)
        color = self.rng.choice([1, 6, 1])
        self.bubbles.append(Bubble(x=x, y=y, vy=vy, wobble=wobble, ch=ch, color=color))

    def _handle_input(self):
        try:
            key = self.stdscr.getch()
        except curses.error:
            return True

        if key == -1:
            return True

        if key in (ord('q'), ord('Q')):
            return False
        if key in (ord('p'), ord('P')):
            self.paused = not self.paused
        if key in (ord('+'), ord('=')):
            self.dt = max(0.02, self.dt * 0.85)
        if key in (ord('-'), ord('_')):
            self.dt = min(0.20, self.dt / 0.85)
        if key == curses.KEY_RESIZE:
            self._reset_world()
        return True

    def _update(self, dt):
        h, w = self.stdscr.getmaxyx()
        bottom = h - 2

        # Fish movement
        for f in self.fish:
            f.x += f.vx * dt
            f.phase += dt * 6.0
            f.bob_phase += dt * 1.2

            # keep y in bounds with gentle drift
            f.y += math.sin(f.bob_phase) * dt * 2.0
            f.y = clamp(f.y, 1.5, bottom - 4)

        # Remove fish out of bounds & respawn
        kept = []
        for f in self.fish:
            fw = f.width()
            if f.vx > 0 and f.x > w + fw + 2:
                continue
            if f.vx < 0 and f.x < -fw - 2:
                continue
            kept.append(f)
        self.fish = kept
        while len(self.fish) < max(4, w // 18):
            self._spawn_fish()

        # Bubbles rise
        for b in self.bubbles:
            b.y -= b.vy * dt
            b.x += math.sin((self.t + b.y) / b.wobble) * dt * 2.0
            b.x = clamp(b.x, 1, w - 2)

        self.bubbles = [b for b in self.bubbles if b.y > 0]
        # Spawn bubbles occasionally
        spawn_rate = max(0.8, w / 18.0)  # bubbles/sec
        # Poisson-ish
        if self.rng.random() < spawn_rate * dt:
            self._spawn_bubble()

        # Seaweed sway phase
        for s in self.seaweed:
            s.phase += dt * self.rng.uniform(0.4, 0.9)

    def _draw_background(self):
        h, w = self.stdscr.getmaxyx()
        # Subtle water "noise" dots
        if w < 10 or h < 6:
            return
        count = (w * h) // 220
        attr = curses.color_pair(5) if curses.has_colors() else 0
        for _ in range(count):
            y = self.rng.randint(1, h - 3)
            x = self.rng.randint(0, w - 2)
            if self.rng.random() < 0.6:
                safe_add(self.stdscr, y, x, ".", attr)

    def _draw_surface(self):
        h, w = self.stdscr.getmaxyx()
        if h < 2:
            return
        attr = curses.color_pair(6) if curses.has_colors() else 0
        # Wavy surface line
        y = 0
        s = []
        for x in range(w):
            wave = math.sin((x / 7.0) + self.t * 1.3)
            s.append("~" if wave > 0.25 else "-" if wave > -0.25 else "_")
        safe_add(self.stdscr, y, 0, "".join(s), attr)

    def _draw_corals(self):
        h, w = self.stdscr.getmaxyx()
        bottom = h - 2
        for c in self.corals:
            attr = curses.color_pair(c.color) if curses.has_colors() else 0
            sh = c.shape
            base_y = bottom - len(sh)
            for i, row in enumerate(sh):
                safe_add(self.stdscr, base_y + i, c.x, row, attr)

    def _draw_sand(self):
        h, w = self.stdscr.getmaxyx()
        if h < 2:
            return
        y = h - 1
        # sand texture
        chars = [".", ",", ":", ";", "·"]
        line = "".join(self.rng.choice(chars) for _ in range(w))
        attr = curses.color_pair(4) if curses.has_colors() else 0
        safe_add(self.stdscr, y, 0, line, attr)

    def _draw_seaweed(self):
        h, w = self.stdscr.getmaxyx()
        bottom = h - 2
        for s in self.seaweed:
            attr = curses.color_pair(s.color) if curses.has_colors() else 0
            sway = math.sin(self.t * 1.1 + s.phase) * 2.2
            # draw from bottom upwards
            for i in range(s.height):
                y = bottom - 1 - i
                if y <= 1:
                    break
                off = int(round(math.sin((i / 2.0) + s.phase + self.t) * 0.8 + sway))
                x = clamp(s.base_x + off, 1, w - 2)
                stem = self.rng.choice(SEAWEED_STEMS) if i < s.height - 1 else self.rng.choice(SEAWEED_TIPS)
                safe_add(self.stdscr, y, x, stem, attr)

    def _draw_bubbles(self):
        for b in self.bubbles:
            attr = curses.color_pair(b.color) if curses.has_colors() else 0
            safe_add(self.stdscr, int(round(b.y)), int(round(b.x)), b.ch, attr)

    def _draw_fish(self):
        for f in self.fish:
            frames = f.frames()
            idx = int(f.phase) % len(frames)
            art = frames[idx]
            y = int(round(f.y + math.sin(f.bob_phase) * 0.4))
            x = int(round(f.x))
            attr = curses.color_pair(f.color) if curses.has_colors() else 0
            safe_add(self.stdscr, y, x, art, attr)

    def _draw_hud(self):
        h, w = self.stdscr.getmaxyx()
        attr = curses.A_DIM
        if curses.has_colors():
            attr |= curses.color_pair(5)
        msg = " aquarium  |  q quit  p pause  +/- speed "
        if self.paused:
            msg += "|  PAUSED "
        safe_add(self.stdscr, h - 1, max(0, w - len(msg) - 1), msg, attr)

    def draw(self):
        self.stdscr.erase()
        self._draw_surface()
        self._draw_background()
        self._draw_bubbles()
        self._draw_fish()
        self._draw_seaweed()
        self._draw_corals()
        self._draw_sand()
        self._draw_hud()
        self.stdscr.refresh()

    def run(self):
        last = time.perf_counter()
        while True:
            if not self._handle_input():
                break

            now = time.perf_counter()
            dt = now - last
            last = now
            dt = clamp(dt, 0.0, 0.25)

            if not self.paused:
                self.t += dt
                self._update(dt)

            self.draw()
            time.sleep(self.dt)


def main(stdscr):
    aq = Aquarium(stdscr)
    aq.run()


if __name__ == "__main__":
    curses.wrapper(main)
