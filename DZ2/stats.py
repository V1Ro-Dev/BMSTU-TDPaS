import numpy as np
from Solution import plot_processor_load

def run_simulation():
    from Solution import Processor, Memory, RTOS, IEEE8023ba, Task # Импортируем классы

    # Конфигурация
    cpu_clock_hz = 1 * 10 ** 9  # Тактовая частота процессора
    data_bandwidth = 100 * 10 ** 9  # Скорость передачи данных
    eth_frame_size_bits = 1500 * 8  # Размер кадра Ethernet
    max_task_size_bits = 128  # Максимальный размер задачи
    processors_count = 4  # Количество процессоров
    cores_per_processor = 8  # Количество ядер на процессоре
    tasks_count = 100  # Количество задач

    # Инициализация системы
    memory = Memory()
    ieee = IEEE8023ba(eth_frame_size_bits, data_bandwidth)
    processors = [Processor(i, cores_per_processor) for i in range(processors_count)]
    planner = RTOS(processors, memory, ieee, cpu_clock_hz)

    # Генерация задач
    tasks = [Task.generate_random_task(i, max_task_size_bits) for i in range(tasks_count)]
    for i, task in enumerate(tasks):
        memory.add_task(i, task)

    # Загрузка задач и их распределение
    planner.load_tasks_from_memory(data_bandwidth)
    planner.distribute_tasks()

    # Сбор данных о времени работы процессоров
    busy_times = [processor.get_total_busy_time() for processor in processors]
    return busy_times, processors


# Множественные измерения
NUM_SIMULATIONS = 5
NUM_PROCESSORS = 4

for i in range(NUM_SIMULATIONS):
    busy_times, processors = run_simulation()  # Получение данных о времени работы процессоров
    plot_processor_load(processors, i)  # Построение и сохранение гистограммы

    mean = np.mean(busy_times)
    variance = np.var(busy_times)
    std_deviation = np.std(busy_times)

    print(f"Результаты симуляции {i + 1}:")
    print("Время работы каждого процессора:", busy_times)
    print(f"Среднее значение: {mean:.4f}")
    print(f"Дисперсия: {variance:.4f}")
    print(f"Стандартное отклонение: {std_deviation:.4f}\n")
