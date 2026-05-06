class Config:
    DEBUG = True         # Set to True to use FakeINA219 for testing without hardware         
    
    
class Ina219Config:
    SAMPLE_RATE_HZ = 10  # Data collection rate in Hz
    MAX_POINTS = 300     # Max data points to keep in memory (30 seconds at 10 Hz)