# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 11:39:19 2021

@author: OWP
"""

#%%

from . import misc
from . import plot
from . import print
from . import figure
from . import legacy


# Plotting
from .plot import plotxy as multiplot   # or rename in plot.py directly
from .plot import plot3d

# Layout / figure tools
from .figure import layout, subplot, axistight, size, tile

# Saving / printing
from .print import savefig

# Optional: small utilities you commonly use
from .misc import color

__all__ = [
    'multiplot',
    'plot3d',
    'layout',
    'subplot',
    'axistight',
    'size',
    'tile',
    'savefig',
    'color',
    'legacy'
]
