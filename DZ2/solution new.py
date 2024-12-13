import time
from queue import Queue
import random


def initialize_logs(processors_count):
    """Очистить файлы логов перед началом работы программы."""
    with open("SystemLOG.txt", "w", encoding="utf-8") as file:
        file.write("=== System Logs ===\n")
    for processor_id in range(processors_count):
        with open(f"Processor-{processor_id}_log.txt", "w", encoding="utf-8") as file:
            file.write(f"=== Logs for Processor-{processor_id} ===\n")


def print_proc_logs(processor_name, log):
    """Добавить лог для конкретного процессора."""
    with open(f"{processor_name}_log.txt", "a", encoding="utf-8") as file:
        file.write(log + '\n')


def print_system_logs(log):
    """Добавить системный лог."""
    with open("SystemLOG.txt", "a", encoding="utf-8") as file:
        file.write(log + '\n')


class DataChannel:
    speed = 100 * (10 ** 9)

    def __init__(self, memory):
        self.memory = memory
        self.frames = []
        self.ethernet_frame_size = 512
        self.headers_size = 144

    def calculate_frames(self):
        frame = Frame()
        for task in self.memory.tasks:
            if task.size + frame.get_occupied_space() <= self.ethernet_frame_size - self.headers_size:
                frame.add_task(task)
            else:
                frame = Frame()
                self.frames.append(frame)
                frame.add_task(task)
        self.frames.append(frame)
        print(f"Total Ethernet frames required: {len(self.frames)}")
        for frame in self.frames:
            print(frame)
        return len(self.frames)

    def transmit(self):
        total_frames = self.calculate_frames()
        transfer_time = total_frames * (512 / self.speed)
        print(f"Total transfer time: {transfer_time} seconds.")
        time.sleep(transfer_time)
        return self.frames


class Frame:
    def __init__(self):
        self.min_size = 512
        self.headers_size = 144
        self.tasks = []
        self.occupied_space = 0

    def __str__(self):
        tasks_info = ", ".join([str(task) for task in self.tasks])
        return f"Frame with {len(self.tasks)} tasks (Occupied space: {self.occupied_space} bytes): [{tasks_info}]"

    def get_occupied_space(self):
        return self.occupied_space

    def add_task(self, task):
        self.tasks.append(task)
        self.occupied_space += task.size


class Task:
    def __init__(self, name):
        self.name = name
        self.ticks_to_complete = random.randint(1, 100)
        self.size = random.randint(1, 128)
        self.remaining_operations = self.ticks_to_complete
        print(f"Task {self.name} created with {self.ticks_to_complete} operations and size {self.size} bytes.")

    def run(self, operations):
        self.remaining_operations -= operations
        if self.remaining_operations <= 0:
            self.remaining_operations = 0
        return self.remaining_operations

    def __str__(self):
        return f"Task {self.name} (Operations: {self.remaining_operations}/{self.ticks_to_complete}, Size: {self.size} bytes)"


class RoundRobin:
    def __init__(self, time_quantum, processors_count, num_cores):
        memory = Memory()
        self.time_quantum = time_quantum
        data_stream = DataChannel(memory)
        self.task_queue = self.get_tasks_from_data_channel(data_stream.transmit())
        self.processors = []
        self.completed_tasks = 0
        self.total_tasks = len(memory.tasks)
        for i in range(processors_count):
            processor = Processor(name=f"Processor-{i}", num_cores=num_cores)
            self.processors.append(processor)

    @staticmethod
    def get_tasks_from_data_channel(data):
        frames = data
        queue = Queue()
        for frame in frames:
            for task in frame.tasks:
                queue.put(task)
                print_system_logs(f"Task {task.name} added with {task.ticks_to_complete} operations and size {task.size} bytes.")
                print(f"Task {task.name} added with {task.ticks_to_complete} operations and size {task.size} bytes.")
        return queue

    def execute(self):
        active_tasks = []
        while not self.task_queue.empty() or active_tasks:
            for processor in self.processors:
                for core in processor.cores:
                    if core.status is None and not self.task_queue.empty():
                        task = self.task_queue.get()
                        core.assign_task(task)
                        log_message = f"Task {task.name} assigned to Core {core.name}."
                        print_proc_logs(processor.name, log_message)
                        # print(log_message)
                        active_tasks.append((processor, core))

            completed_cores = []
            for processor, core in active_tasks:
                core.execute_task(self.time_quantum, processor.clock_speed, processor.name, self.task_queue, self.completed_tasks)
                if core.status is None:
                    completed_cores.append((processor, core))

            active_tasks = [t for t in active_tasks if t not in completed_cores]

            if self.task_queue.empty():
                print("All tasks completed. Ending execution.")
                print_system_logs("All tasks completed. Ending execution.")
                break


class Processor:
    clock_speed = 2.5 * (10 ** 9)  # 2.5 GHz clock speed

    def __init__(self, name, num_cores):
        self.name = name
        self.cores = [Core(name=f'Core-{i}') for i in range(num_cores)]

    def __str__(self):
        return self.name


class Core:
    def __init__(self, name):
        self.status = None
        self.name = name
        self.current_task = None

    def execute_task(self, time_quantum, clock_speed, processor_name, task_queue, completed_tasks):
        operations_per_tick = clock_speed / 10 ** 9  # Operations per clock tick
        log_message = f"Core {self.name} is executing Task {self.current_task.name}. Remaining operations: {self.current_task.remaining_operations}."
        print_proc_logs(processor_name, log_message)
        # print(log_message)
        for _ in range(time_quantum):
            self.current_task.run(operations_per_tick)
            if self.current_task.remaining_operations <= 0:
                log_message = f"Task {self.current_task.name} completed successfully on Core {self.name} of Processor {processor_name}."
                print_proc_logs(processor_name, log_message)
                # print(log_message)
                completed_tasks += 1
                self.status = None
                self.current_task = None
                return
        if self.current_task.remaining_operations > 0:
            log_message = f"Task {self.current_task.name} did not complete on Core {self.name} of Processor {processor_name}. Requeuing."
            print_proc_logs(processor_name, log_message)
            # print(log_message)
            task_queue.put(self.current_task)
            self.status = None
            self.current_task = None

    def assign_task(self, task):
        if self.status is None:
            self.current_task = task
            self.status = task
            return True
        return False


class Memory:
    def __init__(self):
        self.tasks = [Task(name=i) for i in range(5)]


if __name__ == '__main__':
    initialize_logs(processors_count=2)
    round_robin = RoundRobin(time_quantum=10, processors_count=2, num_cores=2)
    round_robin.execute()