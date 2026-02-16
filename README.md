# plotops

Structured plotting utilities built on top of matplotlib.

`plotops` provides:

- Reproducible subplot layouts (cm-based sizing)
- Clean multi-source plotting
- Publication-ready figure control
- Interactive workflow tools (log toggle, pop-out, tiling)

Designed for engineering and scientific workflows where layout consistency matter.

---

## Core Modules

### `plotops.figure`

Layout and figure control:

- `layout()` – compute figure size and normalized layout parameters
- `subplot()` – tight subplot creation
- `axistight()` – MATLAB-style axis padding
- `size()` – resize/position figure window
- `tile()` – tile all open figures on screen
- `log_toggle()` – interactive log/linear toggle
- `enable_popout()` – pop active axes into new figure

---

### `plotops.plot`

High-level plotting utilities:

- `plotxy()` – multi-source row-wise plotting
- `plot3d()` – structured plotting of 3D matrices
- `corr()` – covariance → correlation matrix
- `surfiso()` – triangulated 3D surface with isolines

---

## Example

```python
#%% Test plot 2D
import numpy as np
import matplotlib.pyplot as plt
import plotops

plt.close('all')

# x-data (different sampling per source)
x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)
x3 = np.linspace(0, 10, 200)

# Each source: 2 signals (rows)
y1 = np.vstack((200*np.cos(x1)+201,
                30*np.cos(x1)**2+50))

y2 = np.vstack((200*np.sin(x2)+201,
                30*np.sin(x2)+50))

y3 = np.vstack((-10*np.sin(2*x3)+20,
                800*np.sin(x3)+799.99))

# Layout: 1 row, 2 columns
fig_layout = plotops.figure.layout(1, 2)

fig_out = plotops.plot.plotxy(
    [x1, x2, x3],          # sources
    [y1, y2, y3],
    labels=['case A', 'case B', '$case C$'],
    xlabel='t [s]',
    ylabel=[f'$Y_{i+1}$ [kN]' for i in range(2)],
    suptitle='Main title',
    legend=True,
    cursor=True,
    ncols=2,
    ylog=False,
    layout_kwargs=fig_layout
)

# Save figure (cm-accurate sizing)
plotops.print.savefig(
    fig_out['fig'],
    'plot_test_2c',
    '.',
    figsize=fig_layout['figsize']
)
