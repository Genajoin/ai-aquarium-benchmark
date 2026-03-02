# 43 t/s 2.5 min. ошибка. ошибка. исправил

import curses
import random
import time

class Aquarium:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.bubbles = []
        self.fishes = []
        self.corals = []
        self.plants = []
        self.background = ' '

    def create_bubble(self):
        x = random.randint(0, self.width - 1)
        return {
            'x': x,
            'y': self.height - 1,
            'speed': random.uniform(0.1, 0.4),
            'symbol': random.choice(['o', 'O', '●', '○'])
        }

    def create_fish(self):
        y = random.randint(2, self.height - 3)
        x = random.choice([0, self.width - 6])
        symbol = random.choice(['<(^)^>', '> (^)^<'])
        speed = random.uniform(0.08, 0.12)
        return {
            'x': x,
            'y': y,
            'speed': speed,
            'symbol': symbol,
            'direction': 1 if x == 0 else -1
        }

    def create_coral(self):
        x = random.randint(0, self.width - 5)
        y = random.randint(0, self.height - 5)
        return {
            'x': x,
            'y': y,
            'symbols': ['#', '##', '[]', '[[]]'],
            'index': 0
        }

    def create_plant(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(self.height - 5, self.height - 1)
        return {
            'x': x,
            'y': y,
            'offset': 0
        }

    def update_bubbles(self):
        for bubble in self.bubbles:
            bubble['y'] -= bubble['speed']
            if bubble['y'] < 0:
                self.bubbles.remove(bubble)

    def update_fishes(self):
        for fish in self.fishes:
            fish['x'] += fish['speed'] * fish['direction']
            if fish['x'] >= self.width - len(fish['symbol']) or fish['x'] < 0:
                fish['direction'] *= -1
                fish['symbol'] = '> (^)^<' if fish['direction'] == -1 else '<(^)^>'

    def update_corals(self):
        for coral in self.corals:
            coral['index'] = (coral['index'] + 1) % len(coral['symbols'])
            try:
                self.stdscr.addstr(coral['y'], coral['x'], coral['symbols'][coral['index']])
            except:
                pass

    def update_plants(self):
        for plant in self.plants:
            plant['offset'] += 0.1
            y = int(plant['y'] - 2 + (3 * random.random())) + int(plant['offset'] % 1)
            self.stdscr.addch(y, plant['x'], '~')

    def draw_background(self):
        self.stdscr.clear()
        for y in range(self.height):
            for x in range(0, self.width, 3):
                try:
                    self.stdscr.addch(y, x, self.background)
                except:
                    pass

    def draw_objects(self):
        # Bubbles
        for bubble in self.bubbles:
            try:
                self.stdscr.addstr(int(bubble['y']), bubble['x'], bubble['symbol'])
            except:
                pass

        # Fish
        for fish in self.fishes:
            try:
                self.stdscr.addstr(int(fish['y']), int(fish['x']), fish['symbol'])
            except:
                pass

    def run(self):
        curses.curs_set(0)
        self.stdscr.nodelay(True)

        for _ in range(10):
            self.bubbles.append(self.create_bubble())

        for _ in range(3):
            self.fishes.append(self.create_fish())

        for _ in range(8):
            self.corals.append(self.create_coral())

        for _ in range(15):
            self.plants.append(self.create_plant())

        while True:
            self.update_bubbles()
            self.update_fishes()

            while len(self.bubbles) < 10 and random.random() < 0.05:
                self.bubbles.append(self.create_bubble())

            self.draw_background()
            self.draw_objects()

            self.stdscr.refresh()
            time.sleep(0.05)

            try:
                if self.stdscr.getch() == ord('q'):
                    break
            except:
                pass

def main(stdscr):
    aquarium = Aquarium(stdscr)
    aquarium.run()

if __name__ == "__main__":
    curses.wrapper(main)
