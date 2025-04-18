from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# Driver summary page
@app.route('/summary')
def summary():
    dummy_data = [
        {"plate": "AB1234", "overspeed": 5, "fatigue": 2, "neutral_time": 20},
        {"plate": "CD5678", "overspeed": 8, "fatigue": 3, "neutral_time": 35}
    ]
    return render_template('summary.html', drivers=dummy_data)

# Real-time monitoring page
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

# API for simulated real-time speed data
@app.route('/api/speed')
def speed_api():
    return jsonify({
        "plate": "AB1234",
        "speed": random.randint(50, 130),
        "timestamp": "2025-04-17 16:00"
    })

if __name__ == '__main__':
    app.run(debug=True)