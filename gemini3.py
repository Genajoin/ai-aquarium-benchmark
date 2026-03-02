# думающая, но сделала очень быстро без ошибок и без библиотек

import os
import random
import time
import sys

import termios, tty, select # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
t,_=termios.tcgetattr(0),tty.setcbreak(0) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!

# Настройки экрана
WIDTH, HEIGHT = 80, 24

# ANSI цвета
BLUE = "\033[34m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Спрайты
FISH_RIGHT = ["><(((°>", "><>", ">°))))><", "o.O"]
FISH_LEFT = ["<°)))><", "<><", "><((((°<", "O.o"]
PLANTS = ["( ", " )", "((", "))"]
CORALS = ["*#*", "&&&", "WWW"]

class Fish:
    def __init__(self):
        self.reset()

    def reset(self):
        self.direction = random.choice([-1, 1])
        self.sprite = random.choice(FISH_LEFT if self.direction == -1 else FISH_RIGHT)
        self.y = random.randint(2, HEIGHT - 5)
        self.x = WIDTH if self.direction == -1 else -len(self.sprite)
        self.speed = random.uniform(0.5, 1.5)
        self.color = random.choice([YELLOW, CYAN, MAGENTA, BOLD])

    def move(self):
        self.x += self.direction * self.speed
        if self.x < -10 or self.x > WIDTH + 10:
            self.reset()

class Bubble:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(1, WIDTH - 1)
        self.y = HEIGHT - 2
        self.speed = random.uniform(0.3, 0.8)

    def move(self):
        self.y -= self.speed
        if self.y < 1:
            self.reset()

def draw_aquarium():
    # Инициализация объектов
    fishes = [Fish() for _ in range(6)]
    bubbles = [Bubble() for _ in range(10)]
    
    # Генерация статичного дна (кораллы)
    corals_pos = [(random.randint(1, WIDTH-5), random.choice(CORALS)) for _ in range(5)]
    
    try:
        # Скрыть курсор
        sys.stdout.write("\033[?25l")
        
        tick = 0
        while True:

            if select.select([sys.stdin],[],[],0)[0]:termios.tcsetattr(0,termios.TCSADRAIN,t);break # ЭТО ВСТАВЛЕНО ВРУЧНУЮ!

            # Создаем пустой кадр (буфер)
            screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

            # Рисуем пузырьки
            for b in bubbles:
                b.move()
                if 0 <= int(b.y) < HEIGHT:
                    screen[int(b.y)][int(b.x)] = f"{CYAN}o{RESET}"

            # Рисуем траву (колышется)
            for x in range(0, WIDTH, 4):
                sway = PLANTS[0] if (tick + x) % 10 < 5 else PLANTS[1]
                for y in range(HEIGHT-4, HEIGHT-1):
                    screen[y][x] = f"{GREEN}{sway}{RESET}"

            # Рисуем кораллы
            for x_pos, sprite in corals_pos:
                for i, char in enumerate(sprite):
                    if x_pos + i < WIDTH:
                        screen[HEIGHT-2][x_pos + i] = f"{MAGENTA}{char}{RESET}"

            # Рисуем рыбок
            for f in fishes:
                f.move()
                if 0 <= int(f.x) < WIDTH - len(f.sprite):
                    for i, char in enumerate(f.sprite):
                        if 0 <= int(f.x) + i < WIDTH:
                            screen[int(f.y)][int(f.x) + i] = f"{f.color}{char}{RESET}"

            # Вывод кадра на экран
            output = "\033[H" # Перенос курсора в начало
            for row in screen:
                output += "".join(row) + "\n"
            
            sys.stdout.write(output)
            sys.stdout.flush()
            
            tick += 1
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Показать курсор обратно при выходе
        sys.stdout.write("\033[?25h")
        print("\nАквариум закрыт. Пока!")

if __name__ == "__main__":
    # Очистка экрана перед стартом
    os.system('cls' if os.name == 'nt' else 'clear')
    draw_aquarium()