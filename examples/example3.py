import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

import plotops


plt.close("all")

x = np.linspace(0, 10, 100)
y1 = 20 * np.random.randn(6, 100)
y2 = 20 * np.random.rand(6, 100) + 10

fig_layout = plotops.figure.layout(2, 3)

fig_out = plotops.plot.plotxy(
    x_list=[x],
    y_list=[y1, y2],
    ncols=3,
    suptitle="Main title",
    legend=False,
    layout_kwargs=fig_layout,
)

plotops.print.savefig(
    fig_out["fig"],
    "plot_example_3",
    ".",
    figsize=fig_layout["figsize"],
    formats=["pdf", "png"],
)
