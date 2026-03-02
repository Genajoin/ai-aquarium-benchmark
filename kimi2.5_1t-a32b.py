"""
Terminal Aquarium Screensaver
Pseudo-graphics animation of underwater world
"""

import curses
import random
import math
import time
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Fish:
    x: float
    y: int
    direction: int  # 1 - right, -1 - left
    speed: float
    color: int
    size: int
    frame: int = 0
    
    # ASCII sprites for different sizes
    sprites_right = [
        ["><>"],
        [">))'>", "><((('>"],
        [">))'>", "><((('>", "><(((*>"]
    ]
    sprites_left = [
        ["<><"],
        ["<'((<", "<')))<"],
        ["<*(((<", "<'((<", "<')))<"]
    ]
    
    def get_sprite(self) -> str:
        self.frame = (self.frame + 1) % 20
        sprites = self.sprites_right if self.direction == 1 else self.sprites_left
        if self.size < len(sprites):
            variants = sprites[self.size]
            return variants[self.frame % len(variants)]
        return sprites[0][0]
    
    def move(self, max_x: int):
        self.x += self.speed * self.direction
        if self.direction == 1 and self.x > max_x + 10:
            self.x = -10
        elif self.direction == -1 and self.x < -10:
            self.x = max_x + 10


@dataclass
class Bubble:
    x: int
    y: float
    speed: float
    char: str
    wobble: float = 0.0
    
    def move(self):
        self.y -= self.speed
        self.wobble += 0.1
        self.x += math.sin(self.wobble) * 0.3


@dataclass
class Seaweed:
    x: int
    y: int
    height: int
    color: int
    phase: float
    chars: str = "│╱╲()"
    
    def draw(self, stdscr, tick: int):
        for i in range(self.height):
            wave = math.sin(tick * 0.1 + self.phase + i * 0.3) * 1.5
            char_idx = int((wave + 1.5) * (len(self.chars) - 1) / 3)
            char_idx = max(0, min(len(self.chars) - 1, char_idx))
            char = self.chars[char_idx]
            try:
                stdscr.addstr(self.y - i, self.x + int(wave), char, 
                            curses.color_pair(self.color))
            except curses.error:
                pass


@dataclass 
class Coral:
    x: int
    y: int
    color: int
    
    def draw(self, stdscr):
        # Simple coral shapes
        shapes = [
            " @ ",
            "@@@",
            " @ ",
            " # ",
            "###",
        ]
        for i, line in enumerate(shapes):
            try:
                stdscr.addstr(self.y - i, self.x, line, 
                            curses.color_pair(self.color))
            except curses.error:
                pass


