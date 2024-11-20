from typing import Dict, List  #подключаем модуль typing для аннотации типов
from decimal import Decimal, getcontext

getcontext().prec = 300  #количество занков после запятой


def countProbability(text: str) -> Dict[str, Decimal]:  #функция для подсчета частоты встречаемых символов
    textSize = len(text)  #длина сообщения, которое нужно закодировать
    probability = {}  #словарь для подсчета частоты встречаемых символов (ключ - символ, значение - количество данного символа в тексте)
    for char in text:  #цикл, который итерируется по сообщению
        if char in probability:  #если ключ char есть в словаре, то +1 к его значению
            probability[char] += 1
        else:
            probability[char] = 1  #иначе значение ключа = 1
    probability = {key: Decimal(value) / Decimal(textSize) for key, value in probability.items()}  #насчитываем частоту появления каждого уникального символа
    return probability  #возвращаем итоговый словарь


def buildSegmentDict(probability: Dict[str, Decimal]) -> Dict[str, List[Decimal]]:  #функция для составления "рабочих" полуинтервалов для каждого символа, где длина полуинтервала = частоте появления символа
    segmentDict = {}  #словарь для составления полуинтервалов (ключ - символ, значение - список, где 0-ой элемент - левая граница, а 1-ый элемент - правая граница
    left = Decimal(0) #левая граница - 0
    for char in probability.keys():  #итерируемся по уникальным символам и составлям "рабочий" полуинтервал для каждого символа
        segmentDict[char] = [left, left + probability[char]]
        left = left + probability[char]
    return segmentDict  #возвращаем итоговый словарь


def encode(text: str, segmentDict: Dict[str, List[Decimal]]) -> Decimal:  #функция для кодирования текста в число
    l, r = 0, 1  #левая граница полуинтервала - 0, правая - 1
    for char in text:  #итерируемся по каждому символу текста и пересчитываем левую и правую границу полуинтервала
        newRight = l + (r - l) * segmentDict[char][1]
        newLeft = l + (r - l) * segmentDict[char][0]
        l = newLeft
        r = newRight
    return (l + r) / 2  #в результате наш текст - любое число из полуинтервала [l, r), для лучшей точности возьмем середину


def decode(segmentDict: Dict[str, List[Decimal]], code: Decimal) -> str:  #функция для декодирования числа в текст
    ans = ""  #наш текст, который должен получиться, лежит в переменной ans
    while True:   #запускаем бесконечный цикл, из которого мы выйдем только тогда, когда встретим остановочный символ
        for char, segment in segmentDict.items():  #итерируемся по словарю с "рабочими" полуинтервалами
            if char == "ඞ": #если встретили, то возвращаем ответ
                return ans
            if segment[0] <= code < segment[1]:  # если код(число - которое получили в процессе кодирования текста) лежит в полуинтервале [l, r), то это нужный нам символ
                ans += char  #кладем символ в ответ
                code = (code - segment[0]) / (segment[1] - segment[0])  #пересчитываем код для дальнейшего декодирования
                break


def solution():
    with open("in.txt", 'r', encoding='utf-8') as file:
        textToEncode = file.read()
    probabilityDict = countProbability(textToEncode)  #словарь частот встречаемых символов
    segmentDict = buildSegmentDict(probabilityDict)  #словарь с "рабочими" полуинтервалами
    encodedResult = encode(textToEncode, segmentDict)  #закодированный текст
    print("Encoded text:", encodedResult)  #вывод числа
    decodedResult = decode(segmentDict, encodedResult)  #декодированное число(текст)
    print(decodedResult)  #вывод текста


def main():  #функция main для запуска функции решения
    solution()


if __name__ == '__main__':  #запуск функции main
    main()
