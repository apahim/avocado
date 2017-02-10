import os
import pickle
import sys

from multiprocessing import queues


def _dumps(function):
    return pickle.dumps(function)


class SimpleQueue(queues.SimpleQueue):

    def func_at_exit(self, function, args, kwargs, once=False):
        module_path = sys.modules.get(function.__module__).__file__
        module_dir = os.path.abspath(os.path.dirname(module_path))
        self.put({'func_at_exit': _dumps(function),
                  'args': args,
                  'kwargs': kwargs,
                  'once': once,
                  'modulePath': module_dir})
