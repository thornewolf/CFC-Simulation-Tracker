import sqlite3
import datetime
import json
import logging

from simulation_run_utils import SimulationRun

DB_NAME = 'runs_test.db'

def create_table(drop_first=False):
    '''
    Creates the job table wthin the database

    Args:
        drop_first: Will delete the table if it exists prior to issuing a
        create statement. Use cases may be if the run-space becomes garbled.

    Returns:
        None
    '''
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

'''
The following set of functions have self-explanatory names. If you need
additional functionality from any of these functions and are having trouble
making the necessary modifications, look into the sqlite3 library and how SQL
code is written.
'''

def addSimulationRunToDatabase(run: SimulationRun):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('INSERT INTO jobs (status, type, date_created, configuration) VALUES (?, ?, ?, ?)',
        (run.config.status, 'SIMULATION', run.config.date_created, run.json))
    rowid = c.lastrowid
    run.config.id = rowid
    c.execute('UPDATE jobs set configuration=(?) where id=?', (run.json, rowid))
    conn.commit()
    return rowid

def getSimulationRunById(id: int):
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT configuration from jobs where id=?''',(id,))
    result = c.fetchone()
    run = SimulationRun(as_json=result[0])
    return run

def updateRunStatusById(id: int, new_status: str):
    logger = logging.getLogger('AutomateSims.db.updateRunStatusById')
    logger.info(f"Updating Run {id} with new status \n{new_status}")

    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()

    c.execute('''SELECT configuration from jobs where id=?''', (id,))
    row = c.fetchone()
    run = SimulationRun(as_json=row[0])
    run.config.status = new_status

    c.execute('UPDATE jobs set status=?, configuration=? where id=?', (new_status, run.json, id))
    conn.commit()
    conn.close()

def updateRunInDatabase(run: SimulationRun):
    logger = logging.getLogger('AutomateSims.db.updateRunStatusById')
    logger.info(f"Updating Run {run.config.id} with new configuration\n{run.json}")

    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()

    c.execute('UPDATE jobs set configuration=? where id=?', (run.json, run.config.id))
    conn.commit()
    conn.close()

def getAllSimulationRuns():
    conn = sqlite3.connect(DB_NAME) 
    c = conn.cursor()
    c.execute('''SELECT configuration from jobs''')
    rows = c.fetchall()
    runs = []
    for row in rows:
        run = SimulationRun(as_json=row[0])
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
    run = SimulationRun(as_json=row[0])
    return run

def testCreateAndAddRunToDatabase():
    '''
    Test function to ensure that we can add a variety of runs to the database.
    '''
    # TODO: Make this function use a different database file, rather than wiping the main one. 
    create_table(drop_first=True)
    r1dt = datetime.datetime.now()
    run1 = SimulationRun(None, "COMPLETED", r1dt, 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True)
    run1_in_progress = SimulationRun(None, "IN_PROGRESS", r1dt, 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True)
    run2 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True)
    run3 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2500, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True)
    addSimulationRunToDatabase(run1)
    addSimulationRunToDatabase(run2)
    addSimulationRunToDatabase(run3)
    assert run1 == getSimulationRunById(1)
    updateRunStatusById(1, "IN_PROGRESS")
    assert run2 == getFirstQueuedRun()


if __name__ == '__main__':
    testCreateAndAddRunToDatabase()
    create_table(drop_first=False)