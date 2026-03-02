# версия неизвестна доподлино. 25.02.26 

import curses
import random
import time
import math

class AquariumScreenSaver:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        curses.start_color()
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Bubbles
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Plants/grass
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Fish
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Corals
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)     # Special fish
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Water
        
        self.max_y, self.max_x = stdscr.getmaxyx()
        
        # Initialize elements
        self.bubbles = []
        self.fishes = []
        self.plants = []
        self.corals = []
        
        self.init_scene()
        
    def init_scene(self):
        """Initialize all aquarium elements"""
        # Create bubbles
        for _ in range(15):
            self.bubbles.append(Bubble(
                random.randint(1, self.max_x - 2),
                random.randint(1, self.max_y - 2)
            ))
        
        # Create plants (grass)
        plant_positions = set()
        for _ in range(8):
            x = random.randint(2, self.max_x - 10)
            # Avoid overlapping plants
            while any(abs(x - px) < 4 for px in plant_positions):
                x = random.randint(2, self.max_x - 10)
            plant_positions.add(x)
            self.plants.append(Plant(x, self.max_y - 2))
        
        # Create corals
        for _ in range(5):
            x = random.randint(2, self.max_x - 8)
            self.corals.append(Coral(x, self.max_y - 3))
        
        # Create fish
        for _ in range(4):
            self.fishes.append(Fish(
                random.randint(5, self.max_x - 10),
                random.randint(5, self.max_y - 10)
            ))
    
    def update(self):
        """Update all elements"""
        # Update bubbles
        for bubble in self.bubbles:
            bubble.move(self.max_y, self.max_x)
        
        # Update plants
        for plant in self.plants:
            plant.sway()
        
        # Update fish
        for fish in self.fishes:
            fish.move(self.max_y, self.max_x)
    
    def draw(self):
        """Draw all elements"""
        self.stdscr.clear()
        
        # Draw water background
        for y in range(self.max_y):
            for x in range(self.max_x):
                try:
                    self.stdscr.addch(y, x, '~', curses.color_pair(6) | curses.A_DIM)
                except curses.error:
                    pass
        
        # Draw corals (bottom layer)
        for coral in self.corals:
            coral.draw(self.stdscr)
        
        # Draw plants
        for plant in self.plants:
            plant.draw(self.stdscr)
        
        # Draw bubbles
        for bubble in self.bubbles:
            bubble.draw(self.stdscr)
        
        # Draw fish (top layer)
        for fish in self.fishes:
            fish.draw(self.stdscr)
        
        # Draw bottom sand line
        try:
            self.stdscr.addstr(self.max_y - 1, 0, '=' * self.max_x, 
                              curses.color_pair(2) | curses.A_BOLD)
        except curses.error:
            pass
        
        self.stdscr.refresh()
    
    def run(self):
        """Main loop"""
        while True:
            # Check for key press to exit
            key = self.stdscr.getch()
            if key != -1:
                break
            
            self.update()
            self.draw()
            time.sleep(0.1)

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.5, 2.0)
        self.size = random.choice(['o', 'O', '0'])
        self.offset = random.uniform(0, 2 * math.pi)
    
    def move(self, max_y, max_x):
        # Move upward with slight horizontal sway
        self.y -= self.speed * 0.3
        self.x += math.sin(time.time() + self.offset) * 0.5
        
        # Reset if out of bounds
        if self.y < 1:
            self.y = max_y - 2
            self.x = random.randint(1, max_x - 2)
    
    def draw(self, stdscr):
        try:
            if 0 <= self.y < stdscr.getmaxyx()[0] and 0 <= self.x < stdscr.getmaxyx()[1]:
                stdscr.addch(int(self.y), int(self.x), self.size, 
                            curses.color_pair(1) | curses.A_BOLD)
        except curses.error:
            pass

class Fish:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(1.0, 3.0)
        self.body = '><>' if self.direction > 0 else '<><'
        self.color = random.choice([3, 5])
        self.vertical_speed = random.uniform(-0.5, 0.5)
        self.last_change = time.time()
    
    def move(self, max_y, max_x):
        # Change direction occasionally
        if random.random() < 0.01:
            self.direction *= -1
            self.body = '><>' if self.direction > 0 else '<><'
        
        # Move horizontally
        self.x += self.direction * self.speed * 0.2
        
        # Gentle vertical movement
        self.y += math.sin(time.time() * 2) * 0.1
        
        # Bounce off walls
        if self.x <= 2:
            self.x = 2
            self.direction = 1
            self.body = '><>'
        elif self.x >= max_x - 4:
            self.x = max_x - 4
            self.direction = -1
            self.body = '<><'
        
        # Keep within vertical bounds
        if self.y <= 2:
            self.y = 2
        elif self.y >= max_y - 4:
            self.y = max_y - 4
    
    def draw(self, stdscr):
        try:
            if 0 <= self.y < stdscr.getmaxyx()[0] and 0 <= self.x < stdscr.getmaxyx()[1]:
                stdscr.addstr(int(self.y), int(self.x), self.body, 
                             curses.color_pair(self.color) | curses.A_BOLD)
        except curses.error:
            pass

class Plant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = random.randint(3, 6)
        self.sway_offset = random.uniform(0, 2 * math.pi)
        self.characters = ['|', '║', '║', '║', '║', '║', '║']
    
    def sway(self):
        # Plants sway in the current
        self.current_sway = math.sin(time.time() * 2 + self.sway_offset) * 0.3
    
    def draw(self, stdscr):
        sway_x = int(self.current_sway * 2)
        
        for i in range(self.height):
            y_pos = self.y - i
            x_pos = self.x + int(sway_x * (i / self.height))
            
            if y_pos > 0:
                try:
                    char = '║' if i < self.height - 1 else '╚' if sway_x < 0 else '╔'
                    stdscr.addch(y_pos, x_pos, char, 
                                curses.color_pair(2) | curses.A_BOLD)
                    
                    # Add leaves at the top
                    if i == self.height - 1:
                        if random.random() > 0.5:
                            stdscr.addch(y_pos, x_pos + 1, '╩', 
                                        curses.color_pair(2) | curses.A_BOLD)
                        else:
                            stdscr.addch(y_pos, x_pos - 1, '╦', 
                                        curses.color_pair(2) | curses.A_BOLD)
                except curses.error:
                    pass

class Coral:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.patterns = [
            ['▀▄▀', '▄▀▄'],
            ['▓▒░', '░▒▓'],
            ['◢◣', '◥◤'],
            ['╱╲', '╲╱']
        ]
        self.pattern = random.choice(self.patterns)
    
    def draw(self, stdscr):
        try:
            # Draw coral formation
            stdscr.addstr(self.y, self.x, self.pattern[0], 
                         curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(self.y + 1, self.x, self.pattern[1], 
                         curses.color_pair(4) | curses.A_BOLD)
            
            # Add some details
            for i in range(2):
                if random.random() > 0.7:
                    stdscr.addch(self.y + i, self.x + 3, '*', 
                                curses.color_pair(4) | curses.A_DIM)
        except curses.error:
            pass

def main(stdscr):
    aquarium = AquariumScreenSaver(stdscr)
    aquarium.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")