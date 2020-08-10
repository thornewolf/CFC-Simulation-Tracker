from flask import Flask
from flask import render_template

from db import getAllSimulationRuns

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html', rows=getAllSimulationRuns())


if __name__ == '__main__':
    app.run()
