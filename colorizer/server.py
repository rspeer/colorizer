import flask
from flask import Flask, request
from collections import defaultdict
import sys
app = Flask(__name__)

from colorizer.reader import IncrementalColorizer
colorizers = defaultdict(lambda: IncrementalColorizer(8))

@app.route('/input/<client_id>/<text>')
def add_input(client_id, text):
    result = colorizers[client_id].add_text(text.replace('+', ' '))
    return flask.Response(response=flask.json.dumps(result), mimetype='json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

