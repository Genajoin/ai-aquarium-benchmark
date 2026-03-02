# 25 t/s, 2 min. ошибка. исправлял якобы отсутствие поддержки unicode. 
# пришлось намекнуть на проверку границ. сработало.

import curses
import random

def main(stdscr):
    # Настройка curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(50)
    curses.start_color()
    curses.use_default_colors()

    # Инициализация цветов
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)

    # Получаем размеры экрана
    height, width = stdscr.getmaxyx()
    
    # Минимальный размер для отображения
    if height < 10 or width < 20:
        stdscr.addstr(0, 0, "Окно слишком маленькое!", curses.color_pair(5))
        stdscr.refresh()
        return

    # Объекты
    bubbles = []
    fishes = []
    grass = []
    corals = []

    # --- Инициализация ---
    for _ in range(15):
        bubbles.append({
            'x': random.randint(0, width - 1),
            'y': random.randint(0, height - 1),
            'speed': random.randint(1, 3),
            'char': random.choice(['o', 'O', '.'])
        })

    fish_chars = ['>D', 'oD', '<D', 'D<', '><']
    for _ in range(5):
        fishes.append({
            'x': random.randint(0, width - 2),
            'y': random.randint(2, height - 4),
            'dir': random.choice([1, -1]),
            'char': random.choice(fish_chars),
            'color': curses.color_pair(3)
        })

    grass_chars = ['|', '/', '\\', '-', '~']
    for x in range(0, width, 3):
        grass.append({
            'x': x,
            'height': random.randint(2, 6),
            'char': random.choice(grass_chars)
        })

    coral_chars = ['#', '@', '+', 'X']
    for x in range(0, width, 8):
        if random.random() > 0.5:
            corals.append({
                'x': x,
                'char': random.choice(coral_chars)
            })

    frame = 0
    while True:
        key = stdscr.getch()
        if key == ord('q') or key == 27:
            break

        stdscr.clear()

        # Обновляем размеры (на случай изменения окна)
        height, width = stdscr.getmaxyx()

        # 1. Фон
        if frame % 5 == 0:
            for _ in range(5):
                bx = random.randint(0, width - 1)
                by = random.randint(0, height - 1)
                try:
                    stdscr.addch(by, bx, '.', curses.color_pair(1))
                except:
                    pass

        # 2. Дно
        for x in range(width):
            try:
                stdscr.addch(height - 1, x, '-', curses.color_pair(6))
            except:
                pass

        # 3. Кораллы
        for coral in corals:
            try:
                stdscr.addch(height - 2, coral['x'], coral['char'], curses.color_pair(5))
            except:
                pass

        # 4. Трава
        for g in grass:
            for i in range(1, g['height'] + 1):
                draw_x = g['x']
                if i > g['height'] // 2:
                    draw_x += random.randint(-1, 1)
                
                draw_y = height - 1 - i
                if 0 <= draw_x < width and 0 <= draw_y < height:
                    try:
                        stdscr.addch(draw_y, draw_x, g['char'], curses.color_pair(4))
                    except:
                        pass

        # 5. Рыбки
        for fish in fishes:
            char_to_draw = fish['char'] if fish['dir'] == 1 else fish['char'][::-1]
            if 0 <= fish['x'] < width and 0 <= fish['y'] < height:
                try:
                    stdscr.addstr(fish['y'], fish['x'], char_to_draw, fish['color'])
                except:
                    pass

            fish['x'] += fish['dir']

            if fish['x'] > width - 2 or fish['x'] < 0:
                fish['dir'] *= -1

            if random.random() < 0.01:
                fish['y'] += random.choice([-1, 1])
                fish['y'] = max(0, min(height - 4, fish['y']))

        # 6. Пузырьки
        for b in bubbles:
            if 0 <= b['x'] < width and 0 <= b['y'] < height:
                try:
                    stdscr.addch(b['y'], b['x'], b['char'], curses.color_pair(2))
                except:
                    pass

            b['y'] -= b['speed']
            if random.random() < 0.1:
                b['x'] += random.choice([-1, 1])

            if b['y'] < 0:
                b['y'] = height - 2
                b['x'] = random.randint(0, width - 1)
                b['speed'] = random.randint(1, 3)

        frame += 1
        stdscr.refresh()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Попробуйте увеличить окно терминала или изменить кодировку.")
