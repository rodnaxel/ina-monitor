import time


class DataLogger:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        
    def log(self, data):
        if self.file is None:
            self.file = open(self.filename, 'a')

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Exclude timestamp from data values
        data_values = ', '.join(str(v) for v in data.values() if v != data['timestamp'])
        
        line = f"{timestamp}, {data_values}\n"
        self.file.write(line)
        self.file.flush()