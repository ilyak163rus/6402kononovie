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

def read_config(filename: str) -> dict:
    """
    Функция для чтения конфигурационного файла. 
    Принимает имя файла и возвращает словарь значений.

    Параметры:
    filename (str): Имя файла для чтения.

    Возвращает:
    dict: Словарь значений из конфигурационного файла.
    """
    config = {}
    with open(filename, 'r') as f:
        lines = f.readlines()

    for line in lines:
        key, value = line.strip().split(' = ')
        config[key] = int(value)

    return config

def calculate_and_save(n0:float, h:float, nk:float, a:float, b:float, c:float):
    """
    Функция для вычисления значения функции y = a / (1 + np.exp(-b * x + c)) 
    для заданного диапазона значений x и заданных параметров a, b, c.
    Записывает результаты в файл 'results.txt'.

    Параметры:
    n0 (float): Начальное значение диапазона x.
    h (float): Шаг изменения x.
    nk (float): Конечное значение диапазона x.
    a (float): Параметр a из конфигурации.
    b (float): Параметр b из конфигурации.
    c (float): Параметр c из конфигурации.
    """
    x = np.arange(n0, nk, h)  
    y = a / (1 + np.exp(-b * x + c))  

    with open('results.txt', 'w') as f:
        for i in range(len(x)):
            f.write(f'x={x[i]}, y={y[i]}\n')  

def main():
    """Основная функция программы."""
    # Создаем парсер
    parser = argparse.ArgumentParser(description='Обработка параметров функции.')
    parser.add_argument('--n0', type=float, help='Начальное значение диапазона x.')
    parser.add_argument('--h', type=float, help='Шаг изменения x.')
    parser.add_argument('--nk', type=float, help='Конечное значение диапазона x.')
    parser.add_argument('--a', type=float, help='Параметр a из конфигурации.')
    parser.add_argument('--b', type=float, help='Параметр b из конфигурации.')
    parser.add_argument('--c', type=float, help='Параметр c из конфигурации.')

    # Парсим аргументы
    args = parser.parse_args()

    if all(arg is not None for arg in [args.n0, args.h, args.nk, args.a, args.b, args.c]):
        calculate_and_save(args.n0, args.h, args.nk, args.a, args.b, args.c)
    else:
        config_generate()
        config = read_config('config.txt')
        n0 = config['n0']
        h = config['h']
        nk = config['nk']
        a = config['a']
        b = config['b']
        c = config['c']
        calculate_and_save(n0, h, nk, a, b, c)

if __name__ == "__main__":
    main()

