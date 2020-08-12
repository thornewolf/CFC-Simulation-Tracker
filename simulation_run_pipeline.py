# main.py
import os
import sys
from subprocess import Popen, PIPE
import time
import threading
import sqlite3
import datetime
import logging
from typing import Union, List

from db import getFirstQueuedRun,addSimulationRunToDatabase

from simulation_run_utils import SimulationRun
from simulation_watcher import ProcessWatcher

logging.basicConfig(filename='simulations.log',level=logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logging.getLogger().addHandler(ch)

def generateSimulationStdin(run: SimulationRun):
    '''
    Generates the required input to start a simulation.

    Assumes that the simulation is being continued from some central state and the desired
    parameter to change is the jet.

    Args:
        run:  A SimulationRun representing the desired configuration

    Returns:
        A String representing the stdin required to start a simulation with that configuration.
        13 lines in total.
    '''
    separated_stdin = []
    # continue the simulation
    separated_stdin.append('2')
    # name of simulation to continue TODO: make this generic
    separated_stdin.append('simtocont')
    # don't change any simulation parameters
    separated_stdin.append('n')
    # do change jet parameters
    separated_stdin.append('y')
    # Start location, End Location, Amplitude, Frequency
    separated_stdin.append(f'{run.jet_start}')
    separated_stdin.append(f'{run.jet_end}')
    separated_stdin.append(f'{run.jet_amp}')
    separated_stdin.append(f'{run.jet_freq}')
    # time step
    separated_stdin.append('1e-3') # TODO: Check appropriate time step
    # additional step count
    separated_stdin.append('1000') # One million
    # Iterations between reports
    separated_stdin.append('100')
    # Output File name
    file_name = f'Run{run.id}-Re{run.reynolds}-JetA{run.jet_amp}-JetF{run.jet_freq}'
    separated_stdin.append(file_name)
    # Iterations between writes
    separated_stdin.append('500')
    # Say yes to continuing the simulation
    separated_stdin.append('y')
    
    final_stdin = '\n'.join(separated_stdin) + '\n'
    print('The final stdin to pass to the binary is')
    print(final_stdin)
    return final_stdin,file_name


def runExecutableWithStdIn(executable_path: Union[str, List[str]], stdin: str=''):
    '''
    Runs the specified executable then passes stdin to it.

    Args:
        executable_path: the path to the executable to run
        stdin: the stdin to pass
    
    Returns:
        The process spawned by running the executable.
    '''
    p = Popen(executable_path, stdin=PIPE, text=True, stdout=PIPE, encoding='utf-8')
    if stdin:
        p.stdin.write(stdin)
        p.stdin.flush() # This actually dumps the stdin
    return p

def pipeline(run):
    '''
    Runs the pipeline associated with an end to end simulation -> post processing run.

    The pipeline will create and run 2 processes in sequence then return. The first process is the
    simulation and the second process is the video generation.

    Args:
        run: The simulation run to process.

    Returns:
        None.
    '''

    logger = logging.getLogger(f'AutomateSims.simulation_run_pipeline.Run{run.id}')
    if run.id is None:
        run_id = addSimulationRunToDatabase(run)
        logger.info(f"Assigned {run.id} to current run")
        logger = logging.getLogger(f'AutomateSims.simulation_run_pipeline.Run{run.id}')
        run.id = run_id


    logger.setLevel(logging.INFO)

    logger.info(f"Beginnning pipeline run.")
    
    stdin, filename = generateSimulationStdin(run)
    root = os.getcwd()
    BIN_NAME = 'PFILONGMP.out'
    path = os.path.join(root, BIN_NAME)

    p = runExecutableWithStdIn(path, stdin)
    ProcessWatcher(run, p, ["SIMULATING", "AWAITING_POST_PROCESSING"])
    logger.info(f"Completed simulation step")
    p = runExecutableWithStdIn(['python3.8', os.path.join(root, 'postProcessFake.py')], '')
    ProcessWatcher(run, p, ["POST_PROCESSING", "COMPLETED"])
    logger.info(f"Completed post processing step")


if __name__ == '__main__':
    run = SimulationRun(None, "QUEUED", datetime.datetime.now(), 200, 149, 245, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-3, 10)
    pipeline(run)