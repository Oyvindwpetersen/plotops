#%%

import numpy as np
import matplotlib.pyplot as plt
import mplcursors

from . import misc
from . import figure


#%%

def _to_1d(x):
    x = np.asarray(x)
    if x.ndim == 2 and 1 in x.shape:
        return x.reshape(-1)
    if x.ndim != 1:
        raise ValueError('x must be 1D or (1,N)/(N,1)')
    return x


def _to_2d(y):
    y = np.asarray(y)
    if y.ndim == 1:
        return y.reshape(1, -1)
    if y.ndim != 2:
        raise ValueError('y must be 1D or 2D')
    return y


def plotxy(
    x_list,
    y_list,
    *,
    labels=None,
    color=None,
    linestyle=None,
    linewidth=None,
    xlabel='x',
    ylabel=None,
    ylog=False,
    legend=True,
    cursor=False,
    legend_kwargs=None,
    tight_kwargs=None,
    ncols=None,
    **plot_kwargs
):
    """
    Row-wise plotting utility.

    Each row of y defines one subplot.
    Each subplot contains one curve per data source.
    """

    # -------------------------------------------------
    # normalize inputs to lists
    # -------------------------------------------------

    if not isinstance(x_list, (list, tuple)):
        x_list = [x_list]

    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]

    n_source = len(y_list)

    # -------------------------------------------------
    # expand shared x-axis if needed
    # -------------------------------------------------

    if len(x_list) == 1 and n_source > 1:
        x_list = x_list * n_source

    if len(x_list) != n_source:
        raise ValueError(
            f'x_list length ({len(x_list)}) does not match '
            f'y_list length ({n_source})'
        )

    # -------------------------------------------------
    # convert shapes
    # -------------------------------------------------

    x_list = [_to_1d(x) for x in x_list]
    y_list = [_to_2d(y) for y in y_list]

    n_signal = y_list[0].shape[0]

    for j, (x, y) in enumerate(zip(x_list, y_list)):
        if y.shape[0] != n_signal:
            raise ValueError(
                f'y_list[{j}] has {y.shape[0]} rows, expected {n_signal}'
            )
        if y.shape[1] != x.size:
            raise ValueError(
                f'Shape mismatch in source {j}: '
                f'x has length {x.size}, y has {y.shape[1]} columns'
            )

    # -------------------------------------------------
    # defaults and validation
    # -------------------------------------------------

    if labels is None:
        labels = [str(j + 1) for j in range(n_source)]
    if len(labels) != n_source:
        raise ValueError(
            f'labels length ({len(labels)}) must match number of sources ({n_source})'
        )

    if ylabel is None:
        ylabel = [f'y{i+1}' for i in range(n_signal)]
    if len(ylabel) != n_signal:
        raise ValueError(
            f'ylabel length ({len(ylabel)}) must match number of rows ({n_signal})'
        )

    if color is None:
        color = misc.color(n_source)
    if linestyle is None:
        linestyle = ['-'] * n_source
    if linewidth is None:
        linewidth = [1.8] * n_source

    if len(color) != n_source:
        raise ValueError(f'color length ({len(color)}) must match number of sources')
    if len(linestyle) != n_source:
        raise ValueError(f'linestyle length ({len(linestyle)}) must match number of sources')
    if len(linewidth) != n_source:
        raise ValueError(f'linewidth length ({len(linewidth)}) must match number of sources')

    # -------------------------------------------------
    # subplot layout logic
    # -------------------------------------------------

    if ncols is None:
        ncols = 1

    max_rows_per_fig = 6 if ncols == 1 else n_signal
    max_figs = 8

    figs = []
    axes_all = []

    n_figs = int(np.ceil(n_signal / max_rows_per_fig))
    if n_figs > max_figs:
        print('Warning: more than 8 figures requested. Truncating output.')
        n_figs = max_figs

    for f in range(n_figs):
        i0 = f * max_rows_per_fig
        i1 = min((f + 1) * max_rows_per_fig, n_signal)
        nrows = int(np.ceil((i1 - i0) / ncols))

        axes, fig, _ = figure.subplot(
            nrows, ncols, **(tight_kwargs or {})
        )

        axes = np.atleast_1d(axes)
        figs.append(fig)
        axes_all.append(axes)

        legend_handles = []

        for local_i, global_i in enumerate(range(i0, i1)):
            ax = axes[local_i]

            for j in range(n_source):
                h, = ax.plot(
                    x_list[j],
                    y_list[j][global_i, :],
                    color=color[j],
                    linestyle=linestyle[j],
                    linewidth=linewidth[j],
                    label=labels[j],
                    **plot_kwargs
                )
                if global_i == 0:
                    legend_handles.append(h)

            if ylog:
                ax.set_yscale('log')

            ax.set_ylabel(ylabel[global_i])
            ax.grid(True)

            if ylog:
                figure.axistight(ax, p=(0, 0), axes=('x',))
            else:
                figure.axistight(ax, p=(0, 0.05), axes=('x', 'y'))

            if cursor:
                mplcursors.cursor(ax, hover=False)

        # --- set xlabel on all bottom subplots ---
        for idx, ax in enumerate(axes):
            row = idx // ncols
            if row == nrows - 1:
                ax.set_xlabel(xlabel)

        if legend:
            legend_kwargs = legend_kwargs or {}
            right_edge = max(ax.get_position().x1 for ax in fig.axes)
            fig.legend(
                legend_handles,
                labels,
                loc='upper right',
                bbox_to_anchor=(right_edge, 1.0),
                bbox_transform=fig.transFigure,
                frameon=True,
                **legend_kwargs
            )
            
        figure.size(fig)
        figure.log_toggle(fig, key='l')


    return figs, axes_all


#%%

