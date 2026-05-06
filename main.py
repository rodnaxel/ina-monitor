#!/usr/bin/env python3
"""
INA219 Web Monitor for Raspberry Pi
Real-time voltage/current/power visualization at 10 Hz
"""
import time

from config import Config, Ina219Config
from ina219 import INA219, FakeINA219
from collector import DataCollector
from web.app import create_app


if __name__ == '__main__':
    print("INA219 Web Monitor")
    print("Starting data collector...")
    
    if Config.DEBUG:
        print("Data collector initialized in DEBUG mode with FakeINA219")
        sensor = FakeINA219()
    else:
        print("Data collector initialized with real INA219 sensor")
        sensor = INA219()

    collector = DataCollector(
        sensor, 
        max_points=Ina219Config.MAX_POINTS
    )
    collector.start(sample_rate_hz=Ina219Config.SAMPLE_RATE_HZ)
    
    # Create Flask app
    app = create_app(collector, debug=Config.DEBUG)
    
    # Wait for first reading
    time.sleep(0.5)
    first = collector.get_latest()
    
    if first:
        print(f"First reading: {first['supply_voltage']:.3f}V, {first['current']:.4f}A")
    else:
        print("Warning: No data from sensor. Check I2C connection.")
        print("Used sudo i2cdetect -y 1")
    
    
    print("\nStarting web server on http://0.0.0.0:5000")
    print("Open in browser: http://<raspberry-pi-ip>:5000")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        collector.stop()