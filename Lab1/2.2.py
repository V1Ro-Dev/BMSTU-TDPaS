# Лямбда-функция: Напишите программу, которая использует лямбда-
# функцию для сортировки списка кортежей по второму элементу.

import random

tuples_list = [(random.randint(-100, 100), random.randint(-100, 100)) for _ in range(10)]

sorted_tuple_list = sorted(tuples_list, key=lambda x: x[1])

print(tuples_list)
