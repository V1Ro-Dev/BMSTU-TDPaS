# Проверка анаграммы: Напишите функцию, которая проверяет, являются ли
# две строки анаграммами друг друга.

def are_anagrams(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    return sorted(str1) == sorted(str2)


str1 = input()
str2 = input()

if are_anagrams(str1, str2):
    print('Анаграммы')
else:
    print('Не анаграммы')
