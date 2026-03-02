# 23 t/s, 3 min. Огромное количество попыток. Чудом при очередной иттерации получилось.
# выдает потенциально хороший базовй код, но обязательно ошибется - маловата начальная квантизация 4bit.
# из настроек выжал всё.
# выход - q

"""
Терминальный скринсейвер «Аквариум» для Linux.
Работает в любой терминальной программе, где поддерживаются 256‑цветные ANSI‑коды.

Запуск:
    $ python3 aquarium.py
Нажмите любую клавишу — скринсейвер завершит работу.
"""

import curses
import locale
import random
import time
from typing import List

# --------------------------------------------------------------
# Конфигурация -------------------------------------------------
# --------------------------------------------------------------
FPS = 20                         # кадров в секунду
BUBBLE_DENSITY = 0.02            # вероятность появления пузыря за кадр (0‑1)
FISH_SPAWN_CHANCE = 0.02         # шанс появления новой рыбки за кадр
MAX_FISH = 12                    # ограничитель количества рыбок одновременно
PLANT_DENSITY = 0.08             # плотность травы (0‑1)
CORAL_DENSITY = 0.02             # плотность кораллов (0‑1)

# Цветовые пары (нумерация начинается с 1)
COLOR_WATER = 1      # синий фон
COLOR_BUBBLE = 2     # светло‑голубой
COLOR_FISH = 3       # желтый
COLOR_PLANT = 4      # зелёный
COLOR_CORAL = 5      # красный

# --------------------------------------------------------------
# Описание объектов ---------------------------------------------
# --------------------------------------------------------------

class Bubble:
    """Пузырёк, поднимающийся вверх."""
    def __init__(self, x: int, y: int, speed: float):
        self.x = x
        self.y = y
        self.speed = speed          # ячеек в секунду
        self._phase = 0.0           # для дробного перемещения

    def update(self, dt: float):
        self._phase += self.speed * dt
        if self._phase >= 1.0:
            self.y -= int(self._phase)
            self._phase -= int(self._phase)

    def draw(self, scr):
        max_y, max_x = scr.getmaxyx()
        if 0 <= self.y < max_y and 0 <= self.x < max_x - 1:   # -1 – «запрещённый» столбец
            scr.addstr(self.y, self.x, 'o', curses.color_pair(COLOR_BUBBLE))


class Fish:
    """Простая рыбка, движущаяся в одну сторону."""
    SHAPES = {
        True:  ("<°)))><", "<°)))><"),   # вправо
        False: (">)))))>", "}>)))))>")   # влево (отражённые)
    }

    def __init__(self, x: float, y: float, direction: bool, speed: float):
        self.x = x
        self.y = y
        self.dir = direction          # True → вправо, False → влево
        self.speed = speed
        self._frame = 0

    def update(self, dt: float, max_x: int):
        self.x += (self.speed if self.dir else -self.speed) * dt
        self._frame = (self._frame + 1) % 2

        # «Телепортация» в начало, когда рыбка полностью ушла за границу
        if self.dir and self.x > max_x:
            self.x = -len(self.SHAPES[True][0])
        elif not self.dir and self.x < -len(self.SHAPES[False][0]):
            self.x = max_x

    def draw(self, scr):
        shape = self.SHAPES[self.dir][self._frame]
        max_y, max_x = scr.getmaxyx()
        for i, ch in enumerate(shape):
            xx = int(self.x) + i
            if 0 <= xx < max_x - 1 and 0 <= int(self.y) < max_y:
                scr.addstr(int(self.y), xx, ch, curses.color_pair(COLOR_FISH))


class Plant:
    """Трава на дне."""
    def __init__(self, x: int, height: int):
        self.x = x
        self.height = height

    def draw(self, scr):
        max_y, max_x = scr.getmaxyx()
        for i in range(self.height):
            y = max_y - 2 - i          # -1 — строка дна, -2 — первая «водяная» строка
            if 0 <= y < max_y:
                scr.addstr(y, self.x, '|', curses.color_pair(COLOR_PLANT))


class Coral:
    """Кораллы – статичный набор символов."""
    SHAPES = ["@", "#", "%", "$"]

    def __init__(self, x: int, width: int):
        self.x = x
        self.width = width
        self.shape = random.choice(self.SHAPES)

    def draw(self, scr):
        max_y, max_x = scr.getmaxyx()
        y = max_y - 1
        for i in range(self.width):
            xx = self.x + i
            if 0 <= xx < max_x - 1:          # избегаем правого края
                scr.addstr(y, xx, self.shape, curses.color_pair(COLOR_CORAL))


# --------------------------------------------------------------
# Вспомогательные функции ---------------------------------------
# --------------------------------------------------------------

