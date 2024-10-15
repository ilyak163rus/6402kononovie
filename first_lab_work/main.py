import random
import numpy as np
import argparse

def config_generate():
    """
    Функция для генерации конфигурационного файла с рандомными числами.
    Обеспечивает, что начальное значение n0 меньше конечного nk и шаг h положителен.
    Записывает значения в файл 'config.txt'.
    """
    n0 = random.randint(-100, 100)
    nk = random.randint(n0 + 1, n0 + 100)  # nk всегда больше n0
    h = random.randint(1, 10)  # шаг h всегда положителен
    a = random.randint(-10, 10)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)

    with open("config.txt", "w") as file:
        file.write("n0 = " + str(n0) + '\n')
        file.write("h = " + str(h) + '\n')
        file.write("nk = " + str(nk) + '\n')
        file.write("a = " + str(a) + '\n')
        file.write("b = " + str(b) + '\n')
        file.write("c = " + str(c))

def read_config(filename):
    """
    Функция для чтения конфигурационного файла. 
    Принимает имя файла и возвращает кортеж значений.

    Параметры:
    filename (str): Имя файла для чтения.

    Возвращает:
    tuple: Кортеж значений из конфигурационного файла.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    values = []
    for line in lines:
        key, value = line.strip().split(' = ')
        values.append(int(value))

    return tuple(values)

def calculate_and_save(n0, h, nk, a, b, c):
    """
    Функция для вычисления значения функции y = a / (1 + np.exp(-b * x + c)) 
    для заданного диапазона значений x и заданных параметров a, b, c.
    Записывает результаты в файл 'results.txt'.

    Параметры:
    n0 (int): Начальное значение диапазона x.
    h (int): Шаг изменения x.
    nk (int): Конечное значение диапазона x.
    a (int): Параметр a из конфигурации.
    b (int): Параметр b из конфигурации.
    c (int): Параметр c из конфигурации.
    """
    x = np.arange(n0, nk, h)  # создаем массив значений x с заданным шагом
    y = a / (1 + np.exp(-b * x + c))  # вычисляем значение функции y для каждого x

    with open('results.txt', 'w') as f:
        for i in range(len(x)):
            f.write(f'x={x[i]}, y={y[i]}\n')  # записываем результаты в файл

def main():
    """Основная функция программы."""
    # Создаем парсер
    parser = argparse.ArgumentParser(description='Обработка параметров функции.')
    parser.add_argument('--n0', type=int, help='Начальное значение диапазона x.')
    parser.add_argument('--h', type=int, help='Шаг изменения x.')
    parser.add_argument('--nk', type=int, help='Конечное значение диапазона x.')
    parser.add_argument('--a', type=int, help='Параметр a из конфигурации.')
    parser.add_argument('--b', type=int, help='Параметр b из конфигурации.')
    parser.add_argument('--c', type=int, help='Параметр c из конфигурации.')

    # Парсим аргументы
    args = parser.parse_args()

    if all(arg is not None for arg in [args.n0, args.h, args.nk, args.a, args.b, args.c]):
        calculate_and_save(args.n0, args.h, args.nk, args.a, args.b, args.c)
    else:
        config_generate()
        n0, h, nk, a, b, c = read_config('config.txt')
        calculate_and_save(n0, h, nk, a, b, c)

if __name__ == "__main__":
    main()
