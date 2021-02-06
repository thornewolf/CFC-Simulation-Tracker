import multiprocessing 
import time
import datetime

from db import getFirstQueuedRun,getAllSimulationRuns,updateRunInDatabase
from simulation_run_pipeline import pipeline as simulation_pipeline

JOB_COUNT = 2

def main():
    '''
    Manager function for continually queueing runs. Kicks off processes that
    can exist on different CPU cores from one another.
    '''
    jobs = []
    while True:
        
        # Simulations that were not completed markes as CANCELLED/FAILED and runtime stopped
        runs = getAllSimulationRuns() 
        for x in runs:
            run = runs[x]
            if run.config.status != ['COMPLETED','QUEUED','FINISHED_WITH_FAILURES']:
                run.config.status = 'CANCELLED/FAILED'
                run.config.completion_time = str(datetime.datetime.now())
                updateRunInDatabase(run)
                

        next_job = getFirstQueuedRun()
        while next_job is not None and len(jobs) < JOB_COUNT:
            print('next job is', next_job)
            # Kick off a simulation pipeline that can cross CPU cores.
            p = multiprocessing.Process(target=simulation_pipeline, args=(next_job,))
            p.start()
            jobs.append(p)
            time.sleep(3)
            next_job = getFirstQueuedRun()

        # Wait for all jobs to finish then reset.
        for job in jobs:
            job.join()
        jobs.clear()

        time.sleep(10)

if __name__ == '__main__':
    main()
