from typing import List
import random
import time
import threading
from queue import PriorityQueue
from datetime import datetime
import logging

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Настройка логирования
logging.basicConfig(
    filename='simulation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Task:  # класс задачи
    STATUS_RUNNING = "Running"
    STATUS_READY = "Ready"
    STATUS_BLOCKED = "Blocked"
    STATUS_DONE = "Done"

    def __init__(self, task_id: int, priority: int, operations: int, size: int, ttl: int):
        self.id = task_id  # id задачи
        self.priority = priority  # приоритет задачи
        self.operations = operations  # количество операций
        self.size_bits = size  # размер задачи в битах
        self.queued_time = None  # время, в течение которого задача находилась в очереди
        self.status = Task.STATUS_READY  # начальный статус задачи
        self.ttl = ttl  # ttl одной задачи

    def reduce_operations(self,
                          completed_operations: int):  # метод для уменьшения количества операций, необходимых для выполнения задачи
        self.operations -= completed_operations
        if self.operations <= 0:
            self.operations = 0
            self.status = Task.STATUS_DONE

    def __lt__(self, other: 'Task') -> bool:  # определяем оператор < для сравнения задач по приоритету
        return self.priority > other.priority  # чем меньше приоритет, тем важнее задача

    def __str__(self):
        return f"Task(id={self.id}, priority={self.priority}, size={self.size_bits}, operations={self.operations}, status={self.status})"  # переопределение метода __str__, чтобы выводить информацию по задаче

    @staticmethod
    def generate_random_task(task_id: int, max_task_size_bits: int) -> 'Task':
        task_size_bits = random.randint(1, max_task_size_bits)  # размер задачи в битах
        operations_needed = random.randint(10 ** 6, 10 ** 7)  # количество операций для выполнения задачи
        priority = random.randint(1, 10)  # приоритет задачи
        ttl = 10 ** 6
        return Task(
            task_id=task_id,
            priority=priority,
            operations=operations_needed,
            size=task_size_bits,
            ttl=ttl
        )


class EthFrame:  # класс кадра
    def __init__(self, frame_id: int, tasks: List[Task], bandwidth: int):
        self.frame_id = frame_id  # id кадра
        self.tasks = tasks  # список задач в кадре
        self.total_size = sum(task.size_bits for task in tasks)  # размер кадра

    def __str__(self):
        task_ids = [task.id for task in self.tasks]
        return f"Frame ID {self.frame_id}, tasks: {len(task_ids)}, size: {self.total_size} bits"


class IEEE8023ba:  # реализация стандарта IEEE P802.3ba
    def __init__(self, max_frame_size_bits: int, bandwidth: int):
        self.max_frame_size_bits = max_frame_size_bits  # максимальный размер кадра
        self.bandwidth = bandwidth  # пропускная способность канала

    def group_tasks_into_frames(self, tasks: List[Task]) -> List[
        EthFrame]:  # метод, отвечающий за группировку задач в кадры
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
            logging.info(frame)

        logging.info(f"Created {len(frames)} frames from {len(tasks)} tasks.")
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
        self.processor_id = processor_id  # id процессора
        self.is_busy = False  # занято ли ядро в данный момент
        self.total_busy_time = 0  # время работы ядра
        self.lock = threading.Lock()  # блокировка ядра

    def execute_task(self, task: Task, cpu_clock_hz: int):
        with self.lock:
            self.is_busy = True  #меняем статус на занято
            task.status = Task.STATUS_RUNNING  #меняем статус на "running"

            logging.info(
                f"Processor {self.processor_id} Core {self.core_id} started task {task.id} (priority: {task.priority}, status: {task.status}).")  # логируем информацию по взятию задачи в обработку

            completed_operations = min(task.ttl, task.operations)  # количество выполненных оперций
            execution_time = completed_operations / cpu_clock_hz  # время выполнения операций
            time.sleep(execution_time)  # симуляция выполнения задачи

            task.reduce_operations(completed_operations)

            if task.operations > 0:
                logging.warning(
                    f"Processor {self.processor_id} Core {self.core_id} paused task {task.id} (remaining operations: {task.operations}).")
                task.status = Task.STATUS_READY
            else:
                logging.info(
                    f"Processor {self.processor_id} Core {self.core_id} completed task {task.id}. Status: {task.status}.")

            self.total_busy_time += execution_time  # добавляем время, в течение которого работал процессор
            self.is_busy = False  # меняем статус на свободно


class Processor:  # процессор с несколькими ядрами
    def __init__(self, processor_id: int, num_cores: int):
        self.processor_id = processor_id  #id процессора
        self.cores = [CoreProcessor(i, processor_id) for i in range(num_cores)]  # список ядер

    def get_total_busy_time(self):  # метод, возвращающий суммарное время работы процессора
        return sum(core.total_busy_time for core in self.cores)


class RTOS:  # планировщик задач
    def __init__(self, processors: List[Processor], memory: Memory, ieee: IEEE8023ba, cpu_clock_hz: int):
        self.processors = processors  # список процессоров
        self.task_queue = PriorityQueue()  # очередь задач
        self.memory = memory  # память, в которой хранятся задачи
        self.ieee = ieee  # стандарт передачи
        self.cpu_clock_hz = cpu_clock_hz  # тактовая частота процессора
        self.lock = threading.Lock()

    def load_tasks_from_memory(self, data_bandwidth):
        tasks = list(self.memory.ram.values())  # загружаем задачи из памяти
        self.memory.clear_memory()  # очищаем память
        frames = self.ieee.group_tasks_into_frames(tasks)  # группируем задачи по кадрам
        transmission_size = 0

        for frame in frames:
            logging.info(f"Frame {frame.frame_id} sent to scheduler.")
            transmission_size += frame.total_size

        logging.info(f"Transmission time: {transmission_size / data_bandwidth} seconds.")

        for frame in frames:
            for task in frame.tasks:
                task.queued_time = datetime.now()
                task.status = Task.STATUS_READY  # статус задачи становится "Готова к исполнению"
                self.task_queue.put((task.priority, task))
                logging.info(f"Task {task.id} added to queue (priority: {task.priority}, status: {task.status}).")

    def assign_task_to_core(self, core: CoreProcessor):  # метод, присваивающий задачу ядру
        with self.lock:
            if self.task_queue.empty():  # если очередь пуста, то выходим
                return
            _, task = self.task_queue.get()  # достаем задачу

        task.status = Task.STATUS_RUNNING  # меняем статус на "running"
        core_thread = threading.Thread(target=core.execute_task, args=(
        task, self.cpu_clock_hz))  # создаем поток для задачи и начинаем ее исполненение
        core_thread.start()
        core_thread.join()

        if task.operations > 0:
            with self.lock:
                self.task_queue.put((task.priority, task))

    def distribute_tasks(self):  # метод, распределяющий задачи по процессорам и ядрам
        self.processors = sorted(self.processors,
                                 key=lambda x: x.get_total_busy_time())  # сортируем процессоры по времени занятости
        while not self.task_queue.empty():
            threads = []

            for processor in self.processors:  # итерируемся по процессорам
                for core in processor.cores:  # итерируемся по ядрам конкретного процессора
                    if not core.is_busy:
                        core_thread = threading.Thread(target=self.assign_task_to_core, args=(
                        core,))  # если ядро свободно, то выделяем ей поток и присваиваем ее к ядру
                        threads.append(core_thread)
                        core_thread.start()

            for thread in threads:
                thread.join()


def plot_processor_load(processors, simulation_index):  # функция для построения гистограмм

    processor_ids = [processor.processor_id for processor in processors]
    busy_times = [processor.get_total_busy_time() for processor in processors]

    plt.bar(processor_ids, busy_times, color='skyblue')
    plt.xlabel('Processor ID')
    plt.ylabel('Total Busy Time (s)')
    plt.title(f'Processor Load Distribution - Simulation {simulation_index + 1}')

    # Устанавливаем целочисленные значения для оси X
    plt.xticks(ticks=range(len(processor_ids)), labels=[str(pid) for pid in processor_ids])

    # Добавляем подписи значений к каждому столбцу
    for i, value in enumerate(busy_times):
        plt.text(i, value, f'{value:.4f}', ha='center', va='bottom', fontsize=10)

    plt.gcf().subplots_adjust(top=0.8, bottom=0.25)

    filename = f"processor_load_distribution_simulation_{simulation_index + 1}.png"
    plt.savefig(filename)
    plt.close()
    print(f"График сохранён как '{filename}'")


def main():
    cpu_clock_hz = 1 * 10 ** 9 # тактовая частота процессора
    data_bandwidth = 100 * 10 ** 9 # канал передачи данных со скоростью 100гбит/cек
    eth_frame_size_bits = 1500 * 8 # размер кадра ethernet
    max_task_size_bits = 64 # максимальный размер задачи
    processors_count = 4 # количество процессоров для эмуляции многопроцессорной обработки
    cores_per_processor = 8 # количество ядер у одного процессора
    tasks_count = 100 # количество задач, которое необходимо выполнить

    memory = Memory()
    ieee = IEEE8023ba(eth_frame_size_bits, data_bandwidth)
    processors = [Processor(i, cores_per_processor) for i in range(processors_count)]
    planner = RTOS(processors, memory, ieee, cpu_clock_hz)

    tasks = [Task.generate_random_task(i, max_task_size_bits) for i in range(tasks_count)]
    for i, task in enumerate(tasks):
        memory.add_task(i, task)

    planner.load_tasks_from_memory(data_bandwidth)
    planner.distribute_tasks()
    plot_processor_load(processors)


if __name__ == "__main__":
    main()
