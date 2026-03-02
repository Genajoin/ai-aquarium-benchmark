# 74 t\s, 2 исправления, 

import curses
import random
import time

import sys, termios, tty, select # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
t,_=termios.tcgetattr(0),tty.setcbreak(0) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!

# Определение цветов
colors = {
    "water": " ",
    "bubble": ".",
    "seaweed": "S",
    "fish": "F",
    "coral": "*"
}

# Определение размеров аквариума
WIDTH = 80
HEIGHT = 24

# Определение объектов аквариума
bubbles = [(random.randint(0, WIDTH - 1), HEIGHT - 1) for _ in range(10)]
seaweed_positions = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(10)]
fish_positions = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(5)]
coral_positions = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)) for _ in range(10)]

def draw(screen):
    screen.clear()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            char = colors["water"]
            for bubble in bubbles:
                if (x, y) == bubble:
                    char = colors["bubble"]
            for seaweed in seaweed_positions:
                if (x, y) == seaweed:
                    char = colors["seaweed"]
            for fish in fish_positions:
                if (x, y) == fish:
                    char = colors["fish"]
            for coral in coral_positions:
                if (x, y) == coral:
                    char = colors["coral"]
            screen.addch(y, x, char)
    screen.refresh()

def update():
    global bubbles
    bubbles = [(x, y - 1) if y > 0 else (random.randint(0, WIDTH - 1), HEIGHT - 1) for (x, y) in bubbles]

def main(stdscr):
    curses.curs_set(0)
    while True:
        if select.select([sys.stdin],[],[],0)[0]:termios.tcsetattr(0,termios.TCSADRAIN,t);break # ЭТО ВСТАВЛЕНО ВРУЧНУЮ!
        draw(stdscr)
        update()
        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)
