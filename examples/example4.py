import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import plotops


plt.close("all")

x = np.linspace(0, 2, 100)
A = np.zeros([2, 3, 100])

A[0, 0, :] = 1e1 * np.exp(-x)
A[0, 1, :] = 1e2 * np.exp(-2 * x)
A[0, 2, :] = 1e3 * np.exp(-3 * x)
A[1, 0, :] = 1e1 * np.exp(-x)
A[1, 1, :] = 1e1 * np.exp(-2 * x)
A[1, 2, :] = 1e1 * np.exp(-3 * x)

B = A + 2.0

x2 = np.linspace(0, 2, 200)

C = np.zeros([2, 3, 200])
C[0, 0, :] = 1e1 * np.exp(-x2**2)
C[0, 1, :] = 1e2 * np.exp(-x2 - x2**2)
C[0, 2, :] = 1e3 * np.exp(-x2 - x2**2)
C[1, 0, :] = 1e1 * np.exp(-x2**0.5)
C[1, 1, :] = 1e1 * np.exp(-2 * x2**0.5)
C[1, 2, :] = 1e1 * np.exp(-3 * x2**0.5)

fig_layout = plotops.figure.layout(2, 3)

fig_out = plotops.plot.plot3d(
    [x, x, x2],
    [A, B, C],
    xlabel="f [Hz]",
    linewidth=[1, 2, 1],
    labels=["Data", "Num", "Test series"],
    linestyle=["-", "--", "-"],
    ylog=True,
    layout_kwargs=fig_layout,
)

plotops.print.savefig(
    fig_out["fig"],
    "plot_example_4",
    ".",
    figsize=fig_layout["figsize"],
    formats=["pdf", "png"],
)
