import sqlite3
import datetime
import json

from simulation_run_utils import SimulationRun

DB_NAME = 'runs_test.db'

def create_table(drop_first=False):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('''DROP TABLE IF EXISTS jobs''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        status TEXT,
        type TEXT,
        date_created text,
        configuration text
    );
    ''')
    conn.commit()

def serialize_run(run: SimulationRun):
    return json.dumps({
        'id': run.id,
        'status': run.status,
        'date_created': str(run.date_created),
        'reynolds': run.reynolds,
        'mesh_n': run.mesh_n,
        'mesh_m': run.mesh_m,
        'jet_start': run.jet_start,
        'jet_end': run.jet_end,
        'jet_amp': run.jet_amp,
        'jet_freq': run.jet_freq,
        'a_tilde': run.a_tilde,
        'dt': run.dt,
        'tolerance': run.tolerance,
        'bcs': run.bcs
    }, indent=1)

def deserialize_run(run_json):
    j = json.loads(run_json)
    run = SimulationRun(*j.values())
    run.date_created = datetime.datetime.fromisoformat(run.date_created)
    return run


def addSimulationRunToDatabase(run: SimulationRun):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('INSERT INTO jobs (status, type, date_created, configuration) VALUES (?, ?, ?, ?)',
        (run.status, 'SIMULATION', run.date_created, serialize_run(run)))
    rowid = c.lastrowid
    run.id = rowid
    c.execute('UPDATE jobs set configuration=(?) where id=?', (serialize_run(run), rowid))
    conn.commit()
    return rowid

def getSimulationRunById(id: int):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT configuration from jobs where id=?''',(id,))
    result = c.fetchone()
    run = deserialize_run(result[0])
    return run

def updateRunStatusById(id: int, new_status: str):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()

    c.execute('''SELECT configuration from jobs where id=?''', (id,))
    row = c.fetchone()
    run = deserialize_run(row[0])
    run.status = new_status

    c.execute('UPDATE jobs set status=?, configuration=? where id=?', (new_status, serialize_run(run), id))
    conn.commit()
    conn.close()

def getAllSimulationRuns():
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT configuration from jobs''')
    rows = c.fetchall()
    runs = []
    for row in rows:
        run = deserialize_run(row[0])
        runs.append(run)
    conn.close()
    return runs

def getFirstQueuedRun():
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT configuration from jobs where status="QUEUED"''')
    row = c.fetchone()
    if not row:
        return None
    run = deserialize_run(row[0])
    return run

def testCreateAndAddRunToDatabase():
    create_table(drop_first=True)
    r1dt = datetime.datetime.now()
    run1 = SimulationRun(None, "COMPLETED", r1dt, 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    run1_in_progress = SimulationRun(None, "IN_PROGRESS", r1dt, 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    run2 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    run3 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2500, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    addSimulationRunToDatabase(run1)
    addSimulationRunToDatabase(run2)
    addSimulationRunToDatabase(run3)
    assert run1 == getSimulationRunById(1)
    updateRunStatusById(1, "IN_PROGRESS")
    assert run2 == getFirstQueuedRun()

def testSerializeRun():
    run1 = SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    assert run1==deserialize_run(serialize_run(run1))


if __name__ == '__main__':
    create_table(drop_first=False)