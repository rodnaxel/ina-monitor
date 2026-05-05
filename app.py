from flask import Flask, render_template, jsonify
from collector import DataCollector

app = Flask(__name__)
collector = DataCollector(debug=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    data = collector.get_data()
    latest = collector.get_latest()
    return jsonify({
        'data': data,
        'latest': latest,
        'count': len(data),
        'sample_rate': 10
    })


@app.route('/api/latest')
def get_latest():
    return jsonify(collector.get_latest())


def run_server(host='0.0.0.0', port=5000):
    app.run(host=host, port=port, threaded=True)