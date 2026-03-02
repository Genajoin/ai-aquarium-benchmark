import curses
import random
import math
import time

# Конфигурация
FPS = 15
FISH_COUNT = 5
BUBBLE_COUNT = 20
GRASS_COUNT = 15

# Символы
FISH_RIGHT = ">))°>"
FISH_LEFT = "<°((<"
BUBBLES_CHARS = ["o", "O", ".", "°"]
GRASS_CHARS = ["╙", "│", "╵", "║"]
CORAL_CHARS = ["Y", "H", "K", "M", "W"]
SAND_CHAR = "▒"

class Entity:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class Fish(Entity):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.reset()
        # Случайная начальная позиция по Y (не слишком низко, не слишком высоко)
        self.y = random.randint(2, height - 4)

    def reset(self):
        self.speed = random.uniform(0.3, 0.8)
        self.direction = 1 if random.random() > 0.5 else -1
        self.x = random.randint(0, self.width - len(FISH_RIGHT))
        self.color = random.randint(1, 6) # Разные цвета рыбок

    def update(self):
        self.x += self.speed * self.direction
        
        # Разворот у стен
        if self.direction == 1 and self.x >= self.width - len(FISH_RIGHT):
            self.direction = -1
        elif self.direction == -1 and self.x <= 0:
            self.direction = 1
            
        # Случайное изменение высоты (ныряние)
        if random.random() < 0.02:
            self.y += random.choice([-1, 1])
            self.y = max(2, min(self.height - 4, self.y))

    def draw(self, win):
        sprite = FISH_RIGHT if self.direction == 1 else FISH_LEFT
        try:
            win.addstr(int(self.y), int(self.x), sprite, curses.color_pair(self.color))
        except curses.error:
            pass

class Bubble(Entity):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.width - 1)
        self.y = self.height - 1
        self.speed = random.uniform(0.2, 0.6)
        self.char = random.choice(BUBBLES_CHARS)
        self.wobble = random.uniform(0, 10) # Для покачивания

    def update(self, frame):
        self.y -= self.speed
        self.wobble += 0.1
        # Покачивание влево-вправо
        self.x += math.sin(self.wobble) * 0.2

        if self.y < 0:
            self.reset()

    def draw(self, win):
        try:
            win.addch(int(self.y), int(self.x), self.char, curses.color_pair(7)) # Белый/голубой
        except curses.error:
            pass

class Grass(Entity):
    def __init__(self, x, height):
        super().__init__(0, height) # Width не важен для травы
        self.x = x
        self.height = random.randint(3, 8)
        self.sway_offset = random.uniform(0, 10)
        
    def draw(self, win, time_val):
        # Эффект волны
        sway = math.sin(time_val * 2 + self.sway_offset) * 1.5
        
        for i in range(self.height):
            y_pos = self.height - i # Рисуем снизу вверх относительно базы
            actual_y = (self.height_base) - i 
            
            # Смещение по X для эффекта изгиба
            offset_x = int(sway * (i / self.height))
            
            char = GRASS_CHARS[i % len(GRASS_CHARS)]
            try:
                # Зеленый цвет
                win.addch(actual_y, self.x + offset_x, char, curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass

class Coral(Entity):
    def __init__(self, x, height_base):
        self.x = x
        self.height_base = height_base
        self.height = random.randint(2, 5)
        self.char = random.choice(CORAL_CHARS)
        self.color = random.choice([1, 3, 5]) # Красный, желтый, розовый

    def draw(self, win):
        for i in range(self.height):
            try:
                y = self.height_base - i
                win.addch(y, self.x, self.char, curses.color_pair(self.color))
                # Ветвление
                if i > 1 and random.random() > 0.7:
                     win.addch(y, self.x + 1, '.', curses.color_pair(self.color))
            except curses.error:
                pass

def main(stdscr):
    # Настройка curses
    curses.curs_set(0)  # Скрыть курсор
    stdscr.nodelay(1)   # Не блокировать ввод
    stdscr.timeout(1000 // FPS)
    
    # Инициализация цветов
    curses.start_color()
    curses.use_default_colors()
    # Пары цветов: (номер_пары, цвет_текста, цвет_фона)
    curses.init_pair(1, curses.COLOR_RED, -1)      # Рыбка 1
    curses.init_pair(2, curses.COLOR_GREEN, -1)    # Трава
    curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Рыбка 2 / Песок
    curses.init_pair(4, curses.COLOR_BLUE, -1)     # Вода (фон)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # Коралл
    curses.init_pair(6, curses.COLOR_CYAN, -1)     # Рыбка 3
    curses.init_pair(7, curses.COLOR_WHITE, -1)    # Пузырьки

    height, width = stdscr.getmaxyx()
    
    # Создаем объекты
    fishes = [Fish(width, height) for _ in range(FISH_COUNT)]
    bubbles = [Bubble(width, height) for _ in range(BUBBLE_COUNT)]
    
    # Генерируем статичный декор (трава и кораллы)
    grasses = []
    corals = []
    sand_level = height - 2
    
    # Распределяем траву и кораллы по дну, избегая наложений
    occupied_x = set()
    for _ in range(GRASS_COUNT):
        x = random.randint(2, width - 2)
        if x not in occupied_x:
            g = Grass(x, sand_level)
            g.height_base = sand_level
            grasses.append(g)
            occupied_x.add(x)
            
    for _ in range(5):
        x = random.randint(2, width - 2)
        if x not in occupied_x:
            c = Coral(x, sand_level)
            corals.append(c)
            occupied_x.add(x)

    frame_count = 0
    
    while True:
        # Очистка экрана (можно заменить на заливку синим, если терминал поддерживает)
        stdscr.clear()
        
        # Рисуем песок
        try:
            stdscr.addstr(sand_level, 0, SAND_CHAR * width, curses.color_pair(3))
        except curses.error:
            pass

        # Рисуем кораллы (задний план)
        for coral in corals:
            coral.draw(stdscr)

        # Рисуем траву
        time_val = frame_count / 20.0
        for grass in grasses:
            grass.draw(stdscr, time_val)

        # Обновляем и рисуем пузырьки
        for bubble in bubbles:
            bubble.update(frame_count)
            bubble.draw(stdscr)

        # Обновляем и рисуем рыбок
        for fish in fishes:
            fish.update()
            fish.draw(stdscr)
            
        # Проверка на изменение размера окна
        new_h, new_w = stdscr.getmaxyx()
        if new_h != height or new_w != width:
            height, width = new_h, new_w
            # Пересоздаем сущности при ресайзе, чтобы не вылетали за границы
            fishes = [Fish(width, height) for _ in range(FISH_COUNT)]
            bubbles = [Bubble(width, height) for _ in range(BUBBLE_COUNT)]
            sand_level = height - 2

        # Выход по нажатию 'q'
        key = stdscr.getch()
        if key == ord('q'):
            break
            
        stdscr.refresh()
        frame_count += 1

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass