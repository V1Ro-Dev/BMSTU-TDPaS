from typing import List
import random
import time
import threading
from queue import PriorityQueue
from datetime import datetime


class Task:  # класс задачи
    STATUS_RUNNING = "Running"
    STATUS_READY = "Ready"
    STATUS_BLOCKED = "Blocked"
    STATUS_DONE = "Done"

    def __init__(self, task_id: int, priority: int, operations: int, size: int):
        self.id = task_id  # id задачи
        self.priority = priority  # приоритет задачи
        self.operations = operations  # количество операций
        self.size_bits = size  # размер задачи в битах
        self.queued_time = None # время, в течение которого
        self.status = Task.STATUS_READY  # начальный статус задачи

    def __lt__(self, other: 'Task') -> bool:  # определяем оператор < для сравнения задач по приоритету
        return self.priority > other.priority  # чем меньше приоритет, тем важнее задача

    def __str__(self):
        return f"Task(id={self.id}, priority={self.priority}, size={self.size_bits}, operations={self.operations}, status={self.status})"

    @staticmethod
    def generate_random_task(task_id: int, max_task_size_bits: int) -> 'Task':
        task_size_bits = random.randint(1, max_task_size_bits)  # размер задачи в битах
        operations_needed = random.randint(1, 100)  # количество операций для выполнения задачи
        priority = random.randint(1, 10)  # приоритет задачи
        return Task(
            task_id=task_id,
            priority=priority,
            operations=operations_needed,
            size=task_size_bits
        )


class EthFrame:  # Ethernet Frame
    def __init__(self, frame_id: int, tasks: List[Task], bandwidth: int):
        self.frame_id = frame_id
        self.tasks = tasks
        self.total_size = sum(task.size_bits for task in tasks)

    def __str__(self):
        task_ids = [task.id for task in self.tasks]
        return f"Кадр с id {self.frame_id}, c количеством задач {len(task_ids)}, и размером {self.total_size} бит успешно созда н"


class IEEE8023ba:  # реализация стандарта IEEE P802.3ba
    def __init__(self, max_frame_size_bits: int, bandwidth: int):
        self.max_frame_size_bits = max_frame_size_bits  # максимальный размер кадра
        self.bandwidth = bandwidth  # пропускная способность канала

    def group_tasks_into_frames(self, tasks: List[Task]) -> List[EthFrame]:  # метод, отвечающий за группировку задач в кадры
        frames = []
        frame_id = 0
        current_frame_tasks = []
        current_frame_size = 0

        for task in tasks:
            if current_frame_size + task.size_bits <= self.max_frame_size_bits:  #если размер кадры + размер текущей задачи меньше, чем максимальный размер кадра, то добавляем задачу в текузий кадр
                current_frame_tasks.append(task)
                current_frame_size += task.size_bits
            else:  #иначе создаем новый кадр и добавляем туда задачу
                frames.append(EthFrame(frame_id, current_frame_tasks, self.bandwidth))
                frame_id += 1
                current_frame_tasks = [task]
                current_frame_size = task.size_bits

        if current_frame_tasks:  # добавляем оставшиеся задачи в последний кадр
            frames.append(EthFrame(frame_id, current_frame_tasks, self.bandwidth))

        for frame in frames:
            print(frame)

        print(f"Сформировано {len(frames)} кадров из {len(tasks)} задач.")
        return frames


class Memory:  # класс для эмуляции памяти
    def __init__(self):
        self.ram = {}

    def add_task(self, address: int, task: Task):
        self.ram[address] = task

    def del_task(self, address: int):
        del self.ram[address]

    def get_task(self, address: int) -> Task:
        return self.ram.get(address)

    def clear_memory(self):
        self.ram = {}

    def __str__(self):
        return f"Количество задач в памяти: {len(self.ram)}"


class CoreProcessor:  # ядро процессора
    def __init__(self, core_id: int, processor_id: int):
        self.core_id = core_id
        self.processor_id = processor_id
        self.is_busy = False

    def execute_task(self, task: Task, cpu_clock_hz: int):
        self.is_busy = True
        task.status = Task.STATUS_RUNNING  #меняем статус на "running"
        start_time = datetime.now()
        print(f"Processor {self.processor_id} Core {self.core_id} начал выполнение задачи {task.id} "
              f"(приоритет: {task.priority}, статус: {task.status}).")

        execution_time = task.operations / cpu_clock_hz  # время выполнения = количество операций / тактовая частота
        time.sleep(execution_time) #эмуляция выполнения задачи

        queued_time = (start_time - task.queued_time).total_seconds()  #время нахождения в очереди = время после выполнения - время, когда задача была добавлена в очередь
        task.status = Task.STATUS_DONE  # обновляем статус после выполнения
        print(f"Processor {self.processor_id} Core {self.core_id} завершил задачу {task.id} "
              f"за {execution_time:} секунд. Время в очереди: {queued_time:} секунд. Статус задачи: {task.status}.")
        self.is_busy = False


