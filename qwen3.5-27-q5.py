# 35 t/s, 1.5 min, с первого раза

import curses
import time
import random
import math

# --- Настройки ---
FPS = 30
FRAME_DELAY = 1.0 / FPS

# --- Вспомогательные функции ---
def get_random_color():
    """Генерирует случайный цвет (от 1 до 255 для 24-битного цвета или базовые)"""
    return random.randint(1, 6) # Используем базовые цвета curses для совместимости

def init_colors(stdscr):
    """Инициализация пар цветов"""
    curses.start_color()
    curses.use_default_colors()
    # (Foreground, Background)
    curses.init_pair(1, curses.COLOR_CYAN, -1)     # Пузырьки
    curses.init_pair(2, curses.COLOR_YELLOW, -1)   # Рыбки
    curses.init_pair(3, curses.COLOR_GREEN, -1)    # Трава
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)  # Кораллы
    curses.init_pair(5, curses.COLOR_BLACK, -1)    # Песок/Тени

# --- Классы объектов ---

class Bubble:
    def __init__(self, max_y, max_x):
        self.x = random.randint(0, max_x - 1)
        self.y = random.randint(max_y - 10, max_y - 1)
        self.speed = random.uniform(0.05, 0.2)
        self.size = random.choice(["(", "O", ")"])
        self.color = curses.color_pair(1)
        self.reset(max_y)

    def reset(self, max_y):
        self.y = random.randint(max_y - 5, max_y - 1)
        self.x = random.randint(0, curses.COLS - 1)
        self.speed = random.uniform(0.05, 0.2)

    def move(self):
        self.y -= self.speed
        if self.y < 0:
            self.reset(curses.LINES)

class Fish:
    def __init__(self, max_y, max_x):
        self.max_x = max_x
        self.x = random.randint(0, max_x)
        self.y = random.randint(5, max_y // 2)
        self.direction = 1 if random.random() > 0.5 else -1
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.choice(["small", "medium"])
        self.color = curses.color_pair(2)
        self.frame = 0

    def get_body(self, facing_right):
        if self.size == "small":
            return ">8" if facing_right else "8<"
        else:
            return ">>8" if facing_right else "8<<"

    def move(self):
        self.x += self.speed * self.direction
        
        # Отскок от стен
        if self.x > self.max_x - 5:
            self.direction = -1
            self.x = self.max_x - 5
        elif self.x < 0:
            self.direction = 1
            self.x = 0
            
        self.frame += 1

    def draw(self, stdscr):
        self.frame %= 4 # Анимация хвоста (цикл 4 кадра)
        facing_right = self.direction == 1
        body = self.get_body(facing_right)
        
        # Рисуем тело
        stdscr.attron(self.color | curses.A_BOLD)
        try:
            stdscr.addstr(int(self.y), int(self.x), body)
        except curses.error:
            pass
        stdscr.attroff(self.color | curses.A_BOLD)

class Plant:
    def __init__(self, x, max_y, max_x):
        self.x = x
        self.max_y = max_y
        self.height = random.randint(3, 8)
        self.type = random.choice(["grass", "coral"])
        self.sway_offset = random.random() * math.pi * 2
        self.color = curses.color_pair(3) if self.type == "grass" else curses.color_pair(4)

    def draw(self, stdscr, time_val):
        # Эффект покачивания
        sway = math.sin(time_val + self.sway_offset) * 1.5
        
        for i in range(self.height):
            # Вычисляем смещение для текущего сегмента
            offset = int(sway * (1 - i / self.height))
            
            # Выбор символа
            if self.type == "grass":
                char = "|" if i < self.height - 2 else "/" if sway > 0 else "\\"
            else: # Коралл (шире)
                char = "X" if i % 2 == 0 else "="

            y = self.max_y - 1 - i
            x = self.x + offset
            
            try:
                if 0 <= y < curses.LINES and 0 <= x < curses.COLS:
                    stdscr.attron(self.color)
                    stdscr.addstr(y, x, char)
                    stdscr.attroff(self.color)
            except curses.error:
                pass

# --- Основная функция ---

def main(stdscr):
    init_colors(stdscr)
    curses.curs_set(0) # Скрыть курсор
    stdscr.nodelay(True) # Не блокировать ввод
    
    max_y, max_x = stdscr.getmaxyx()
    
    # Инициализация объектов
    bubbles = [Bubble(max_y, max_x) for _ in range(30)]
    fish_list = [Fish(max_y, max_x) for _ in range(4)]
    # Растения ставим только в нижней части
    plants = []
    plant_spacing = 5
    for i in range(0, max_x, plant_spacing):
        plants.append(Plant(i, max_y, max_x))
        
    # Песок (фон)
    sand_y = max_y - 1
    sand_color = curses.color_pair(5) # Темный
    
    frame_count = 0
    start_time = time.time()

    while True:
        # Обработка выхода
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
        except:
            pass

        # Очистка экрана (но мы будем перерисовывать всё, это проще для скринсейвера)
        stdscr.erase()
        
        # Рисуем песок
        stdscr.attron(sand_color)
        try:
            stdscr.addstr(sand_y, 0, " " * max_x)
        except curses.error:
            pass
        stdscr.attroff(sand_color)

        current_time = time.time()
        
        # 1. Рисуем и двигаем растения
        for plant in plants:
            plant.draw(stdscr, current_time)

        # 2. Рисуем и двигаем рыбок
        for fish in fish_list:
            fish.move()
            fish.draw(stdscr)

        # 3. Рисуем и двигаем пузырьки
        for bubble in bubbles:
            bubble.move()
            # Простая отрисовка пузырька
            if 0 <= bubble.y < max_y and 0 <= bubble.x < max_x:
                stdscr.attron(bubble.color)
                try:
                    # Рисуем только символ, который сейчас у пузыря
                    stdscr.addstr(int(bubble.y), int(bubble.x), bubble.size)
                except curses.error:
                    pass
                stdscr.attroff(bubble.color)

        # Обновляем экран
        stdscr.refresh()
        
        # Контроль FPS
        elapsed = time.time() - current_time
        if elapsed < FRAME_DELAY:
            time.sleep(FRAME_DELAY - elapsed)

if __name__ == "__main__":
    curses.wrapper(main)
