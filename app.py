from flask import Flask, render_template, request, jsonify
from functionSummary import get_driver_summary
from functionMonitor import get_simulation_data

app = Flask(__name__)

# Page: Main Page
@app.route('/')
def index():
    return render_template('index.html')

# Page: Summary Page
@app.route('/summary')
def summary():
    return render_template('summary.html')

# API: Get summary of driving behavior within a given period for a driver
@app.route('/api/summary', methods=['GET'])
def summary_api():
    driver_id = request.args.get('driverID')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    result = get_driver_summary(driver_id, start_time, end_time)
    return jsonify(result)

# Page: Real-Time Monitoring Pgae
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

# API: Get simulation data for monitoring
@app.route('/api/simulation', methods=['GET'])
def simulation_api():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    result = get_simulation_data(start_time, end_time)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)