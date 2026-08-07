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
- `plotops.subplots`
- `plotops.finish`
- `plotops.multiplot`
- `plotops.plot_timefreq`
- `plotops.plot3d`
- `plotops.savefig`
- `plotops.close`

Avoid importing deep internals unless needed for a specific reason.

## Core Logic

`plotops` separates plotting into two layers:

1. Layout layer
   `plotops.layout(nrow, ncol, ...)`
   computes figure size and normalized spacing.

2. Axes creation / plotting layer
   - `plotops.subplot(...)` creates axes using the layout
   - `plotops.subplots(...)` combines `layout(...)` and `subplot(...)` for custom plotting setup
   - `plotops.finish(...)` applies standard post-plot finishing for custom subplot workflows
   - `plotops.multiplot(...)` creates standard row-wise multi-source plots directly
   - `plotops.plot_timefreq(...)` creates standard 2-column time/FFT plots
   - `plotops.plot3d(...)` flattens 3D matrix-style data into a subplot grid

This means:
- for custom plotting, prefer `plotops.subplots(...)` + custom drawing + `plotops.finish(...)`
- use the explicit `layout()` + `subplot()` form when the layout dictionary must be inspected, reused for export, or shared across figures
- if the code matches the standard “same x-type data, several sources, one signal per subplot row” pattern, use `multiplot()`
- if the code matches a standard time-domain plus FFT comparison pattern, prefer `plot_timefreq()`
- if the input is matrix-style 3D data, prefer `plot3d()`

## Typical Use

### Pattern A: custom figure logic

Use this when you want full control over what is drawn in each axis.

```python
import plotops

fig_out = plotops.subplots(
    2,
    1,
    layout_kwargs={"subsize": (3.0, 8.0)},
    xlabel="t [s]",
    ylabel=["Signal 1", "Signal 2"],
    ylog=False,
    xlog=False,
    grid=True,
)

fig = fig_out["fig"]
axes = fig_out["axes"]

axes[0, 0].plot(x, y1)
axes[1, 0].plot(x, y2)

plotops.finish(
    fig,
    axes,
    suptitle="Main title",
)
```

Use this pattern when:
- each subplot has different custom drawing logic
- you need annotations, mixed plot types, or special axis handling
- you are building figures manually

Pass shared axis settings such as `xlabel`, `ylabel`, `xlog`, `ylog`, `xlim`, `ylim`, and `grid` directly into `plotops.subplots(...)` when available, instead of setting them afterwards axis by axis. Then call `plotops.finish(...)` after custom plotting to apply the standard post-plot behavior that `plotxy()` would otherwise handle automatically, such as axis tightening, figure-level legend placement, hiding unused padded axes, cursor hookup, and interactive helpers.

`plotops.subplots(...)` accepts layout options inside its `layout_kwargs` dictionary. This differs from the high-level plotting functions, where `layout_kwargs` is the already computed dictionary returned by `plotops.layout(...)`.

For `plotops.subplot(...)` and `plotops.subplots(...)`, treat `ylabel` as supporting exactly these shapes:
- a single string for all axes
- a list of length `nrow` for one y-label per row across all columns
- a list of length `nrow * ncol` for one y-label per axis in row-major order

Example: on a 2-row subplot grid, `ylabel=["MSD", ""]` labels the first row and leaves the second row unlabeled.

For `xlim` and `ylim`:
- `None` leaves limits automatic
- one numeric `(min, max)` pair is broadcast to all axes
- a sequence of pairs applies one pair per axis in row-major order

For `grid`, pass one boolean for all axes or one boolean per axis. Enabled grid lines are drawn behind plotted data.

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
    suptitle="Main title",
    layout_kwargs=layout,
)
```

Use this pattern by default for comparison plots. `plotops.multiplot(...)` forwards `suptitle` to the underlying `plotxy()` implementation.

### Pattern C: time and frequency side-by-side

Use this for the common case:
- one time-domain subplot and one FFT subplot per signal
- several data sources compared in each row
- shared legend/layout behavior from `plotxy()`

```python
import plotops

layout = plotops.layout(2, 2)

