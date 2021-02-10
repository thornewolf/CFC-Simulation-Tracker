# main.py
import os
import sys
import json
import time
import threading
import sqlite3
import datetime
import logging
import glob
import multiprocessing as mp
import zipfile
from subprocess import Popen, PIPE
from typing import Union, List

from db import getFirstQueuedRun,addSimulationRunToDatabase,updateRunInDatabase,getSimulationRunById

from simulation_run_utils import SimulationRun
from simulation_watcher import ProcessWatcher
from images_to_video import images_to_video

logging.basicConfig(filename='simulations.log',level=logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logging.getLogger().addHandler(ch)

def generateVisualizationStdin(run: SimulationRun, logger=None):
    '''
    Generates the required input to start the conversion from output files to
    images.
    
    Args:
        run: A SimulationRun object that contains the necessary information for
        file naming and accessing.

    Returns:
        A String containing the input for the visualization code.
    '''
    file_name = run.name

    separated_stdin = []
    # What is the P001 that you want to start at?
    separated_stdin.append(f'{file_name}P001')
    file_count = len(glob.glob(f'{file_name}P[0-9][0-9][0-9]'))
    # How many files are there to work with?
    # file_count-1 to intentionally ignore the base_name file.
    separated_stdin.append(f'{file_count-1}')
    final_stdin = '\n'.join(separated_stdin) + '\n'
    if logger is not None:
        logger.info(f'The final stdin to pass to the visualization is\n{final_stdin}')
    return final_stdin

def deleteLeftoverFiles(prefix: str):
    '''
    Removes all files that match the given prefix

    Args:
        prefix: The prefix to do a search on.

    Returns:
        None
    '''

    maching_files = glob.glob(f'{prefix}P[0-9][0-9][0-9]')
    maching_files = [f for f in maching_files if '.avi' not in f]
    for f in maching_files:
        os.remove(f)

def get_output_file_names(run):
    file_name = run.name
    output_files = glob.glob(f'{file_name}P*')

    # This should extract the file_number so we do not sort lexographically
    sorting_function = lambda file_name: int(file_name.split('P')[1])

    output_files = sorted(output_files, key=sorting_function)
    return output_files



def compress_files(inp_file_names, run, logger=None):
    """
    Compresses a list of files into a .zip file.

    Args:
        inp_file_names : list of filenames to be zipped
        out_zip_file : output zip file

    Returns:
        None
    """

    out_zip_file = f'{run.name}.zip'

    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED
    if logger is not None:
        logger.info(f" *** Input File name passed for zipping - {inp_file_names}")

    # create the zip file first parameter path/name, second mode
    if logger is not None:
        logger.info(f' *** out_zip_file is - {out_zip_file}')
    zf = zipfile.ZipFile(out_zip_file, mode="w")

    try:
        for file_to_write in inp_file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            if logger is not None:
                logger.info(f' *** Processing file {file_to_write}')
                zf.write(file_to_write, file_to_write, compress_type=compression)
    except FileNotFoundError as e:
        if logger is not None:
            logger.info(f' *** Exception occurred during zip process - {e}')
    finally:
        # Don't forget to close the file!
        zf.close()



def generateSimulationStdinCont(run: SimulationRun, logger=None):
    '''
    Generates the required input to start the continuation a simulation.
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
    with open('baseline_sims.config') as f:
        options = json.loads(f.read())
    separated_stdin.append(options[run.config.continued_run])
    # don't change any simulation parameters
    separated_stdin.append('n')
    # do change jet parameters
    separated_stdin.append('y')
    # Start location, End Location, Amplitude, Frequency
    separated_stdin.append(f'{run.config.jet_start}')
    separated_stdin.append(f'{run.config.jet_end}')
    separated_stdin.append(f'{run.config.jet_amp}')
    separated_stdin.append(f'{run.config.jet_freq}')
    # time step
    # separated_stdin.append(f'{run.config.dt}')
    # additional step count
    separated_stdin.append(f'{run.config.additional_steps}')
    # Iterations between reports
    separated_stdin.append(f'{run.config.time_between_reports}')
    # Output File name
    file_name = run.name
    separated_stdin.append(file_name)
    # Iterations between writes
    separated_stdin.append(f'{run.config.iterations_between_writes}')
    # Say yes to continuing the simulation
    separated_stdin.append('y')
    
    final_stdin = os.linesep.join(separated_stdin) + os.linesep
    if logger is not None:
        logger.info(f'The final stdin to pass to the binary is\n{final_stdin}')
    return final_stdin,file_name


def generateSimulationStdinNovel(run: SimulationRun, logger=None):
    '''
    Generates the required input to start a novel simulation.
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
    separated_stdin.append('1')
    # size of mesh
    separated_stdin.append(f'{run.config.mesh_n}')
    separated_stdin.append(f'{run.config.mesh_m}')
    # jet included
    separated_stdin.append('y')
    # Start location, End Location, Amplitude, Frequency
    separated_stdin.append(f'{run.config.jet_start}')
    separated_stdin.append(f'{run.config.jet_end}')
    separated_stdin.append(f'{run.config.jet_amp}')
    separated_stdin.append(f'{run.config.jet_freq}')
    # reynold number
    separated_stdin.append(f'{run.config.reynolds}')
    # circulation parameter (A-tilde)
    separated_stdin.append(f'{run.config.a_tilde}')
    # time steps
    separated_stdin.append(f'{run.config.time_steps}')
    # Iterations between reports
    separated_stdin.append(f'{run.config.time_between_reports}')
    # dt
    separated_stdin.append(f'{run.config.dt}')
    # tolerance level
    separated_stdin.append(f'{run.config.tolerance}')
    # BCs
    separated_stdin.append(f'{run.config.bcs}')
    # Output File name
    file_name = run.name
    separated_stdin.append(file_name)
    # Iterations between file writes
    separated_stdin.append(f'{run.config.iterations_between_writes}')
    # Say yes to continuing the simulation
    separated_stdin.append('y')

    final_stdin = os.linesep.join(separated_stdin) + os.linesep
    if logger is not None:
        logger.info(f'The final stdin to pass to the binary is\n{final_stdin}')
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

    logger = logging.getLogger(f'AutomateSims.simulation_run_pipeline.Run{run.config.id}')
    if run.config.id is None:
        run_id = addSimulationRunToDatabase(run)
        logger.info(f"Assigned {run.config.id} to current run")
        logger = logging.getLogger(f'AutomateSims.simulation_run_pipeline.Run{run.config.id}')
        run.config.id = run_id

    logger.setLevel(logging.INFO)

    logger.info(f"Beginnning pipeline run.")
    logger.info(f'Simulation type is {run.config.sim_type}')
    

    if run.config.sim_type == 'continued': 
        stdin, filename = generateSimulationStdinCont(run, logger=logger)
    elif run.config.sim_type == 'new':
        stdin, filename = generateSimulationStdinNovel(run, logger=logger)
    else:
        logger.error("Invalid simulation type provided, ending run")
        run.config.status = 'FINISHED_WITH_FAILURES'
        run = getSimulationRunById(run.config.id)
        run.config.completion_time = str(datetime.datetime.now())
        updateRunInDatabase(run)
        logger.info(f'Finished run {run.config.id}')
        return


    root = os.getcwd()
    BIN_NAME = 'PFI_fast.out'
    path = os.path.join(root, BIN_NAME)

    p = runExecutableWithStdIn(path, stdin)
    ProcessWatcher(run, p, ["SIMULATING", "AWAITING_POST_PROCESSING"])
    logger.info(f"Completed simulation step")

    logger.info(f'Compressing files')
    output_files = get_output_file_names(run)
    logger.info(f'Found {len(output_files)} files. Like {output_files[:1]}')
    compress_files(output_files, run, logger=logger)
    
    ps = []
    vizInputs = generateVisualizationStdin(run, logger=logger)
    for _ in range(5):
        p = runExecutableWithStdIn(['octave-cli', os.path.join(root, f'Visualize_multiprocess.m')], vizInputs)
        ps.append(p)
    logger.info(f'Running {len(ps)} concurrently.')
    logger.info(ps)

    pws = []
    for p in ps[::-1]:
        pw = ProcessWatcher(run, p, ["IMAGE_GENERATION", "COMPLETED"], blocking=False)
        pws.append(pw)
    for pw in pws:
        while not pw.done:
            time.sleep(1)

    logger.info(f"Completed image generating step")

    failures = images_to_video(filename)

    logger.info(f"Completed video generating with {failures} failures.")

    if len(glob.glob(f'{run.name}*.zip')):
        deleteLeftoverFiles(filename)
        logger.info(f"Removed leftover files for run")
    else:
        logger.info(f"Could not find compressed file. Keeping leftover files.")

    ps.clear()

    # Mark the run as completed.
    # TODO: Move this somewhere where the logic makes sense.
    if failures > 0:
        run.config.status = 'FINISHED_WITH_FAILURES'
    run = getSimulationRunById(run.config.id)
    run.config.completion_time = str(datetime.datetime.now())
    updateRunInDatabase(run)
    logger.info(f'Finished run {run.config.id}')
