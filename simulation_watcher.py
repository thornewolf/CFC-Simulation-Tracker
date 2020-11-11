import time
import logging
from db import addSimulationRunToDatabase, updateRunStatusById

class ProcessWatcher:
    '''
    Keeps track of the state of a run and will post updates on it. Recognizes when the process has
    begun and when it has ended.
    '''
    def __init__(self, run, run_process, stages):
        '''
        Initialize the class.

        Args:
            self: The class itself.
            run: The run that is associated with the process.
            run_proecess: The process that is being tracked and observed.
            stages: List[String] What to label the mid-process and post-process
            states.
        '''
        self.logger = logging.getLogger(f"AutomateSims.simulation_watcher.Run{run.config.id}")
        self.logger.setLevel(logging.INFO)
        self.run = run
        self.run_process = run_process
        self.log = []
        self.stages = stages
        self.begin_watching()

    def begin_watching(self):
        updateRunStatusById(self.run.config.id, self.stages[0])
        for line in self.run_process.stdout:
            line = line.strip()
            self.log.append(line)
            self.logger.info(line)
        updateRunStatusById(self.run.config.id, self.stages[1])