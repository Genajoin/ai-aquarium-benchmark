#!/usr/bin/env python3

import curses
import random
import time

import sys, termios, tty, select # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!
t,_=termios.tcgetattr(0),tty.setcbreak(0) # ЭТО ДОБАВЛЕНО ВРУЧНУЮ!

class Bubble:
    def __init__(self, y, size=1, speed=1):
        self.y = y
        self.size = size
        self.speed = speed
        self.direction = random.choice([-1, 1])

    def move(self):
        self.y += self.speed * self.direction
        if self.y <= 0 or self.y >= 18:  # Размер экрана 20 строк (0-19)
            self.speed *= -1

    def draw(self, screen):
        # Добавляем пузырьки как отдельные символы
        for i in range(self.size):
            screen.addch(self.y, 10 + i, 'O')  # 10 - столбец, 10+i - координаты Y

class Plant:
    def __init__(self, y, growth_rate=0.05):
        self.y = y
        self.growth_rate = growth_rate
        self.height = 5

    def grow(self):
        self.height += self.growth_rate
        if self.height > 20:
            self.height = 5

    def draw(self, screen):
        # Рисуем траву как строку '#' длиной self.height
        for i in range(int(self.height)):
            screen.addch(self.y, 30 + i, '#')

class Fish:
    def __init__(self, y, speed=2):
        self.y = y
        self.speed = speed
        self.direction = 1

    def move(self):
        self.y += self.speed * self.direction
        if self.y <= 0 or self.y >= 18:
            self.direction *= -1

    def draw(self, screen):
        # Рисуем рыбу как 'F'
        screen.addch(self.y, 40, 'F')

class Coral:
    def __init__(self, y, size=3):
        self.y = y
        self.size = size

    def draw(self, screen):
        # Кораллы — строка 'C' размера size
        for i in range(self.size):
            screen.addch(self.y, 50 + i, 'C')

def main(stdscr):
    curses.curs_set(0)  # Скрыть курсор
    screen = stdscr
    screen.nodelay(True)  # Не блокировать на ввод
    screen.timeout(100)  # Обновлять каждые 100 мс

    # Инициализация объектов
    bubbles = [Bubble(random.randint(2, 17)) for _ in range(5)]  # 5 пузырька
    plants = [Plant(random.randint(2, 17)) for _ in range(3)]  # 3 растения
    fish = [Fish(random.randint(2, 17)) for _ in range(2)]  # 2 рыбы
    corals = [Coral(random.randint(2, 17)) for _ in range(2)]  # 2 кораллы

    while True:
        screen.clear()
        if select.select([sys.stdin],[],[],0)[0]:termios.tcsetattr(0,termios.TCSADRAIN,t);break # ЭТО ВСТАВЛЕНО ВРУЧНУЮ!
        
        # Фон аквариума
        screen.addstr(0, 0, "+-----------------------------+")
        screen.addstr(21, 0, "|   Aquarium  |")
        screen.addstr(23, 0, "+-----------------------------+")
        
        # Двигаем и рисуем объекты
        for bubble in bubbles:
            bubble.move()
            bubble.draw(screen)
        
        for plant in plants:
            plant.grow()
            plant.draw(screen)
        
        for fish_obj in fish:
            fish_obj.move()
            fish_obj.draw(screen)
        
        for coral_obj in corals:
            coral_obj.draw(screen)
        
        # Добавляем новые объекты с небольшой вероятностью
        if random.random() < 0.1:
            bubbles.append(Bubble(random.randint(2, 17)))
        if random.random() < 0.05:
            plants.append(Plant(random.randint(2, 17)))
        if random.random() < 0.05:
            corals.append(Coral(random.randint(2, 17)))
        
        screen.refresh()
        time.sleep(0.05)  # Снижаем скорость

curses.wrapper(main)
