# AGENTS.md

## Plotting Standard

Use `plotops` for matplotlib-based plotting in this repository.

The goal is to keep:
- subplot layout consistent across figures
- figure sizes reproducible
- multi-panel plots easy to read and compare
- saving/export behavior uniform across scripts and modules

Do not hand-build subplot spacing with repeated `plt.subplots_adjust(...)` unless there is a strong reason. Prefer `plotops` layout utilities first.

## Preferred Imports

Use:

```python
import plotops
```

Preferred top-level functions:
- `plotops.layout`
- `plotops.subplot`
- `plotops.multiplot`
- `plotops.plot_timefreq`
- `plotops.plot3d`
- `plotops.savefig`

Avoid importing deep internals unless needed for a specific reason.

## Core Logic

`plotops` separates plotting into two layers:

1. Layout layer
   `plotops.layout(nrow, ncol, ...)`
   computes figure size and normalized spacing.

2. Axes creation / plotting layer
   - `plotops.subplot(...)` creates axes using the layout
   - `plotops.multiplot(...)` creates standard row-wise multi-source plots directly
   - `plotops.plot_timefreq(...)` creates standard 2-column time/FFT plots
   - `plotops.plot3d(...)` flattens 3D matrix-style data into a subplot grid

This means:
- if the code needs custom plotting logic, use `layout()` + `subplot()`
- if the code matches the standard “same x-type data, several sources, one signal per subplot row” pattern, use `multiplot()`
- if the code matches a standard time-domain plus FFT comparison pattern, prefer `plot_timefreq()`
- if the input is matrix-style 3D data, prefer `plot3d()`

## Typical Use

### Pattern A: custom figure logic

Use this when you want full control over what is drawn in each axis.

```python
import plotops

layout = plotops.layout(2, 1)
axes, fig, _ = plotops.subplot(
    2,
    1,
    layout=layout,
    xlabel="t [s]",
    ylabel=["Signal 1", "Signal 2"],
    ylog=False,
    xlog=False,
    suptitle="Main title",
    grid=True,
)

axes[0, 0].plot(x, y1)
axes[1, 0].plot(x, y2)
```

Use this pattern when:
- each subplot has different custom drawing logic
- you need annotations, mixed plot types, or special axis handling
- you are building figures manually

Pass shared axis/figure settings such as `xlabel`, `ylabel`, `xlog`, `ylog`, `suptitle`, and `grid` directly into `plotops.subplot(...)` when available, instead of setting them afterwards axis by axis.

### Pattern B: standard multi-source line plots

Use this for the common case:
- several data sources
- one or more signals
- one subplot per signal
- one line per source in each subplot

```python
import plotops

layout = plotops.layout(2, 1)

fig_out = plotops.multiplot(
    x_list=[x_a, x_b],
    y_list=[y_a, y_b],
    labels=["Case A", "Case B"],
    xlabel="t [s]",
    ylabel=["Response 1", "Response 2"],
    layout_kwargs=layout,
)
```

Use this pattern by default for comparison plots.

### Pattern C: matrix-style 3D data

Use `plotops.plot3d(...)` when data is shaped like:
- `(nrow, ncol, npoints)`

This produces a subplot grid automatically.

```python
fig_out = plotops.plot3d(
    [x1, x2],
    [A, B],
    xlabel="f [Hz]",
    labels=["Measured", "Model"],
    layout_kwargs=plotops.layout(2, 3),
)
```

## Preferences

### Prefer `layout()` before plotting

Create layout explicitly when figure shape matters.

```python
layout = plotops.layout(nrow, ncol)
```

Pass it forward as:
- `layout=layout` to `plotops.subplot(...)`
- `layout_kwargs=layout` to `plotops.multiplot(...)` or `plotops.plot3d(...)`

This is preferred over relying on default spacing when writing project code that should stay visually consistent.

### Prefer `multiplot()` for repeated comparison plots

If the plot is fundamentally:
- same kind of x-axis
- same signals across datasets
- one legend for several sources

then prefer `plotops.multiplot()` over manual loops.

### Prefer project-level labels and units

Set:
- `xlabel`
- `ylabel`
- `labels`

explicitly in repository code. Do not rely on generic defaults like `x`, `y_1`, `y_2` unless it is quick exploratory code.

### Prefer repository scripts to save with `plotops.savefig()`

Use:

