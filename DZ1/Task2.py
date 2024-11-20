import heapq
from typing import Dict, List


class Node:  #нода двоичного дерева
    def __init__(self, char: str, freq: int) -> None:
        self.char = char  #символ
        self.freq = freq  #частота появления символа
        self.left = None  #левый потомок
        self.right = None  #правый потомок

    #оператор сравнения, чтобы можно было выполнить метод heapify
    def __lt__(self, other):
        return self.freq < other.freq


def countFreq(textToEncode: str) -> Dict[str, int]: #функция подсчета частоты встречаний различных символов
    freqDict = {}  #создаем словарь ключ - уникальный символ, значение - количество этого символа в тексте
    for char in textToEncode:  #итерируемся по тексту
        if char in freqDict:
            freqDict[char] += 1  #если ключ уже есть, то значение +1
        else:
            freqDict[char] = 1   #иначе значение = 1
    return freqDict


def createPriorityQueue(freqDict: Dict[str, int]) -> List[Node]: #функция создания приоритетной очереди
    priorityQueue = []  #пустой список для хранения нод
    for char, freq in freqDict.items(): #итерируемся по словарю с частотой встречаний символов
        priorityQueue.append(Node(char, freq))  #добавляем в список ноду
    heapq.heapify(priorityQueue) #вызываем heapify, чтобы создать приоритетную очередь
    return priorityQueue


def buildHuffmanTree(heap: List[Node]) -> Node: #создаем двоичное дерево хаффмана
    while len(heap) > 1:  #пока в очереди больше 1 элемента
        l = heapq.heappop(heap)  #достаем ноду с наименьшей частотой
        r = heapq.heappop(heap)  #достаем вторую ноду с наименьшей частотой

        merged = Node(None, l.freq + r.freq)  #создаем смерженную ноду
        merged.left = l  #левый потомок
        merged.right = r  #правый потомок

        heapq.heappush(heap, merged) #пушим обратно в очередь

    return heap[0]  #возвращаем корень нашего дерева хаффмана


def buildHuffmanCodes(root: Node, current_code="", codes=None) -> Dict[str, int]: #функция составления кодов хаффмана
    if codes is None: #передаем изначально codes = None, т.к есть прикол с mutable defaults)
        codes = {}

    if root is None: #если доходим до листа дерева, то возвращаем его
        return codes

    if root.char is not None:
        codes[root.char] = current_code

    buildHuffmanCodes(root.left, current_code + "0", codes)  #далее рекурсивно обходим дерево, сохраняя 0 для левого поддерева и 1 для правого
    buildHuffmanCodes(root.right, current_code + "1", codes)

    return codes


def encode(text: str, huffmanCodes: Dict[str, int]) -> str:
    return ''.join([huffmanCodes[char] for char in text])  #генератором списка кодируем с помощью кодов хаффмана наш текст и преобразовываем наш список в строку


def solution():
    textToEncode = ("Множество целых чисел, представимых в памяти ЭВМ, ограничено. Диапазон значений зависит от размера области памяти, используемой для размещения чисел.")
    freqDict = countFreq(textToEncode)  #словарь с частотой появления символов
    priorityQueue = createPriorityQueue(freqDict)  #приоритетная очередь с нодами
    treeNode = buildHuffmanTree(priorityQueue)    #дерево хаффмана
    huffmanCodes = buildHuffmanCodes(treeNode)    #коды хаффмана
    encodedText = encode(textToEncode, huffmanCodes)  #полученный закодированный текст
    print("Коды Хаффмана:", huffmanCodes)
    print("Закодированное сообщение:", encodedText)


def main():      #main функция
    solution()


if __name__ == '__main__':   #вызов мейн функции
    main()
