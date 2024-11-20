# Списки с сортировкой: Создайте список из 10 случайных целых чисел,
# затем отсортируйте его и выведите на экран как исходный, так и
# отсортированный список. Реализовать любой алгоритм сортировки

import random


def my_sort(lst):
    for i in range(len(lst)):
        for j in range(0, len(lst) - i - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]


lst = [random.randint(-100, 100) for i in range(10)]
my_sort(lst)
print(lst)