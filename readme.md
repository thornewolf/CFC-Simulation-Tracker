## Overview
CFC Simulation Tracker (CST) is a project purposed to increase the levels of automation associated with running Computational Flow Calculations using Dr. Morris' PhD Fortran code.
This project is research code and not purposed to be applied in a production environment.

This project provides a front end "dashboard" for researchers to manage configurations for simulations and minimize human involvement with running simulations. It manages running the team's Fortran code. The Fortran code simulates Computational Fluid Dynamics (CFD) and Computational Fluid Control (CFC) using synthetic jet actuators.

## Installation

There are two primary toolchains used in CST. A Python toolchain and a Fortran toolchain. The Fortran toolchain will not be described here as it typically is a one-time involvement for compiling the relatively stagnant fortran code. For the Python toolchain you will need to install all dependencies listed in requirements.txt.

```
python -m pip install -r requirements.txt
```

## Usage

## Dashboard Code ##

To startup the dashboard you will need to be running both the dashboard and the run manager. The dashboard is the frontend of this project and the run manager is the backend.

You can start either with
```
python dashboard.py
python continually_run_sims.py
```

Both will need to be running concurrently for the pipeline to function properly.

## Fortran Code ##

If you desire to run the fortran compiles code you will be prompted for a few configuration options to get your simulation running. You can see how the standard input that is passed to the fortran code is constructed in `simulation_run_pipeline.py`.

An example generated stdin is

```
2
simtocont
n
y
120
130
0.001
0.007
0.001
1000
100
Run12_ReNone_JetA0p001_JetF0p007pstate
500
y
```

These are a sequence of parameters that are passed to the binary. They answer the following questions:
```
(1) start simulation (2) continue simulation (3) exit
name of the simulation you want to continue
do you want to change simulation parameters?
do you want to change jet parameters
where should the jet start?
where should the jet end?
Jet amplitude
Jet frequencty
timesteps to iterate
timesteps between reports
output file name
timesteps between writing simulation state to a file
start simulation?
```

Don't worry about `simtocont`. That is just the name of the file that was continues in this specific case. If you want to start a fresh simulation and are looking for some reasonable input parameters consider the following.
```
Reynolds: 800
N = 400
M = 800
Grid lines = 40
dt = 0.0035
tolerance = 1e-5
Iterations = 100000
Iterations between reports = 50
Iterations between writes = 100
```

If a simulation seems slow at first such that you think it will take a really long time to finish, give it some time to converge. It takes longer to integrate when flow is unsteady. (this is also a way to tell how effective a jet configuration is)