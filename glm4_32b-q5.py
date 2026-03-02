# 37 t/s, 23s

import curses
import random
import time

class Bubble:
    def __init__(self, height, width):
        self.x = random.randint(1, width - 2)
        self.y = height - 1
        self.speed = random.uniform(0.1, 0.5)

    def move(self):
        self.y -= self.speed

class Fish:
    def __init__(self, height, width):
        self.x = random.randint(1, width - 2)
        self.y = random.randint(1, height - 2)
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(0.1, 0.5)

    def move(self):
        self.x += self.direction * self.speed
        if self.x <= 1 or self.x >= curses.COLS - 2:
            self.direction *= -1

    def draw(self, stdscr):
        fish_str = '<>' if self.direction > 0 else '<>'
        stdscr.addstr(int(self.y), int(self.x), fish_str)

class Seaweed:
    def __init__(self, height, width):
        self.x = random.randint(1, width - 2)
        self.height = random.randint(3, 10)
        self.segments = ['|', '/', '\\', '|', '/', '\\']

    def draw(self, stdscr):
        for i in range(self.height):
            stdscr.addch(i + 1, self.x, self.segments[i % len(self.segments)])

class Coral:
    def __init__(self, height, width):
        self.x = random.randint(1, width - 2)
        self.height = random.randint(2, 5)
        self.width = random.randint(2, 5)

    def draw(self, stdscr):
        for i in range(self.height):
            for j in range(self.width):
                stdscr.addch(i + 1, self.x + j, '#')

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    height, width = stdscr.getmaxyx()
    bubbles = [Bubble(height, width) for _ in range(20)]
    fishes = [Fish(height, width) for _ in range(5)]
    seaweeds = [Seaweed(height, width) for _ in range(5)]
    corals = [Coral(height, width) for _ in range(3)]

    while True:
        stdscr.clear()
        stdscr.border(0)

        for bubble in bubbles:
            if bubble.y > 1:
                stdscr.addch(int(bubble.y), int(bubble.x), '.')
                bubble.move()
            else:
                bubble.y = height - 1
                bubble.x = random.randint(1, width - 2)

        for fish in fishes:
            fish.move()
            fish.draw(stdscr)

        for seaweed in seaweeds:
            seaweed.draw(stdscr)

        for coral in corals:
            coral.draw(stdscr)

        stdscr.refresh()

        if stdscr.getch() != -1:
            break

        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)
