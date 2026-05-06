import random
import time
import math


class FakeINA219:
    """
    Эмулятор INA219 для тестирования без реального железа.
    Генерирует реалистичные данные с небольшим шумом и возможными скачками.
    """
    
    def __init__(self, base_voltage=12.0, base_current=0.5, noise_level=0.02):
        self.base_voltage = base_voltage      # Базовое напряжение (В)
        self.base_current = base_current      # Базовый ток (А)
        self.noise_level = noise_level        # Уровень шума (доля от значения)
        self._start_time = time.time()
        self._shunt_resistance = 0.1          # Сопротивление шунта (Ом)
    
    def _noise(self, value):
        """Добавляет случайный шум к значению"""
        return value * (1 + random.uniform(-self.noise_level, self.noise_level))
    
    def read_all(self):
        """
        Возвращает словарь с фейковыми данными, имитируя формат реального INA219.
        
        Returns:
            dict: {
                'bus_voltage': float,      # Напряжение на нагрузке (В)
                'shunt_voltage': float,    # Падение на шунте (В)
                'supply_voltage': float,   # Напряжение питания (В)
                'current': float,          # Ток (А)
                'power': float,            # Мощность (Вт)
                'timestamp': float         # Unix timestamp
            }
        """
        # Небольшое дрейфование базовых значений для реализма
        drift_v = 0.05 * math.sin((time.time() - self._start_time) * 0.5)
        drift_c = 0.1 * math.sin((time.time() - self._start_time) * 0.3 + 1)
        
        # Случайный скачок тока (имитация включения нагрузки)
        spike = 0
        if random.random() < 0.02:  # 2% шанс скачка
            spike = random.uniform(0.2, 1.0)
        
        bus_voltage = self._noise(self.base_voltage + drift_v)
        current = self._noise(max(0, self.base_current + drift_c + spike))
        
        # Расчёт производных величин (как в реальном INA219)
        shunt_voltage = current * self._shunt_resistance
        supply_voltage = bus_voltage + shunt_voltage
        power = bus_voltage * current
        
        return {
            'bus_voltage': round(bus_voltage, 4),
            'shunt_voltage': round(shunt_voltage, 6),
            'supply_voltage': round(supply_voltage, 4),
            'current': round(current, 4),
            'power': round(power, 4),
            'timestamp': time.time()
        }