fig_out = plotops.plot_timefreq(
    t_list=[t_a, t_b],
    y_list=[y_a, y_b],
    labels=["Case A", "Case B"],
    ylabel=["Response 1", "Response 2"],
    suptitle="Main title",
    layout_kwargs=layout,
)
```

Use this pattern when the left column is time series and the right column is the corresponding positive-frequency FFT. `plotops.plot_timefreq(...)` supports the same common plotting options as `plotxy()` and `multiplot()`, including `suptitle`, while also adding time/frequency-specific arguments such as `time_xlabel`, `freq_xlabel`, `fft_ylabel`, `time_xlim`, `freq_xlim`, and `ylog_freq`.

### Pattern D: matrix-style 3D data

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

### Choose the API by plot type

| Plot type | Preferred API |
|---|---|
| Standard source comparison | `plotops.multiplot()` |
| Time domain plus FFT | `plotops.plot_timefreq()` |
| Matrix-style 3D input | `plotops.plot3d()` |
| Custom artists or mixed plot types | `plotops.subplots()` + `plotops.finish()` |
| Inspected, reused, or shared layout | `plotops.layout()` + `plotops.subplot()` + `plotops.finish()` |

### Use explicit `layout()` when the layout object matters

For custom plots, `plotops.subplots(...)` computes the layout automatically. Create it explicitly when the layout dictionary must be inspected, reused, shared, or passed to `plotops.savefig(...)`.

```python
layout = plotops.layout(nrow, ncol)
```

Pass it forward as:
- `layout=layout` to `plotops.subplot(...)`
- `layout_kwargs=layout` to `plotops.multiplot(...)`, `plotops.plot_timefreq(...)`, or `plotops.plot3d(...)`

Do not confuse that high-level use with `plotops.subplots(layout_kwargs={...})`, where the dictionary contains arguments that will be forwarded to `plotops.layout(...)`.

This is preferred over relying on default spacing when writing project code that should stay visually consistent.

### Prefer `multiplot()` for repeated comparison plots

If the plot is fundamentally:
- same kind of x-axis
- same signals across datasets
- one legend for several sources

then prefer `plotops.multiplot()` over manual loops.

`plotops.multiplot()` also supports one x-array per subplot row when a wrapper or caller needs different x-values in different rows.

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

`ylabel` may be passed as:
- one string for all axes
- one string per row
- one string per axis in row-major order

Use this when you need direct access to axes handles.

### `plotops.subplots(...)`

Returns a `dict` containing:
- `"fig"`: the matplotlib figure handle
- `"axes"`: a 2D NumPy object array with shape `(nrow, ncol)`
- `"pos"`: normalized axes positions
- `"layout"`: the computed or supplied layout dictionary

Use this as the default setup for custom plotting. Supply layout options with `layout_kwargs={...}`, or pass an existing layout dictionary with `fig_layout=layout`. Do not pass both.

### `plotops.finish(...)`

Returns a `dict`.

Important keys:
- `"fig"`: the matplotlib figure handle
- `"axes"`: the input axes as a NumPy object array
- `"active_axes"`: flattened list of active axes used for finishing
- `"legend"`: the created figure-level legend artist, or `None`

Use this after `plotops.subplots(...)` or `plotops.subplot(...)` and custom plotting when you want standard finishing behavior without switching to `plotops.multiplot(...)`.

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

### `plotops.plot_timefreq(...)`

Returns the same kind of output dict as `plotops.multiplot(...)`.

It also accepts the same common plotting options as `plotops.multiplot(...)` / `plotxy(...)`, including `labels`, `color`, `linestyle`, `linewidth`, `legend`, `layout_kwargs`, and `suptitle`, plus time/frequency-specific options.

Important additional keys:
- `"time_lines"`: plotted time-domain line handles for the first figure
- `"freq_lines"`: plotted FFT line handles for the first figure

### `plotops.plot3d(...)`

Returns the same kind of output dict as `plotops.multiplot(...)`.

### `plotops.savefig(...)`

Does not return a plot object to build on. Treat it as an export function with side effects:
- resizes figure for export
- writes files to disk
- may open the first saved file by default

### `plotops.close(...)`

Closes matplotlib figures. `plotops.close()` defaults to closing all open figures; pass a figure, figure number, or figure name to close a specific target.

## Data Shape Conventions

### For `multiplot()`

`x_list`:
- one 1D array per source, or one shared 1D array reused for all sources
- optionally one 1D array per subplot row for each source

`y_list`:
- one 2D array per source
- shape is `(nsignal, npoints)`
- optionally one 1D array per subplot row for each source

Interpretation:
- each row in each `y` array becomes one subplot
- each source contributes one line in each subplot

If a source has only one signal, a 1D array is acceptable and is promoted internally to shape `(1, npoints)`.

If row-wise `x_list` and `y_list` are used, each x-row must match the length of its corresponding y-row.

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
4. Prefer `plotops.plot_timefreq()` for standard time-and-FFT comparison plots.
5. Prefer `plotops.subplots()` when custom axes-by-axes plotting is needed.
6. Use explicit `plotops.layout()` + `plotops.subplot()` when the layout must be inspected, reused for export, or shared across figures.
7. After custom plotting, use `plotops.finish()` for legend placement, axis tightening, hiding unused axes, and interactive helpers.
8. Use `plotops.savefig()` for final exported figures.
9. Use `plotops.close()` when a workflow should explicitly release figures.
10. Keep labels, units, and legend names explicit.
11. Preserve returned handles (`fig`, `axes`, `fig_out`) when later code may need editing, annotations, or saving.

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

fig_out = plotops.subplots(
    nrow,
    ncol,
    layout_kwargs=layout_options,
    xlabel=xlabel,
    ylabel=ylabel,
    xlog=xlog,
    ylog=ylog,
    grid=grid,
)

fig = fig_out["fig"]
axes = fig_out["axes"]

# custom plotting on `axes`

plotops.finish(
    fig,
    axes,
    suptitle=suptitle,
)
```

and then build the plot manually on `axes`.
