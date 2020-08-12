import flask
from flask import Flask
from flask import render_template
from flask import redirect,url_for
import datetime

from db import getAllSimulationRuns,addSimulationRunToDatabase
from simulation_run_utils import SimulationRun
from db import serialize_run,deserialize_run

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', rows=getAllSimulationRuns())

@app.route('/add', methods=['GET', 'POST'])
def add():
    if flask.request.method == 'POST':
        run = deserialize_run(flask.request.form.get('configuration_text'))
        run_id = addSimulationRunToDatabase(run)
        return redirect(url_for('index'))

    sample_run = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    return render_template('add.html', default_text=serialize_run(sample_run))


if __name__ == '__main__':
    app.run()