```python
plotops.savefig(fig, "figure_name", folder=out_dir, figsize=layout["figsize"])
```

This keeps export sizing and formatting consistent.

## Return Types and Outputs

### `plotops.layout(...)`

Returns a `dict`.

Typical keys:
- `"figsize"`: `(height_cm, width_cm)`
- `"subsize_cm"`: `(axis_height_cm, axis_width_cm)`
- `"gap_cm"`
- `"marg_h_cm"`
- `"marg_w_cm"`
- `"gap"`: normalized spacing
- `"marg_h"`: normalized vertical margins
- `"marg_w"`: normalized horizontal margins

Use this dict as configuration input for subplot creation and saving.

### `plotops.subplot(...)`

Returns:

```python
axes, fig, pos = plotops.subplot(...)
```

Where:
- `axes` is a 2D NumPy object array of matplotlib axes handles with shape `(nrow, ncol)`
- `fig` is a matplotlib figure handle
- `pos` is a `list` of `[left, bottom, width, height]` normalized axis positions

Use this when you need direct access to axes handles.

### `plotops.multiplot(...)`

Returns a `dict` named here as `fig_out`.

Important keys:
- `"fig"`: the main matplotlib figure handle
- `"axes"`: axes handles for the first figure
- `"lines"`: plotted line handles for the first figure
- `"meta"`: metadata dict

Typical metadata includes:
- `"n_source"`
- `"n_signal"`
- `"ncols"`
- `"ylog"`
- `"labels"`
- `"ylabel"`

Preferred use:

```python
fig_out = plotops.multiplot(...)
fig = fig_out["fig"]
axes = fig_out["axes"]
```

Treat `fig_out` as the standard returned object for high-level plotting.

### `plotops.plot3d(...)`

Returns the same kind of output dict as `plotops.multiplot(...)`.

### `plotops.savefig(...)`

Does not return a plot object to build on. Treat it as an export function with side effects:
- resizes figure for export
- writes files to disk
- may open the first saved file by default

## Data Shape Conventions

### For `multiplot()`

`x_list`:
- one 1D array per source, or one shared 1D array reused for all sources

`y_list`:
- one 2D array per source
- shape is `(nsignal, npoints)`

Interpretation:
- each row in each `y` array becomes one subplot
- each source contributes one line in each subplot

If a source has only one signal, a 1D array is acceptable and is promoted internally to shape `(1, npoints)`.

### For `plot3d()`

Each `y` input must be 3D:
- shape `(nrow, ncol, npoints)`

Interpretation:
- the first two dimensions define subplot grid placement
- the last dimension is the curve over x

## Usage Rules for Codex

When creating or updating plotting code in this repository:

1. Prefer `plotops` over ad hoc matplotlib layout code.
2. Prefer `plotops.layout()` for reproducible figure dimensions.
3. Prefer `plotops.multiplot()` for standard comparison plots.
4. Use `plotops.subplot()` when custom axes-by-axes plotting is needed.
5. Use `plotops.savefig()` for final exported figures.
6. Keep labels, units, and legend names explicit.
7. Preserve returned handles (`fig`, `axes`, `fig_out`) when later code may need editing, annotations, or saving.

## When Not to Use `plotops`

Direct matplotlib is acceptable when:
- making a very unusual one-off visualization not matched by `plotops`
- plotting non-standard artist types where `plotops` adds no value
- a library callback/API requires native matplotlib object creation in a special way

Even in those cases, still consider `plotops.layout()` for figure sizing and spacing.

## Recommended Default Pattern

For most repository plots, start from this template:

```python
import plotops

layout = plotops.layout(nrow, ncol)

fig_out = plotops.multiplot(
    x_list=x_list,
    y_list=y_list,
    labels=labels,
    xlabel=xlabel,
    ylabel=ylabel,
    layout_kwargs=layout,
)

plotops.savefig(
    fig_out["fig"],
    filename,
    folder=folder,
    figsize=layout["figsize"],
)
```

If the plot needs custom drawing, use:

```python
import plotops

layout = plotops.layout(nrow, ncol)
axes, fig, _ = plotops.subplot(
    nrow,
    ncol,
    layout=layout,
    xlabel=xlabel,
    ylabel=ylabel,
    xlog=xlog,
    ylog=ylog,
    suptitle=suptitle,
    grid=grid,
)
```

and then build the plot manually on `axes`.
