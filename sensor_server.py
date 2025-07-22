# sensor_server.py
from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)
# Disable template caching during development
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def init_db():
    conn = sqlite3.connect('sensordata.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            lux REAL
        )
    ''')
    conn.commit()
    conn.close()

def format_timestamp(dt):
    """Format datetime to ISO format without microseconds"""
    return dt.replace(microsecond=0).isoformat()

@app.route('/sensordata', methods=['POST'])
def receive_data():
    data = request.json
    if not data:
        return jsonify({'error': 'No data received'}), 400

    try:
        timestamp = format_timestamp(datetime.now())
        conn = sqlite3.connect('sensordata.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO sensor_data (timestamp, temperature, humidity, pressure, lux)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, data['temperature'], data['humidity'], data['pressure'], data['lux']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data stored'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/data')
def get_data():
    start = request.args.get('start')
    end = request.args.get('end')

    conn = sqlite3.connect('sensordata.db')
    c = conn.cursor()

    try:
        if start and end:
            # Remove any milliseconds from the timestamps
            start = start.split('.')[0]
            end = end.split('.')[0]
            
            # Filter by provided ISO-format start/end timestamps
            c.execute('''
                SELECT timestamp, temperature, humidity, pressure, lux
                FROM sensor_data
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start, end))
            rows = c.fetchall()
        else:
            # Default: latest 50 points
            c.execute('''
                SELECT timestamp, temperature, humidity, pressure, lux
                FROM sensor_data
                ORDER BY id DESC
                LIMIT 50
            ''')
            rows = c.fetchall()
            rows.reverse()  # oldest-first for chart

        data = {
            "timestamps": [row[0] for row in rows],
            "temperature": [row[1] for row in rows],
            "humidity":    [row[2] for row in rows],
            "pressure":    [row[3] for row in rows],
            "lux":         [row[4] for row in rows]
        }
        return jsonify(data)
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