class Processor:  # процессор с несколькими ядрами
    def __init__(self, processor_id: int, num_cores: int):
        self.processor_id = processor_id  # id процессора
        self.cores = [CoreProcessor(i, processor_id) for i in range(num_cores)]  # ядра процессора

    def assign_task(self, task: Task, cpu_clock_hz: int):
        for core in self.cores:
            if not core.is_busy:  # если процессор не занят, начинаем исполнение задачи
                threading.Thread(target=core.execute_task, args=(task, cpu_clock_hz)).start()
                return True
        return False  # все ядра заняты


class RTOS:  # планировщик задач
    def __init__(self, processors: List[Processor], memory: Memory, ieee: IEEE8023ba, cpu_clock_hz: int):
        self.processors = processors  # список процессоров
        self.task_queue = PriorityQueue()  # очередь задач
        self.memory = memory  # память, в которой хранятся задачи
        self.ieee = ieee  # стандарт передачи
        self.cpu_clock_hz = cpu_clock_hz  # тактовая частота процессора

    def load_tasks_from_memory(self, data_bandwidth):
        tasks = list(self.memory.ram.values())  # загружаем задачи из памяти
        self.memory.clear_memory()  # очищаем память
        frames = self.ieee.group_tasks_into_frames(tasks)  # группируем задачи по кадрам
        transmission_size = 0
        for frame in frames:
            print(f"Кадр {frame.frame_id} передан в планировщик.")
            transmission_size += frame.total_size

        print('Время, затраченное на передачу кадров: ',
              transmission_size / data_bandwidth)  # рассчитываем время передачи кадров

        for frame in frames:
            for task in frame.tasks:
                task.queued_time = datetime.now()
                task.status = Task.STATUS_READY  # статус задачи становится "Готова к исполнению"
                self.task_queue.put((task.priority, task))
                print(f"Задача {task.id} (приоритет: {task.priority}, статус: {task.status}) добавлена в очередь.")

    def distribute_tasks(self):  #метод, распределяющий задачи по процессорам
        while not self.task_queue.empty():
            _, task = self.task_queue.get()
            if random.random() < 0.1:  # эмуляция того, что задача может быть заблокирована (подробнее написано в ДЗ)
                task.status = Task.STATUS_BLOCKED
                print(f"Задача {task.id} заблокирована. Статус: {task.status}.")
                time.sleep(1)
                task.status = Task.STATUS_READY
                self.task_queue.put((task.priority, task))
                continue

            assigned = False
            for processor in self.processors:
                if processor.assign_task(task, self.cpu_clock_hz):
                    assigned = True
                    break

            if not assigned:  #если задача не была передана процессору, то она остается в очереди
                task.status = Task.STATUS_READY
                print(f"Все ядра заняты. Задача {task.id} возвращена в очередь. Статус: {task.status}.")
                self.task_queue.put((task.priority, task))


def main():
    # Configurable constants
    cpu_clock_hz = 2.5 * 10 ** 9  # тактовая частота процессора XuanTie-C910 2.5ГГц
    data_bandwidth = 100 * 10 ** 9  # канал передачи данных со скоростью 100гбит/cек
    eth_frame_size_bits = 1500 * 8  # размер кадра ethernet
    max_task_size_bits = 128  # максимальный размер задачи
    processors_count = 4  # количество процессоров для эмуляции многопроцессорной обработки
    cores_per_processor = 3  # количество ядер у одного процессора
    tasks_count = 20  # количество задач, которое необходимо выполнить

    memory = Memory()
    ieee = IEEE8023ba(eth_frame_size_bits, data_bandwidth)
    processors = [Processor(i, cores_per_processor) for i in range(processors_count)]
    planner = RTOS(processors, memory, ieee, cpu_clock_hz)

    tasks = [Task.generate_random_task(i, max_task_size_bits) for i in range(tasks_count)]
    for i, task in enumerate(tasks):
        memory.add_task(i, task)

    planner.load_tasks_from_memory(data_bandwidth)
    planner.distribute_tasks()


if __name__ == "__main__":
    main()