class Aquarium:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_colors()
        self.max_y, self.max_x = stdscr.getmaxyx()
        self.fish: List[Fish] = []
        self.bubbles: List[Bubble] = []
        self.seaweeds: List[Seaweed] = []
        self.corals: List[Coral] = []
        self.tick = 0
        self.init_objects()
        
    def setup_colors(self):
        curses.start_color()
        curses.use_default_colors()
        # Define color pairs
        curses.init_pair(1, curses.COLOR_CYAN, -1)      # Water/bubbles
        curses.init_pair(2, curses.COLOR_YELLOW, -1)    # Fish 1
        curses.init_pair(3, curses.COLOR_MAGENTA, -1)   # Fish 2  
        curses.init_pair(4, curses.COLOR_RED, -1)       # Fish 3
        curses.init_pair(5, curses.COLOR_GREEN, -1)     # Seaweed
        curses.init_pair(6, curses.COLOR_WHITE, -1)     # Bubbles bright
        curses.init_pair(7, curses.COLOR_BLUE, -1)      # Deep water
        curses.init_pair(8, curses.COLOR_YELLOW, -1)    # Sand
        
    def init_objects(self):
        # Create fish
        for _ in range(8):
            self.fish.append(Fish(
                x=random.randint(0, self.max_x),
                y=random.randint(3, self.max_y - 5),
                direction=random.choice([-1, 1]),
                speed=random.uniform(0.2, 0.8),
                color=random.choice([2, 3, 4]),
                size=random.randint(0, 2)
            ))
        
        # Create seaweed on bottom
        for x in range(2, self.max_x - 2, random.randint(4, 8)):
            self.seaweeds.append(Seaweed(
                x=x,
                y=self.max_y - 2,
                height=random.randint(3, 8),
                color=5,
                phase=random.random() * 6.28
            ))
            
        # Create corals
        for _ in range(5):
            self.corals.append(Coral(
                x=random.randint(5, self.max_x - 5),
                y=self.max_y - 2,
                color=random.choice([4, 7])
            ))
            
    def spawn_bubble(self):
        if random.random() < 0.1:  # 10% chance per frame
            x = random.randint(1, self.max_x - 2)
            self.bubbles.append(Bubble(
                x=x,
                y=self.max_y - 2,
                speed=random.uniform(0.1, 0.4),
                char=random.choice(['o', 'O', '.', '*']),
                wobble=random.random() * 6.28
            ))
            
    def draw_sand(self):
        # Draw bottom sand
        sand_chars = "░▒▓█"
        for x in range(self.max_x):
            char = random.choice(sand_chars)
            try:
                self.stdscr.addstr(self.max_y - 1, x, char, 
                                 curses.color_pair(8))
            except curses.error:
                pass
                
    def draw_water_effect(self):
        # Subtle water shimmer effect
        if self.tick % 10 == 0:
            for _ in range(3):
                x = random.randint(0, self.max_x - 1)
                y = random.randint(0, self.max_y - 3)
                try:
                    self.stdscr.addstr(y, x, '~', curses.color_pair(7) | curses.A_DIM)
                except curses.error:
                    pass
                
    def update(self):
        self.stdscr.erase()
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        
        # Draw sand bottom
        self.draw_sand()
        
        # Draw water effects
        self.draw_water_effect()
        
        # Draw and update seaweed
        for weed in self.seaweeds:
            weed.draw(self.stdscr, self.tick)
            
        # Draw corals
        for coral in self.corals:
            coral.draw(self.stdscr)
            
        # Update and draw fish
        for f in self.fish:
            f.move(self.max_x)
            sprite = f.get_sprite()
            y = int(f.y)
            x = int(f.x)
            if 0 <= y < self.max_y - 1 and 0 <= x < self.max_x - len(sprite):
                try:
                    self.stdscr.addstr(y, x, sprite, 
                                     curses.color_pair(f.color) | curses.A_BOLD)
                except curses.error:
                    pass
                    
        # Spawn and update bubbles
        self.spawn_bubble()
        for b in self.bubbles[:]:
            b.move()
            if b.y < 1:
                self.bubbles.remove(b)
            else:
                y = int(b.y)
                x = int(b.x + math.sin(b.wobble))
                if 0 <= y < self.max_y - 1 and 0 <= x < self.max_x:
                    try:
                        attr = curses.color_pair(6) if b.char in ['O', '*'] else curses.color_pair(1)
                        self.stdscr.addstr(y, x, b.char, attr)
                    except curses.error:
                        pass
                        
        # Draw status line
        status = " 🐠  Terminal Aquarium  |  Press 'q' to quit  |  Fish: {}  Bubbles: {} ".format(
            len(self.fish), len(self.bubbles))
        try:
            self.stdscr.addstr(0, 0, status[:self.max_x-1], 
                             curses.color_pair(1) | curses.A_REVERSE)
        except curses.error:
            pass
            
        self.stdscr.refresh()
        self.tick += 1
        
    def run(self):
        self.stdscr.nodelay(True)  # Non-blocking input
        self.stdscr.timeout(50)    # 50ms refresh rate (~20 FPS)
        
        while True:
            try:
                key = self.stdscr.getch()
                if key == ord('q') or key == 27:  # q or ESC
                    break
                    
                self.update()
                time.sleep(0.05)
                
            except KeyboardInterrupt:
                break
            except curses.error:
                # Handle terminal resize errors gracefully
                pass


def main():
    try:
        curses.wrapper(lambda stdscr: Aquarium(stdscr).run())
    except Exception as e:
        print(f"Aquarium crashed: {e}")


if __name__ == "__main__":
    main()