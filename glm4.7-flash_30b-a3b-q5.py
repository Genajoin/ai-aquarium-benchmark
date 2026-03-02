#!/usr/bin/env python3
# 128 t/s, слишком много думает, много попыток правки и плачевный результат. 
# q8 дает 24 t/s, но результат такой же. куча ошибок и не видит их реальной причины.

import os
import random
import time
import math
import sys

import termios, tty, select # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
t,_=termios.tcgetattr(0),tty.setcbreak(0) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!

# --- Настройки ---
WIDTH = 80
HEIGHT = 24
DELAY = 0.1  # Немного замедлил для плавности

def clear_screen():
    # Используем чистую команду переноса курсора для плавности
    sys.stdout.write('\033[H') 
    sys.stdout.flush()

# --- Классы ---

class Fish:
    def __init__(self):
        self.reset()

    def reset(self):
        self.y = random.randint(2, HEIGHT - 4)
        self.x = random.randint(0, WIDTH)
        self.speed = random.choice([-0.5, 0.5, -1.0, 1.0])
        if self.speed == 0: self.speed = 0.5
        self.type = random.randint(1, 3) 
        self.color = random.choice(['\033[31m', '\033[33m', '\033[92m', '\033[95m', '\033[96m'])
        self.tail_wag = 0 

    def move(self):
        self.x += self.speed
        self.tail_wag += 0.2
        
        if self.x > WIDTH - 2:
            self.speed = -abs(self.speed)
        elif self.x < 2:
            self.speed = abs(self.speed)

    def draw(self):
        # Правильное выравнивание рыбы по центру всей строки
        fish_str = f"{self.color}((>_<))\033[0m" if self.type == 1 else \
                   f"{self.color}><((*>\033[0m" if self.type == 2 else \
                   f"{self.color}^_~\033[0m"
        
        return f"{fish_str:^{WIDTH}}"

class Bubble:
    def __init__(self):
        self.reset()

    def reset(self):
        self.y = HEIGHT + 1
        self.x = random.randint(0, WIDTH - 1)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.choice(['O', 'o', '°'])

    def update(self):
        self.y -= self.speed
        self.x += random.choice([-0.5, 0, 0.5])
        self.x = round(self.x)
        self.y = round(self.y)

        if self.y < 1:
            self.reset()

    def draw(self):
        # Рисуем: отступ слева + пузырек + пробелы до конца
        # Это гарантирует, что строка ровно 80 символов
        return f"{' ' * self.x}{self.size}{' ' * (WIDTH - self.x - 1)}"

class Seaweed:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(4, 10)
        self.color = '\033[32m' 
        self.offset = random.random() * 6.28

    def draw(self, t):
        grass = ""
        # Рисуем траву снизу вверх
        for i in range(self.height):
            line = ""
            # Левая часть
            if i == self.height - 1:
                line += "/"
            else:
                line += " "
            # Центр
            line += "|"
            # Правая часть
            if i == self.height - 1:
                line += "\\"
            else:
                line += " "
            grass += line
        
        # Добавляем отступы слева, чтобы трава встала ровно на свою координату x
        # И добавляем пробелы справа, чтобы дно было ровным
        padding = ' ' * self.x
        return padding + grass

def draw_background():
    bg = ""
    for y in range(HEIGHT):
        if y == HEIGHT - 1: # Песок на дне
            row = " " * WIDTH
        elif y == 0: # Верх воды
            row = "░" * WIDTH
        elif y == 1: 
            row = "▒" * WIDTH
        elif y == HEIGHT - 2: # Граница воды
            row = "▓" * WIDTH
        else:
            row = "█" * WIDTH
        bg += row + "\n"
    return bg

def main():
    fishes = [Fish() for _ in range(5)]
    bubbles = [Bubble() for _ in range(20)]
    seaweeds = [Seaweed(random.randint(0, WIDTH)) for _ in range(8)]
    
    # Установка цвета терминала (синий фон)
    try:
        os.system('color 0B') 
    except:
        pass

    try:
        while True:
            clear_screen() # Плавное обновление вместо cls
            if select.select([sys.stdin],[],[],0)[0]:termios.tcsetattr(0,termios.TCSADRAIN,t);break # ЭТО ВСТАВЛЕНО ВРУЧНУЮ!
            
            print(draw_background())
            
            # 1. Рисуем траву (снизу вверх)
            for weed in seaweeds:
                print(weed.draw(time.time()))
            
            # 2. Рисуем пузырьки (они над травой, но под рыбами)
            for b in bubbles:
                b.update()
                print(b.draw())
            
            # 3. Рисуем рыб (поверх всего)
            for f in fishes:
                f.move()
                print(f.draw())
                
            time.sleep(DELAY)
            
    except KeyboardInterrupt:
        clear_screen()
        print("Аквариум выключен.")

if __name__ == "__main__":
    main()
