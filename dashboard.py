import flask
from flask import Flask
from flask import render_template
from flask import redirect,url_for
import datetime
import json

from db import getAllSimulationRuns,addSimulationRunToDatabase
from simulation_run_utils import SimulationRun

app = Flask(__name__)

'''
The code here is self explanatory if you are familiar with the Python Flask
framework. If you need to make modifications to this file, I recommend that
you first learn how flask works overall.

See: http://flask.pocoo.org/docs/0.12/quickstart/
'''

@app.route('/')
def index():
    return render_template('index.html', rows=getAllSimulationRuns())

@app.route('/add', methods=['GET', 'POST'])
def add():
    if flask.request.method == 'POST':
        run_json = flask.request.form.get('configuration_text')
        run = SimulationRun(as_json=run_json)
        run.config.continued_run = flask.request.form.get('simtocont')
        run.config.date_created = datetime.datetime.now()
        run.config.status = 'QUEUED'
        run_id = addSimulationRunToDatabase(run)
        return redirect(url_for('index'))

    sample_run = SimulationRun(as_json='''{
        "id": null,
        "jet_start": 120,
        "jet_end": 130,
        "jet_amp": 0.001,
        "jet_freq": 0.007,
        "additional_steps": 500,
        "iterations_between_writes": 250
        }
    ''')
    return render_template('add.html', continue_simulation_options=get_baseline_simulations(), default_text=sample_run.json)

@app.route('/info/<run_id>', methods=['GET'])
def run_info(run_id):
    body = []
    with open('simulations.log', 'r') as f:
        body = f.readlines()
    body = [l for l in body if f'Run{run_id}:' in l]
    return render_template('siminfo.html', log=body)

def get_baseline_simulations():
    baselines = None
    with open('baseline_sims.config') as f:
        baselines = json.loads(f.read())
    return baselines

if __name__ == '__main__':

	app.run(host='0.0.0.0', port='5000')
