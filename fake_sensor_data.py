#!/usr/bin/env python3
"""
Fake Sensor Data Generator
Simulates ESP32 sensor readings and sends them to a local server
"""

import requests
import json
import time
import random
import math
from datetime import datetime

# Server configuration
SERVER_URL = "http://127.0.0.1:8080/sensordata"
SEND_INTERVAL = 5  # seconds (matches ESP32 delay)

class SensorSimulator:
    def __init__(self):
        # Base values for realistic outdoor conditions
        self.base_temperature = 23.0  # Celsius
        self.base_humidity = 23.0     # Percentage
        self.base_pressure = 1013.25  # hPa (standard atmospheric pressure)
        
        # For creating smooth variations
        self.temp_offset = 0
        self.humidity_offset = 0
        self.pressure_offset = 0
        self.light_phase = 0
        
    def generate_temperature(self):
        """Generate realistic temperature readings around 23°C"""
        # Slow drift ±2°C with small random variations
        drift = math.sin(time.time() / 300) * 2  # 5-minute cycle
        noise = random.uniform(-0.5, 0.5)
        return round(self.base_temperature + drift + noise, 1)
    
    def generate_humidity(self):
        """Generate realistic humidity readings around 23%"""
        # Humidity tends to be inversely related to temperature
        temp_factor = (self.generate_temperature() - self.base_temperature) * -0.5
        drift = math.sin(time.time() / 400) * 3  # Slower variation
        noise = random.uniform(-1, 1)
        humidity = self.base_humidity + temp_factor + drift + noise
        return round(max(10, min(90, humidity)), 1)  # Clamp between 10-90%
    
    def generate_pressure(self):
        """Generate realistic atmospheric pressure"""
        # Pressure changes slowly throughout the day
        daily_cycle = math.sin(time.time() / 43200) * 5  # 12-hour cycle, ±5 hPa
        noise = random.uniform(-1, 1)
        return round(self.base_pressure + daily_cycle + noise, 1)
    
    def generate_light(self):
        """Generate light readings fluctuating between 100-700 lux"""
        # More dynamic light changes to simulate cloud cover, shadows, etc.
        base_light = 400  # Mid-range
        
        # Fast fluctuations for cloud cover
        fast_variation = math.sin(time.time() / 30) * 150  # 30-second cycle
        medium_variation = math.sin(time.time() / 120) * 100  # 2-minute cycle
        
        # Random spikes and dips
        noise = random.uniform(-50, 50)
        
        light = base_light + fast_variation + medium_variation + noise
        return round(max(100, min(700, light)), 1)  # Clamp between 100-700
    
    def get_sensor_reading(self):
        """Generate a complete sensor reading"""
        return {
            "temperature": self.generate_temperature(),
            "humidity": self.generate_humidity(),
            "pressure": self.generate_pressure(),
            "lux": self.generate_light()
        }

def send_sensor_data(data):
    """Send sensor data to the server"""
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(SERVER_URL, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ Data sent successfully. Response code: {response.status_code}")
            return True
        else:
            print(f"✗ Server responded with code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Failed to connect to server. Is the server running at 127.0.0.1:5000?")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error sending data: {str(e)}")
        return False

def main():
    print("🌡️  Fake Sensor Data Simulator")
    print(f"📡 Sending data to: {SERVER_URL}")
    print(f"⏱️  Interval: {SEND_INTERVAL} seconds")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")
    
    simulator = SensorSimulator()
    
    try:
        while True:
            # Generate sensor reading
            sensor_data = simulator.get_sensor_reading()
            
            # Create JSON payload (matching ESP32 format)
            payload = {
                "temperature": sensor_data["temperature"],
                "humidity": sensor_data["humidity"], 
                "pressure": sensor_data["pressure"],
                "lux": sensor_data["lux"]
            }
            
            # Print the payload (like ESP32 Serial output)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] --- Sending JSON Payload ---")
            print(f"[{timestamp}] {json.dumps(payload)}")
            
            # Send data
            success = send_sensor_data(payload)
            
            if success:
                print(f"[{timestamp}] 📤 Data transmitted")
            else:
                print(f"[{timestamp}] ❌ Transmission failed")
            
            print()  # Empty line for readability
            
            # Wait before next reading
            time.sleep(SEND_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping sensor simulation...")
        print("Goodbye!")

if __name__ == "__main__":
    main()