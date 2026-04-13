# plotops

Structured plotting utilities built on top of matplotlib.

`plotops` provides:

- Reproducible subplot layouts with cm-based sizing
- Clean multi-source plotting helpers
- Publication-ready export utilities
- Interactive workflow tools such as log toggle, pop-out, and tiling

Designed for engineering and scientific workflows where layout consistency matters.

## Install

```bash
pip install plotops
```

Current runtime dependencies:

- `numpy`
- `matplotlib`
- `mplcursors`
- `PyQt5`

## Core Modules

### `plotops.figure`

Layout and figure control:

- `layout()` computes figure size and normalized layout parameters
- `subplot()` creates tightly controlled subplot grids as a 2D axes array and can apply labels, log scaling, limits, and grids
- `finish()` applies standard post-plot finishing for custom subplot workflows
- `axistight()` applies MATLAB-style axis padding
- `size()` resizes and repositions the figure window
- `tile()` tiles all open figures on screen
- `log_toggle()` toggles linear and log scale interactively
- `enable_popout()` pops the active axes into a new figure

### `plotops.plot`

High-level plotting utilities:

- `plotxy()` creates multi-source row-wise plots and accepts `suptitle=...`
- `plot_timefreq()` creates 2-column time/FFT subplot grids and supports the same common plotting arguments as `plotxy()` such as `suptitle=...`, plus time/FFT-specific options
- `plot3d()` flattens 3D matrix data into structured subplot layouts
- `corr()` converts covariance matrices to correlation plots
- `surfiso()` plots triangulated 3D surfaces with isolines

`plotxy(..., return_all=True)` returns all generated figures, axes groups, and line groups when one call spans multiple figures.

`plotxy()` accepts either one shared x-array per source or one x-array per subplot row, which allows wrappers such as `plot_timefreq()` to reuse the same legend and layout behavior.

The top-level alias `plotops.multiplot(...)` points to `plotxy()`, so it also supports `suptitle=...`.

### `plotops.legacy`

Legacy APIs are kept in `plotops.legacy` so older workflows remain available without crowding the main modules.

## Quickstart

```python
import numpy as np
import plotops

x1 = np.linspace(0, 10, 100)
x2 = np.linspace(0, 10, 400)
y1 = 20 * np.cos(x1) + 40
y2 = 20 * np.sin(x2) + 50

fig_layout = plotops.figure.layout(1, 1)

fig_out = plotops.plot.plotxy(
    [x1, x2],
    [y1, y2],
    labels=["Case A", "Case B"],
    suptitle="Main title",
    layout_kwargs=fig_layout,
)

plotops.print.savefig(
    fig_out["fig"],
    "plot_example_1",
    ".",
    figsize=fig_layout["figsize"],
    formats=["pdf", "png"],
)
```

## Manual Plotting

For cases where you want the layout helper but will add lines or scatter plots manually:

```python
layout = plotops.layout(2, 1)
axes, fig, _ = plotops.subplot(
    2, 1,
    layout=layout,
    xlabel="t [s]",
    ylabel=["Signal 1", "Signal 2"],
    ylog=False,
)

axes[0, 0].plot(x, y1)
axes[1, 0].scatter(x, y2)

plotops.finish(
    fig,
    axes,
    suptitle="Main title",
)
```

`plotops.finish()` is the recommended way to give custom subplot-based figures the same kind of post-plot behavior that high-level helpers already provide automatically, including axis tightening, figure-level legend placement, hiding unused padded axes, cursor hookup, and interactive figure helpers.

## Time And Frequency

For repeated "time on the left, FFT on the right" plots, use `plot_timefreq()`:

```python
fig_layout = plotops.layout(2, 2)

fig_out = plotops.plot_timefreq(
    [t_a, t_b],
    [y_a, y_b],
    labels=["Case A", "Case B"],
    ylabel=["Response 1", "Response 2"],
    suptitle="Main title",
    layout_kwargs=fig_layout,
)
```

This keeps the same legend/layout behavior as `plotxy()` while internally building one time row and one positive-frequency FFT row per signal. In practice, `plot_timefreq()` supports the common `plotxy()` options such as `labels`, `color`, `linestyle`, `linewidth`, `legend`, `layout_kwargs`, and `suptitle`, and adds time/frequency-specific arguments such as `time_xlabel`, `freq_xlabel`, `fft_ylabel`, `time_xlim`, `freq_xlim`, and `ylog_freq`.

## Examples

The example scripts live in [examples](examples):

- [example1.py](examples/example1.py): 2D plotting workflows
- [example2.py](examples/example2.py): surface and isoline plotting
- [example3.py](examples/example3.py): matrix-style subplot layouts
- [example4.py](examples/example4.py): 3D matrix plotting

Example outputs:

<img src="examples/plot_example_1.png" width="500">
<img src="examples/plot_example_2.png" width="500">
<img src="examples/plot_example_3.png" width="1200">
<img src="examples/plot_example_4.png" width="1200">

