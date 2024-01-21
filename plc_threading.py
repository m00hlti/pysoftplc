import time
from threading import Thread
from functools import partial

_init_functions = []
_loop_functions = []
_loop_threads = []

def _parametrized(dec):
    """
    Just a generalized helper for setting up the correct decorators
    """
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

@_parametrized
def plc_init_func(func):
    """
    Decorator for all initialization functions
    """
    _init_functions.append(func)    
    return func

@_parametrized
def plc_loop_func(func, waiting_time):
    """
    Decorator for all PLC loops
    """
    _loop_functions.append((func, waiting_time))    
    return func

def _plc_thread(func: callable, pause: int):
    """
    This is the main strucutre all threads are running in
    """
    while True:
        start = time.time()
        func()
        end = time.time()
        time_elapsed = end-start
        if time_elapsed > pause:
            print("Warning, execution time ({0}) is longer then the pause ({1})".format(time_elapsed, pause))
        else:
            time.sleep(pause - (end-start))

def run_init_funcs():
    """
    This function is used to run all the initialization tasks
    """
    for t in _init_functions:
        t()

def start_loop_threads():
    """
    Create threads for all looops and let them run in parallel
    """
    def spawn_thread(func: callable, pause: int):
        t = Thread(target=_plc_thread, args=(func, pause))
        _loop_threads.append(t)
        t.start()                
    
    for func, sleep in _loop_functions:
        spawn_thread(func, sleep)


def finish_loop_threads():
    """
    Catch all the threads when they stop
    """
    # Just Cleanup
    for t in _loop_threads:
        t.join()
