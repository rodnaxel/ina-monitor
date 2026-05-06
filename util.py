import random
import time
import math


def noise(value, level=0.02):
    """Добавляет случайный шум к значению"""
    return value * (1 + random.uniform(-level, level))

def drift(base, amplitude=0.05, frequency=0.5):
    """Генерирует медленное дрейфование базового значения"""
    return amplitude * math.sin(time.time() * frequency)

def spike(chance=0.02, min_spike=0.2, max_spike=1.0):
    """Генерирует случайный скачок с заданной вероятностью"""
    if random.random() < chance:
        return random.uniform(min_spike, max_spike)
    return 0