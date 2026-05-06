import smbus2
import time
import util


INA219_ADDRESS = 0x40  # Default I2C address (A0=A1=GND)

# Registers
REG_CONFIG = 0x00
REG_SHUNT_VOLTAGE = 0x01
REG_BUS_VOLTAGE = 0x02
REG_POWER = 0x03
REG_CURRENT = 0x04
REG_CALIBRATION = 0x05

# Calibration for 32V (max 26V) / 2A range (0.1 Ohm shunt)
CALIBRATION_VALUE = 4096
CURRENT_LSB = 0.0001  # A/bit (100 µA)
POWER_LSB = 0.002     # W/bit (2 mW)
BUS_VOLTAGE_LSB = 0.004  # V/bit (4 mV)
SHUNT_VOLTAGE_LSB = 0.00001  # V/bit (10 µV)


class INA219:
    def __init__(self, bus_number=1, address=INA219_ADDRESS):
        self.bus = smbus2.SMBus(bus_number)
        self.address = address
        
        self._cal_value = CALIBRATION_VALUE
        self._current_lsb = CURRENT_LSB
        self._power_lsb = POWER_LSB
        
        self._configure()
    
    def _write_register(self, register, value):
        """Write 16-bit value to register (big-endian)"""
        data = [(value >> 8) & 0xFF, value & 0xFF]
        self.bus.write_i2c_block_data(self.address, register, data)
    
    def _read_register(self, register):
        """Read 16-bit value from register (big-endian)"""
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        return (data[0] << 8) | data[1]
    
    def _configure(self):
        """Configure INA219 for continuous measurement"""
        # Config: 32V range, gain 8 (320mV), 12-bit ADC, continuous mode
        
        # Bits: RST(15)=0, BRNG(13)=1 (32V), PG(11:12)=11 (gain 8), 
        #       BADC(7:10)=0011 (12bit), SADC(3:6)=0011 (12bit), MODE(0:2)=111 (cont shunt+bus)
        config = 0x399F  # 0011 1001 1001 1111
        self._write_register(REG_CONFIG, config)
        self._write_register(REG_CALIBRATION, self._cal_value)
        time.sleep(0.1)  # Wait for first conversion
    
    def read_shunt_voltage(self):
        """Read shunt voltage in Volts"""
        raw = self._read_register(REG_SHUNT_VOLTAGE)
        # Convert from two's complement
        if raw > 32767:
            raw -= 65536
        return raw * SHUNT_VOLTAGE_LSB
    
    def read_bus_voltage(self):
        """Read bus voltage in Volts (V- to GND)"""
        raw = self._read_register(REG_BUS_VOLTAGE)
        # Upper 13 bits are voltage, lower 3 bits are flags
        voltage_raw = raw >> 3
        return voltage_raw * BUS_VOLTAGE_LSB
    
    def read_current(self):
        """Read current in Amperes"""
        # Must write calibration before reading current
        self._write_register(REG_CALIBRATION, self._cal_value)
        raw = self._read_register(REG_CURRENT)
        if raw > 32767:
            raw -= 65536
        return raw * self._current_lsb
    
    def read_power(self):
        """Read power in Watts"""
        self._write_register(REG_CALIBRATION, self._cal_value)
        raw = self._read_register(REG_POWER)
        return raw * self._power_lsb
    
    def read_all(self):
        """Read all measurements at once"""
        try:
            shunt_v = self.read_shunt_voltage()
            bus_v = self.read_bus_voltage()
            current = self.read_current()
            power = self.read_power()
            
            # Supply voltage = bus + shunt
            supply_v = bus_v + shunt_v
            
            return {
                'bus_voltage': round(bus_v, 4),
                'shunt_voltage': round(shunt_v, 6),
                'supply_voltage': round(supply_v, 4),
                'current': round(current, 4),
                'power': round(power, 4),
                'timestamp': time.time()
            }
        except Exception as e:
            print(f"Read error: {e}")
            return None
        
        
class FakeINA219:
    """
    Эмулятор INA219 для тестирования без реального железа.
    Генерирует реалистичные данные с небольшим шумом и возможными скачками.
    """
    
    def __init__(self, base_voltage=12.0, base_current=0.5, noise_level=0.02, shunt_resistance=0.1):
        self.base_voltage = base_voltage            # Базовое напряжение (В)
        self.base_current = base_current            # Базовый ток (А)
        self.noise_level = noise_level              # Уровень шума (доля от значения)
        self._shunt_resistance = shunt_resistance   # Сопротивление шунта (Ом)
    
    def read_all(self):
        """Генерирует набор данных, имитирующий реальные измерения"""
        # Генерация дрейфа
        drift_v = util.drift(self.base_voltage, amplitude=0.05, frequency=0.5)
        drift_c = util.drift(self.base_current, amplitude=0.1, frequency=0.3)
        
        # Случайный скачок тока
        spike = util.spike(chance=0.02, min_spike=0.2, max_spike=1.0)
        
        # Генерация шума и итоговых значений
        bus_voltage = util.noise(self.base_voltage + drift_v, self.noise_level)
        current = util.noise(max(0, self.base_current + drift_c + spike), self.noise_level)
        
        # Расчёт производных величин
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