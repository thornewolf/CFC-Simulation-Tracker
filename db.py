import sqlite3
import datetime

from simulation_run_utils import SimulationRun

DB_NAME = 'runs_test.db'

def create_table(drop_first=False):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''DROP TABLE IF EXISTS runs''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY,
        status TEXT,
        date_created text,
        reynolds int,
        mesh_n int,
        mesh_m int,
        jet_start int,
        jet_end int,
        jet_amp real,
        jet_freq real,
        a_tilde real,
        dt real,
        tolerance real,
        BCs real
    );
    ''')
    conn.commit()


def addSimulationRunToDatabase(run: SimulationRun):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''
        INSERT INTO runs (status, date_created, reynolds, mesh_n, mesh_m, jet_start, jet_end, jet_amp, jet_freq, a_tilde, dt, tolerance, BCs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''',
    (run.status, datetime.datetime.now(), run.reynolds, run.mesh_n, run.mesh_m, run.jet_start, run.jet_end, run.jet_amp, run.jet_freq, run.a_tilde, run.dt, run.tolerance, run.bcs))
    conn.commit()

def getSimulationRunById(id: int):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT * from runs where id=?''',(id,))
    result = c.fetchone()
    run = SimulationRun(*result)
    return run

def getAllSimulationRuns():
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT * from runs''')
    rows = c.fetchall()
    runs = []
    for row in rows:
        run = SimulationRun(*row)
        runs.append(run)
    return runs

def getFirstQueuedRun():
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT * from runs where status="QUEUED"''')
    row = c.fetchone()
    run = SimulationRun(*row)
    return run

def testCreateAndAddRunToDatabase():
    create_table(drop_first=True)
    run1 = SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    run2 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    run3 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2500, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    addSimulationRunToDatabase(run1)
    addSimulationRunToDatabase(run2)
    addSimulationRunToDatabase(run3)
    getSimulationRunById(1)
    getFirstQueuedRun()

if __name__ == '__main__':
    testCreateAndAddRunToDatabase()