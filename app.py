from flask import Flask, render_template, jsonify


def create_app(collector, debug=False):
    app = Flask(__name__)

    @app.route('/')
    def index():
        debug_label = "Режим отладки" if debug else ""
        return render_template('index.html',  mode=debug_label)


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
    
    return app