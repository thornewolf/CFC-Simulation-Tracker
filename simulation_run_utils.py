from dataclasses import dataclass
import json
import datetime

class SimulationRun:
    def __init__(self, *args, inline=False, as_json=None, **kwargs):
        if inline:
            self.config = SimulationRunConfig(*args, **kwargs)
        elif as_json:
            self.config = SimulationRunConfig(**json.loads(as_json))
        else:
            self.config = SimulationRunConfig()

    def __repr__(self):
        return self.json

    def __eq__(self, other):
        return self.json == other.json

    @property
    def json(self):
        return json.dumps({
            'id': self.config.id,
            'status': self.config.status,
            'date_created': str(self.config.date_created),
            'reynolds': self.config.reynolds,
            'mesh_n': self.config.mesh_n,
            'mesh_m': self.config.mesh_m,
            'jet_start': self.config.jet_start,
            'jet_end': self.config.jet_end,
            'jet_amp': self.config.jet_amp,
            'jet_freq': self.config.jet_freq,
            'a_tilde': self.config.a_tilde,
            'dt': self.config.dt,
            'tolerance': self.config.tolerance,
            'bcs': self.config.bcs,
            'continued_run': self.config.continued_run,
            'additional_steps': self.config.additional_steps,
            'time_between_reports': self.config.time_between_reports,
            'iterations_between_writes': self.config.iterations_between_writes
        }, indent=1)

@dataclass
class SimulationRunConfig:
    id: int = None
    status: str = None
    date_created: datetime.datetime = None
    reynolds: int = None
    mesh_n: int = None
    mesh_m: int = None
    jet_start: int = None
    jet_end: int = None
    jet_amp: float = None
    jet_freq: float = None
    a_tilde: float = None
    dt: float = 1e-3
    tolerance: float = None
    bcs: int = None
    continued_run: str = None
    additional_steps: int = 1000
    time_between_reports: int = 100
    iterations_between_writes: int = 500

'''
print(SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True).config)
print(SimulationRun(inline=True).config)
run = SimulationRun(None, "COMPLETED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20, inline=True)
print(run.json)
print(SimulationRun(as_json=run.json).json)
print(SimulationRun(as_json='{"jet_end": 10}').json)
'''