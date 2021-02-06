from dataclasses import dataclass
import json
import datetime

class SimulationRun:
    '''
    A large dataclass designed to assist in moving all information pertaining
    to a single simulation run around.  Offsers a large set of utility
    functions for ease of development.
    '''
    def __init__(self, *args, inline=False, as_json=None, **kwargs):
        '''
        Initialize the class.

        Args:
            *args: inline arguments to be passed directly into a
            SimulationRunConfig object.
            inline: indicate whether *args is fully complete and should be
            passed down to SimulationRunConfig.
            as_json: An optional json String to load the configuration for
            the run from.
            **kwargs: keywork arguments to be passed to SimulationRunConfig.

        Returns:
            Implicitly returns the class.
        '''
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
            'time_steps': self.config.time_steps,
            'additional_steps': self.config.additional_steps,
            'time_between_reports': self.config.time_between_reports,
            'iterations_between_writes': self.config.iterations_between_writes,
            'completion_time': self.config.completion_time,
            'sim_type': self.config.sim_type
        }, indent=1)

    @property
    def name(self):
        '''
        Allows for runs to handle the formatting in which they should be named.
        '''
        ans = ''
        if self.config.continued_run is not None:
            ans = f'Run{self.config.id}_JetA{self.config.jet_amp}_JetF{self.config.jet_freq}'
        else:
            ans = f'Run{self.config.id}_JetA{self.config.jet_amp}_JetF{self.config.jet_freq}'
        ans = ans.replace('.','p')
        ans = ans.replace(' ','_')
        return ans
    
    @property
    def runtime(self):
        '''
        Calculate total runtime
        '''
        # TODO: time since creation is not runtime. It should be time since
        # start. Need additional data within the config.
        if self.config.completion_time is None:
            d = datetime.datetime.now() - self.datetime_created
        else:
            d = self.datetime_completed - self.datetime_created
        return f'{d.total_seconds()//3600:.0f}h {(d.total_seconds()%3600)//60:.0f}m {d.total_seconds()%60:.0f}s'

    @property
    def datetime_created(self):
        return datetime.datetime.fromisoformat(self.config.date_created)

    @property
    def datetime_completed(self):
        return datetime.datetime.fromisoformat(self.config.completion_time)

    @property
    def sim_type(self):
        return self.config.sim_type

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
    time_steps: int = 1000
    additional_steps: int = 1000
    time_between_reports: int = 100
    iterations_between_writes: int = 500
    completion_time: datetime.datetime = None
    sim_type: str = None
