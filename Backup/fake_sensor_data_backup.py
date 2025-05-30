import requests
import time
import random
from datetime import datetime

# Configuration
SERVER_URL = 'http://localhost:5000/sensordata'
INTERVAL = 3  # seconds between readings

def format_timestamp(dt):
    """Format datetime to ISO format without microseconds"""
    return dt.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

def generate_sensor_data():
    """Generate realistic sensor readings"""
    return {
        # Temperature between 20-30°C (room temperature with variations)
        'temperature': round(random.uniform(20.0, 30.0), 2),
        
        # Humidity between 30-70% (typical indoor humidity)
        'humidity': round(random.uniform(30.0, 70.0), 2),
        
        # Atmospheric pressure around 1013.25 hPa (standard sea level) with variations
        'pressure': round(random.uniform(1010.0, 1016.0), 2),
        
        # Light levels between 0-1000 lux (indoor lighting conditions)
        # 0-50: dark/night
        # 50-200: dim indoor
        # 200-500: normal indoor
        # 500-1000: bright indoor
        'lux': round(random.uniform(0, 1000), 2)
    }

def main():
    print("Starting fake sensor data generation...")
    print("Press Ctrl+C to stop")
    
    while True:
        try:
            # Generate and send data
            data = generate_sensor_data()
            
            # Send POST request to server
            response = requests.post(SERVER_URL, json=data)
            
            # Print status
            timestamp = format_timestamp(datetime.now())
            print(f"\n[{timestamp}] Sending data:")
            print(f"Temperature: {data['temperature']}°C")
            print(f"Humidity: {data['humidity']}%")
            print(f"Pressure: {data['pressure']} hPa")
            print(f"Light: {data['lux']} lux")
            print(f"Server response: {response.status_code}")
            
            # Wait for next reading
            time.sleep(INTERVAL)
            
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
            print("Make sure the sensor_server.py is running")
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping data generation")
            break

if __name__ == "__main__":
    main() 