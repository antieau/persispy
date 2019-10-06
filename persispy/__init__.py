# -*- coding: utf-8 -*-

__author__ = 'Benjamin Antieau'
__email__ = 'benjamin.antieau@gmail.com'
__version__ = '0.0.1'

__all__ = []

import pkgutil
import inspect
try:
    from matplotlib import use
    use('TKAgg')
except ImportError:
    print("Matplotlib is not currently installed. Plot functions are unavailable.")


for loader, name, is_pkg in pkgutil.walk_packages('__path__'):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)
