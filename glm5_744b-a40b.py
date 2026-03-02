
import curses
import random
import time
import math

# --- Настройки ---
FPS = 30
FISH_COUNT = 7
BUBBLE_COUNT = 15
SEAWEED_COUNT = 10
CORAL_COUNT = 5

class Bubble:
    def __init__(self, max_y, max_x):
        self.reset(max_y, max_x, initial=True)

    def reset(self, max_y, max_x, initial=False):
        self.x = random.randint(1, max_x - 2)
        self.y = max_y - 2 if initial else random.randint(1, max_y - 2)
        self.speed = random.uniform(0.2, 0.6)
        self.wobble_phase = random.uniform(0, math.pi)
        # Символы пузырьков
        self.chars = ['.', 'o', 'O', '0']
        self.char_idx = 0

    def update(self, max_y, max_x):
        self.y -= self.speed
        self.wobble_phase += 0.2
        # Покачивание влево-вправо
        self.x += math.sin(self.wobble_phase) * 0.3
        
        # Рост пузырька при подъеме
        if random.random() < 0.1:
             self.char_idx = min(self.char_idx + 1, len(self.chars) - 1)

        if self.y < 1:
            self.reset(max_y, max_x)

    def draw(self, stdscr):
        char = self.chars[self.char_idx]
        try:
            stdscr.addstr(int(self.y), int(self.x), char, curses.color_pair(1))
        except curses.error:
            pass

class Fish:
    def __init__(self, max_y, max_x):
        self.y = random.randint(2, max_y - 5)
        self.x = random.randint(1, max_x - 10)
        self.direction = random.choice([-1, 1]) # -1: лево, 1: право
        self.speed = random.uniform(0.15, 0.4)
        self.color = random.choice([2, 3, 4, 5]) # Разные цвета
        self.body_right = "><(((('>" # Вид справа
        self.body_left = "<'(((><"   # Вид слева
        self.counter = random.randint(0, 10)

    def update(self, max_y, max_x):
        self.counter += 1
        
        # Движение
        self.x += self.speed * self.direction
        
        # Случайная смена направления и глубины
        if random.random() < 0.01:
            self.direction *= -1
        if random.random() < 0.02:
            self.y += random.choice([-1, 1])
            self.y = max(2, min(self.y, max_y - 4))

        # Границы экрана
        if self.x > max_x - 2:
            self.direction = -1
        if self.x < 2:
            self.direction = 1

    def draw(self, stdscr):
        body = self.body_right if self.direction == 1 else self.body_left
        # Анимация хвоста (простая смена кадра)
        if self.counter % 4 < 2:
             body = body.replace("(", ")") if self.direction == 1 else body.replace(")", "(")

        try:
            stdscr.addstr(int(self.y), int(self.x), body, curses.color_pair(self.color))
        except curses.error:
            pass

class Seaweed:
    def __init__(self, x, max_y):
        self.x = x
        self.max_y = max_y
        self.height = random.randint(4, 8)
        self.phase = random.uniform(0, math.pi * 2)
        self.chars = ['|', '/', '\\', '|']

    def update(self):
        self.phase += 0.15

    def draw(self, stdscr):
        for i in range(self.height):
            # Колыхание травы
            offset_x = math.sin(self.phase + i * 0.5) * 2
            y = self.max_y - 2 - i
            
            char_idx = int((self.phase + i) % len(self.chars))
            char = self.chars[char_idx]
            
            try:
                stdscr.addstr(y, int(self.x + offset_x), char, curses.color_pair(2))
            except curses.error:
                pass

class Coral:
    def __init__(self, max_y, max_x):
        self.y = max_y - 2
        self.x = random.randint(2, max_x - 4)
        self.shape = random.choice([
            [" %%% ", "%@%@%"],
            [" /\\ ", "(##)", " #### "],
            ["(###)", "/#/#\\"]
        ])
        self.color = random.choice([3, 4, 5])

    def draw(self, stdscr):
        for i, line in enumerate(self.shape):
            try:
                stdscr.addstr(self.y - i, self.x, line, curses.color_pair(self.color))
            except curses.error:
                pass

def main(stdscr):
    # Настройка curses
    curses.curs_set(0)  # Скрыть курсор
    stdscr.nodelay(1)   # Неблокирующий ввод
    curses.start_color()
    
    # Инициализация цветов (пары: номер, текст, фон)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Пузырьки
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Водоросли
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Рыбки 1
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Кораллы/Рыбки
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# Рыбки 2

    # Получение размеров экрана
    max_y, max_x = stdscr.getmaxyx()

    # Создание объектов
    bubbles = [Bubble(max_y, max_x) for _ in range(BUBBLE_COUNT)]
    fishes = [Fish(max_y, max_x) for _ in range(FISH_COUNT)]
    
    # Равномерное распределение водорослей
    seaweeds = []
    step = max_x // (SEAWEED_COUNT + 1)
    for i in range(SEAWEED_COUNT):
        seaweeds.append(Seaweed(step * (i + 1), max_y))
        
    corals = [Coral(max_y, max_x) for _ in range(CORAL_COUNT)]

    while True:
        # Проверка выхода
        key = stdscr.getch()
        if key != -1:
            break
        
        stdscr.erase() # Очистка экрана

        # Обновление размеров окна (если пользователь изменил размер терминала)
        max_y, max_x = stdscr.getmaxyx()
        
        # 1. Рисуем дно
        stdscr.hline(max_y - 2, 0, '~', max_x, curses.color_pair(2))

        # 2. Обновляем и рисуем объекты (порядок важен для слоев)
        
        # Водоросли
        for sw in seaweeds:
            sw.update()
            sw.draw(stdscr)
            
        # Кораллы (статичные, но могут быть "дышащими" в будущем)
        for c in corals:
            c.draw(stdscr)

        # Пузырьки
        for b in bubbles:
            b.update(max_y, max_x)
            b.draw(stdscr)

        # Рыбки
        for f in fishes:
            f.update(max_y, max_x)
            f.draw(stdscr)

        stdscr.refresh()
        time.sleep(1.0 / FPS)

if __name__ == "__main__":
    curses.wrapper(main)