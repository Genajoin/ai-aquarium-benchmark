#!/bin/bash

# Находим все Python-файлы в текущей директории и сортируем их
for file in *.py; do
    # Проверяем, существует ли файл (на случай, если нет .py файлов)
    [ -e "$file" ] || continue

    # Меняем заголовок терминала
    printf '\033]0;%s\007' "$file"

    echo "======================================"
    echo "Файл: $file"
    echo "======================================"
    head -n 5 "$file"
    echo "======================================"
    echo "Enter - запустить, ESC - пропустить"

    # Ждем только Enter или ESC
    while true; do
        IFS= read -n 1 -s key

        # Если ESC - пропускаем файл
        if [[ "$key" == $'\e' ]]; then
            echo ""
            echo ">>> Пропущено: $file <<<"
            echo ""
            continue 2
        fi

        # Если Enter (пустая строка) - запускаем файл
        if [[ -z "$key" ]]; then
            break
        fi

        # Игнорируем другие клавиши
    done

    python3 "$file"

    echo ""
    echo "--- Завершено: $file ---"
    echo ""
done

echo "Все файлы выполнены."
