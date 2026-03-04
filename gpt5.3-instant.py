import curses
import random
import time

FISH_RIGHT = ["<><", "><>", ">))'>"]
FISH_LEFT = ["><>", "<><", "<'((<"]

BUBBLE = "o"
SEAWEED = ["|", "/", "\\"]
CORALS = ["Y", "W", "M"]

class Fish:
    def __init__(self, max_y, max_x):
        self.y = random.randint(2, max_y-5)
        self.x = random.randint(2, max_x-10)
        self.dir = random.choice([-1, 1])
        self.speed = random.uniform(0.05, 0.2)
        self.sprite = random.choice(FISH_RIGHT if self.dir == 1 else FISH_LEFT)

    def move(self, max_x):
        self.x += self.dir
        if self.x > max_x - 5:
            self.dir = -1
            self.sprite = random.choice(FISH_LEFT)
        elif self.x < 1:
            self.dir = 1
            self.sprite = random.choice(FISH_RIGHT)

class Bubble:
    def __init__(self, max_y, max_x):
        self.y = max_y - 2
        self.x = random.randint(1, max_x - 2)
        self.speed = random.uniform(0.05, 0.2)

    def move(self):
        self.y -= 1

def draw_seaweed(stdscr, max_y, max_x, tick):
    for x in range(2, max_x, 10):
        height = random.randint(3,6)
        for i in range(height):
            char = SEAWEED[(tick+i) % len(SEAWEED)]
            stdscr.addstr(max_y-2-i, x, char)

def draw_corals(stdscr, max_y, max_x):
    for x in range(5, max_x, 20):
        coral = random.choice(CORALS)
        stdscr.addstr(max_y-2, x, coral)

def aquarium(stdscr):

    curses.curs_set(0)
    stdscr.nodelay(True)

    max_y, max_x = stdscr.getmaxyx()

    fishes = [Fish(max_y, max_x) for _ in range(6)]
    bubbles = []

    tick = 0

    while True:
        stdscr.erase()

        # spawn bubbles
        if random.random() < 0.3:
            bubbles.append(Bubble(max_y, max_x))

        # move bubbles
        for b in bubbles[:]:
            b.move()
            if b.y < 1:
                bubbles.remove(b)

        # draw bubbles
        for b in bubbles:
            stdscr.addstr(int(b.y), b.x, BUBBLE)

        # move fish
        for f in fishes:
            f.move(max_x)

        # draw fish
        for f in fishes:
            try:
                stdscr.addstr(int(f.y), int(f.x), f.sprite)
            except:
                pass

        draw_seaweed(stdscr, max_y, max_x, tick)
        draw_corals(stdscr, max_y, max_x)

        stdscr.refresh()

        tick += 1
        time.sleep(0.08)

def main():
    curses.wrapper(aquarium)

if __name__ == "__main__":
    main()
