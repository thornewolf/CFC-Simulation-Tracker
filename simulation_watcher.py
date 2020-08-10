import time

class ProcessWatcher:
    def __init__(self, run, run_process):
        self.run = run
        self.run_process = run_process
        self.log = []

        self.begin_watching()

    def begin_watching(self):
        for line in self.run_process.stdout:
            self.log.append(line)
            print(f'Just saw this pop up for {self.run.id}: {line}')