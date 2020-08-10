# main.py
import os
from subprocess import Popen, PIPE
import time
import threading
import sqlite3
import datetime
from typing import Union, List

from db import getFirstQueuedRun

from simulation_run_utils import SimulationRun
from simulation_watcher import ProcessWatcher

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
    separated_stdin.append('1000000') # One million
    # Output File name
    separated_stdin.append(f'Re{run.reynolds}-JetA{run.jet_amp}-JetF{run.jet_freq}')
    # Iterations between writes
    separated_stdin.append('1000')
    # Say yes to continuing the simulation
    separated_stdin.append('y')

    return '\n'.join(separated_stdin)


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

def testRunBinaryWithStdIn():
    '''
    Tests that running the binary is successful.
    '''
    root = os.getcwd()
    BIN_NAME = 'a.out'
    path = os.path.join(root, BIN_NAME)
    p = runExecutableWithStdIn(path, "1 2 3 4 5 6 7 8 9 0\n")
    ret = []
    for line in p.stdout:
        ret.append(line)
    print(ret)

def testGenerateSimulationStdin():
    run1 = SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    print(generateSimulationStdin(run1))

def pipeline():
    run = SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    stdin = generateSimulationStdin(run)

    root = os.getcwd()
    BIN_NAME = 'a.out'
    path = os.path.join(root, BIN_NAME)

    p = runExecutableWithStdIn(path, stdin)
    ProcessWatcher(run, p)


if __name__ == '__main__':
    pipeline()