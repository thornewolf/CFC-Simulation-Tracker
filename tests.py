from simulation_run_utils import SimulationRun
from simulation_run_pipeline import runExecutableWithStdIn

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
    '''
    Tests that the function runs without errors. Could check output specifically, but my testing is
    not that involved.
    '''
    run1 = SimulationRun(None, "QUEUED", datetime.datetime.now(), 2100, 299, 399, 120, 130, 0.001, 0.007, 1.8, 1e-3, 1e-5, 20)
    generateSimulationStdin(run1)