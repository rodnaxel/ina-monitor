from collections import deque
import threading
import time


class DataCollector:
    def __init__(self, sensor, logger=None, max_points=300):
        self.sensor = sensor
        self.logger = logger

        self.buffer = deque(maxlen=max_points)
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self, sample_rate_hz=10):
        """Start data collection thread"""
        self.running = True
        self.thread = threading.Thread(
            target=self._collect, args=(sample_rate_hz,), daemon=True
        )
        self.thread.start()

    def _collect(self, sample_rate_hz):
        """Collect data at specified rate"""
        interval = 1.0 / sample_rate_hz
        while self.running:
            start = time.time()
            data = self.sensor.read_all()
            if data:
                with self.lock:
                    self.buffer.append(data)
                    
                # Если есть логгер, записать данные в файл
                if self.logger:
                    self.logger.log(data)
            
            # Precise timing
            elapsed = time.time() - start
            sleep_time = max(0, interval - elapsed)
            time.sleep(sleep_time)

    def get_data(self, last_n=None):
        """Get collected data"""
        with self.lock:
            if last_n:
                return list(self.buffer)[-last_n:]
            return list(self.buffer)

    def get_latest(self):
        """Get latest measurement"""
        with self.lock:
            return self.buffer[-1] if self.buffer else None

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
