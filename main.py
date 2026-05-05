#!/usr/bin/env python3
"""
INA219 Web Monitor for Raspberry Pi
Real-time voltage/current/power visualization at 10 Hz
"""

import time

from app import app, collector, run_server


if __name__ == '__main__':
    print("INA219 Web Monitor")
    print("Starting data collector at 10 Hz...")
    
    collector.start(sample_rate_hz=10)
    
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