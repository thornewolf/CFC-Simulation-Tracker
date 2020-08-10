from dataclasses import dataclass
import datetime

@dataclass
class SimulationRun:
    id: int
    status: str
    date_created: datetime.datetime
    reynolds: int
    mesh_n: int
    mesh_m: int
    jet_start: int
    jet_end: int
    jet_amp: float
    jet_freq: float
    a_tilde: float
    dt: float
    tolerance: float
    bcs: int