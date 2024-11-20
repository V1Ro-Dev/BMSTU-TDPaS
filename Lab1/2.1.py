# Использование map(): Напишите программу, которая использует функцию
# map() для возведения каждой цифры в списке чисел в квадрат.


numbers = [i for i in range(1, 10)]


def square(num):
    return num ** 2


ans = list(map(square, numbers))


print(*ans)
