from flask import Flask, render_template, request, jsonify
from functionSummary import get_driver_summary
from functionMonitor import df, load_data, get_monitor_data

app = Flask(__name__, template_folder="views", static_folder="static")

# Page: Main Page
@app.route('/')
def index():
    return render_template('index.html')

# Page: Summary Page
@app.route('/summary')
def summary():
    return render_template('summary.html')

# API: Get summary of driving behavior within a given period for a driver
@app.route('/api/summary', methods=['POST'])
def summary_api():
    print("summary api called")
    data = request.get_json()
    driver_id = data.get('driverID')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    result = get_driver_summary(driver_id, start_time, end_time)
    return jsonify(result)

# Page: Real-Time Monitoring Pgae
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/api/monitor_start', methods=['POST'])
def monitor_start_call():
    data = request.get_json()
    start_time = data.get('start_time')

    load_data(start_time)

    return jsonify({"status": "Data loaded"})

# API: Get simulation data for monitoring
@app.route('/api/monitor', methods=['POST'])
def monitor_api():
    print("monitor api called")
    data = request.get_json()
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    print("Start = " + start_time)
    print("End = " + end_time)
    cache_df = load_data(start_time)
    result = get_monitor_data(start_time, end_time, cache_df)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)