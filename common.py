from tempfile import TemporaryDirectory
from diskcache import Cache
from playhouse.dataset import DataSet
import subprocess
import json
import numpy as np
from copy import deepcopy

class BayesianStdMean:
    """
    A class which calculates the mean, var, std using quasi-bayesian method in order to save memory.
    It adds to the mean iteratively while decaying the running mean by the amount of window that would be added
    """
    
    def __init__(self, initial_sample: np.ndarray):
        self.window = 1
        self.mean = initial_sample
        self.var = np.zeros_like(initial_sample)
        self.std = np.zeros_like(initial_sample)
    
    def update(self, add: np.ndarray):
        self.window += 1
        p = (self.window-1)/self.window
        pmean = deepcopy(self.mean)
        self.mean = pmean*p + add/self.window
        
        #asciimath 1/N(x_N^2 + (N-1)(v + mu_1^2)) - mu_2^2
        self.var = np.abs((add**2 + (self.window-1)*(self.var+pmean**2))/self.window - self.mean**2)
        self.std = np.sqrt(self.var)


class DiskBayesianStdMean:
    def __init__(self, cache: Cache, key: str):
        self.cache = cache
        self.key = key

    def update(self, add: np.ndarray):
        with self.cache.transact():
            tracker = self.cache.get(self.key)
            if tracker is None:
                tracker =  BayesianStdMean(add)
            else:
                tracker.update(add)
            self.cache[self.key] = tracker

    def get(self) -> BayesianStdMean:
        return self.cache.get(self.key)
    
    def __str__(self) -> str:
        tracker = self.get()
        return f'Mean: {tracker.mean}, std: {tracker.std}'
       

def run_db_bench(name, fn, setup_fn = None, runner = None):
    if runner is None:
        runner = Runner()

    run_store = Cache('./rundata/')
    with TemporaryDirectory() as tmpdir:
        extra_args = tuple()
        if setup_fn is not None:
            extra_args = setup_fn(tmpdir)
            if extra_args is None:
                extra_args = tuple()
            elif type(extra_args) not in [list, tuple]:
                extra_args = (extra_args,)

        runner.bench_func(name, fn, tmpdir, *extra_args)

        dust_data = subprocess.check_output(['dust', '-j', tmpdir])
        storage_data = json.loads(dust_data)
        avg_store = DiskBayesianStdMean(run_store, f'{name}:storage')
        if not runner.args.quiet:
            avg = avg_store.get()
            print(f'Storage usage: {round(avg.mean/1024)}KB std: {round(avg.std/1024)}KB')
        else:
            avg_store.update(storage_data['size'])