def init_colors():
    """Инициализация цветовых пар."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_WATER, curses.COLOR_BLUE, -1)
    curses.init_pair(COLOR_BUBBLE, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_FISH, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_PLANT, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_CORAL, curses.COLOR_RED, -1)


def init_background(scr):
    """Устанавливает единый фон (синий) для всего окна."""
    scr.bkgd(' ', curses.color_pair(COLOR_WATER))
    scr.clear()                       # заполняет всё текущим фоном


def spawn_bubble(max_x: int, max_y: int) -> Bubble:
    """Создаёт пузырёк у дна в случайной горизонтали."""
    x = random.randint(0, max_x - 2)   # -2, чтобы не попасть в запрещённый столбец
    y = max_y - 2                     # -1 – строка дна, -2 – первая «водяная» строка
    speed = random.uniform(0.5, 2.0)
    return Bubble(x, y, speed)


def spawn_fish(max_x: int, max_y: int) -> Fish:
    """Создаёт новую рыбку в случайном месте."""
    direction = random.choice([True, False])
    y = random.randint(2, max_y - 5)
    speed = random.uniform(5.0, 12.0)
    if direction:                     # слева → справа
        x = -10
    else:                             # справа → слева
        x = max_x + 10
    return Fish(x, y, direction, speed)


def generate_plant_line(max_x: int) -> List[Plant]:
    """Генерирует статичную растительность у дна."""
    plants = []
    for x in range(max_x - 1):          # -1, чтобы не писать в крайний столбец
        if random.random() < PLANT_DENSITY:
            height = random.randint(1, 4)
            plants.append(Plant(x, height))
    return plants


def generate_coral_line(max_x: int) -> List[Coral]:
    """Генерирует несколько кусочков кораллов."""
    corals = []
    for x in range(0, max_x - 1, 7):
        if random.random() < CORAL_DENSITY:
            w = random.randint(2, 5)
            corals.append(Coral(x, w))
    return corals


# --------------------------------------------------------------
# Основной цикл ------------------------------------------------
# --------------------------------------------------------------

def main(stdscr):
    # Обеспечиваем корректный вывод Unicode‑символов
    locale.setlocale(locale.LC_ALL, '')

    curses.curs_set(0)          # скрыть курсор
    stdscr.nodelay(True)        # не ждать ввода
    stdscr.timeout(0)

    init_colors()
    init_background(stdscr)     # фон задаётся один раз

    max_y, max_x = stdscr.getmaxyx()

    # Защита от слишком маленького окна
    if max_y < 10 or max_x < 30:
        stdscr.addstr(0, 0, "Окно слишком мало – увеличьте его размер.", curses.A_BOLD)
        stdscr.refresh()
        time.sleep(3)
        return

    # Списки объектов
    bubbles: List[Bubble] = []
    fish: List[Fish] = []
    plants = generate_plant_line(max_x)
    corals = generate_coral_line(max_x)

    last_time = time.time()

    while True:
        # --------------------------------------------------
        # 1. Выход по любой клавише
        # --------------------------------------------------
        if stdscr.getch() != -1:
            break

        # --------------------------------------------------
        # 2. Дельта‑время
        # --------------------------------------------------
        now = time.time()
        dt = now - last_time
        last_time = now

        # --------------------------------------------------
        # 3. Обновляем объекты
        # --------------------------------------------------
        # Пузырьки
        for b in bubbles:
            b.update(dt)
        bubbles = [b for b in bubbles if b.y >= 0]   # удаляем вышедшие наверх

        if random.random() < BUBBLE_DENSITY * max_x * max_y:
            bubbles.append(spawn_bubble(max_x, max_y))

        # Рыбки
        for f in fish:
            f.update(dt, max_x)
        if len(fish) < MAX_FISH and random.random() < FISH_SPAWN_CHANCE:
            fish.append(spawn_fish(max_x, max_y))

        # --------------------------------------------------
        # 4. Рендеринг
        # --------------------------------------------------
        stdscr.erase()            # стираем экран, но фон остаётся (установлен в init_background)

        # Дно – линия «_». Пропускаем правый столбец, чтобы не писать в угол.
        for x in range(max_x - 1):
            stdscr.addstr(max_y - 1, x, '_', curses.color_pair(COLOR_WATER))

        # Статические элементы
        for c in corals:
            c.draw(stdscr)
        for p in plants:
            p.draw(stdscr)

        # Движущиеся элементы
        for b in bubbles:
            b.draw(stdscr)
        for f in fish:
            f.draw(stdscr)

        stdscr.refresh()
        time.sleep(max(0, 1.0 / FPS))


# --------------------------------------------------------------
# Точка входа
# --------------------------------------------------------------
if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        # Graceful exit on Ctrl‑C
        pass
