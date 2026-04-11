# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 21:32:25 2025

@author: oyvinpet
"""

#%%
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import plotops

#%%

plt.close('all')
n1, n2 = 40, 50
x1 = np.linspace(0.1, 10.0, n1)
x2 = np.linspace(0.2, 6.0, n2)
X1, X2 = np.meshgrid(x1, x2, indexing='ij')
F = np.sin(X1) * np.cos(0.7 * X2) + 0.2 * X1

x = np.column_stack([X1.ravel(), X2.ravel()])
f = F.ravel()

plt.figure()

plotops.plot.surfiso(x, f, xlabel='x1',ylabel='x2',zlabel='f',isolines=20,cmap='coolwarm',markercolor=[0,0,0],facealpha=0.85,view=(40, 15))

# cbar=True,
# markersize=None)
