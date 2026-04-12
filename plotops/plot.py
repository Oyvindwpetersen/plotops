#%%

import numpy as np
import matplotlib.pyplot as plt
import mplcursors
import matplotlib.ticker as mticker

from . import misc
from . import figure


#%%

def plotxy(
    x_list,
    y_list,
    *,
    labels=None,
    color=None,
    linestyle=('-',),
    linewidth=(1.2,),
    marker=(None,),
    alpha=(1.0,),
    xlabel='x',
    ylabel=None,
    suptitle='',
    xlog=False,
    ylog=False,
    xlim=None,
    legend=True,
    cursor=True,
    ncols=None,
    layout_kwargs=None,
    legend_kwargs=None,
    return_all=False,
    **plot_kwargs
):
    """
    Plot multiple data sources row-wise.
    
    Parameters
    ----------
    x_list : array-like or list
        One shared 1D x-array per source, or one x-array per subplot row.
    y_list : array-like or list
        One 1D/2D y-array per source, or one y-array per subplot row.
    labels : list of str, optional
    ncols : int, optional
    return_all : bool, optional
        If True, include all generated figures and axes groups in the output.
    
    Returns
    -------
    dict
        Figure, axes, lines, and metadata.
    """

    # -------------------------------------------------
    # helpers
    # -------------------------------------------------

    def _to_n(x, n, name):
        if isinstance(x, (str, bytes)) or not isinstance(x, (list, tuple)):
            return [x] * n
        x = list(x)
        if len(x) == 1:
            return x * n
        if len(x) != n:
            raise ValueError(f'{name} length ({len(x)}) must be 1 or {n}')
        return x

    def _is_rowwise_x(x, nrow):
        if isinstance(x, np.ndarray):
            return x.ndim == 2 and x.shape[0] == nrow

        if isinstance(x, (str, bytes)) or not isinstance(x, (list, tuple)):
            return False

        if len(x) != nrow:
            return False

        return any(not np.isscalar(xi) for xi in x)

    def _is_rowwise_y(y):
        if isinstance(y, np.ndarray):
            return y.ndim == 2

        if isinstance(y, (str, bytes)) or not isinstance(y, (list, tuple)):
            return False

        return any(not np.isscalar(yi) for yi in y)

    def _normalize_y_source(y):
        if _is_rowwise_y(y):
            if isinstance(y, np.ndarray):
                return [_to_1d(yi) for yi in y]
            return [_to_1d(yi) for yi in list(y)]

        return [_to_1d(y)]

    def _normalize_x_source(x, y_rows, idx):
        if _is_rowwise_x(x, len(y_rows)):
            if isinstance(x, np.ndarray):
                x_rows = [_to_1d(xi) for xi in x]
            else:
                x_rows = [_to_1d(xi) for xi in list(x)]
        else:
            x_shared = _to_1d(x)
            x_rows = [x_shared] * len(y_rows)

        for i, (xi, yi) in enumerate(zip(x_rows, y_rows)):
            if yi.size != xi.size:
                raise ValueError(
                    f'idx {idx}, row {i}: x.size={xi.size}, y.size={yi.size}'
                )

        return x_rows

    # -------------------------------------------------
    # normalize inputs
    # -------------------------------------------------
    
    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]
    
    y_rows_list = [_normalize_y_source(y) for y in y_list]
    n_source = len(y_rows_list)
    
    # Handle missing x_list
    if x_list is None or (isinstance(x_list, (list, tuple)) and len(x_list) == 0):
        N = y_rows_list[0][0].size
        x_default = np.arange(1, N + 1)
        x_list = [x_default.copy() for _ in range(n_source)]
    
    # Now normalize x_list
    if not isinstance(x_list, (list, tuple)):
        x_list = [x_list]
    
    if len(x_list) == 1 and n_source > 1:
        x_list = x_list * n_source

    if len(x_list) != n_source:
        raise ValueError(
            f'x_list length ({len(x_list)}) does not match '
            f'y_list length ({n_source})'
        )

    n_signal = len(y_rows_list[0])
    x_rows_list = []

    rows = []
    errors = []

    for j, (x, y_rows) in enumerate(zip(x_list, y_rows_list)):
        if len(y_rows) != n_signal:
            errors.append(
                f'y_list[{j}]: rows={len(y_rows)} (expected {n_signal})'
            )
            first_size = y_rows[0].size if len(y_rows) > 0 else 0
            rows.append((j, '-', len(y_rows), first_size))
            continue

        try:
            x_rows = _normalize_x_source(x, y_rows, j)
        except ValueError as exc:
            errors.append(str(exc))
            x_rows = None

        if x_rows is not None:
            x_rows_list.append(x_rows)
            x_size_info = x_rows[0].size if all(xi.size == x_rows[0].size for xi in x_rows) else 'var'
            y_size_info = y_rows[0].size if all(yi.size == y_rows[0].size for yi in y_rows) else 'var'
        else:
            x_rows_list.append(None)
            x_size_info = 'err'
            y_size_info = 'err'

        rows.append((j, x_size_info, len(y_rows), y_size_info))

    if errors:
        header = ' idx (source) | x.size | y.rows | y.size '
        sep = '-' * len(header)
        table = '\n'.join(
            f'{j:4d} | {str(xs):>6s} | {yr:6d} | {str(yc):>6s}'
            for j, xs, yr, yc in rows
        )

        raise ValueError(
            'Input dimension check failed:\n'
            + '\n'.join(errors)
            + '\n\nOverview of all sources:\n'
            + header + '\n' + sep + '\n' + table
        )

    # -------------------------------------------------
    # defaults and broadcast styling
    # -------------------------------------------------

    if labels is None:
        labels = [str(j + 1) for j in range(n_source)]
    if len(labels) != n_source:
        raise ValueError(
            f'labels length ({len(labels)}) must match number of sources ({n_source})'
        )

    if ylabel is None:
        ylabel = [f'$y_{i+1}$' for i in range(n_signal)]
    if isinstance(ylabel, str):
        ylabel=[ylabel]
    if len(ylabel) != n_signal:
        raise ValueError(
            f'ylabel length ({len(ylabel)}) must match number of rows ({n_signal})'
        )

    if color is None:
        color = misc.color(n_source)
    
    linestyle = _to_n(linestyle, n_source, 'linestyle')
    linewidth = _to_n(linewidth, n_source, 'linewidth')
    marker = _to_n(marker, n_source, 'marker')
    alpha = _to_n(alpha, n_source, 'alpha')

    if len(color) != n_source:
        raise ValueError(f'color length ({len(color)}) must match number of sources')
    
    # -------------------------------------------------
    # subplot layout logic
    # -------------------------------------------------

    if ncols is None:
        ncols = 1

    max_rows_per_fig = 6 if ncols == 1 else n_signal
    max_figs = 8

    figs = []
    axes_all = []
    lines_all = []

    n_figs = int(np.ceil(n_signal / max_rows_per_fig))
    if n_figs > max_figs:
        print('Warning: more than 8 figures requested. Truncating output.')
        n_figs = max_figs

    for f in range(n_figs):
        i0 = f * max_rows_per_fig
        i1 = min((f + 1) * max_rows_per_fig, n_signal)
        nrows = int(np.ceil((i1 - i0) / ncols))

        # Avoid recomputing layout if provided
        fig_layout = layout_kwargs if layout_kwargs is not None else figure.layout(nrows, ncols)
        n_axes = nrows * ncols
        n_active = i1 - i0
        n_pad = n_axes - n_active

        xlog_fig = _to_n(xlog, n_signal, 'xlog')[i0:i1] + [False] * n_pad
        ylog_fig = _to_n(ylog, n_signal, 'ylog')[i0:i1] + [False] * n_pad
        xlim_fig = _to_n(xlim, n_signal, 'xlim')[i0:i1] + [None] * n_pad
        ylabel_fig = ylabel[i0:i1] + [None] * n_pad

        axes, fig, _ = figure.subplot(
            nrows,
            ncols,
            layout=fig_layout,
            xlabel=xlabel,
            ylabel=ylabel_fig,
            xlog=xlog_fig,
            ylog=ylog_fig,
            xlim=xlim_fig,
            grid=True,
        )
        axes_flat = np.asarray(axes, dtype=object).reshape(-1)

        figs.append(fig)
        axes_all.append(axes)

        legend_handles = []
        per_fig_lines = []

        for local_i, global_i in enumerate(range(i0, i1)):
            ax = axes_flat[local_i]
            ax_lines = []

            for j in range(n_source):
                x_row = x_rows_list[j][global_i]
                h, = ax.plot(
                    x_row,
                    y_rows_list[j][global_i],
                    color=color[j],
                    linestyle=linestyle[j],
                    linewidth=linewidth[j],
                    marker=marker[j],
                    alpha=alpha[j],
                    label=labels[j],
                    **plot_kwargs
                )
                ax_lines.append(h)

                if global_i == 0:
                    legend_handles.append(h)

            if ylog_fig[local_i]:
                figure.axistight(ax, p=(0, 0.05), axes=('x','ylog'))
            else:
                figure.axistight(ax, p=(0, 0.05), axes=('x','y'))

            if cursor:
                mplcursors.cursor(ax, hover=False)

            per_fig_lines.append(ax_lines)

        for ax in axes_flat[n_active:]:
            ax.set_visible(False)

        if suptitle != '':
            fig.suptitle(suptitle, fontweight='bold', fontsize=10)

        if legend:
            legend_kwargs = legend_kwargs or {}
            
            # Reorder legend to row-wise
            ncol = min(n_source, 5)
            n = len(labels)
            nrow = int(np.ceil(n / ncol))
            
            order = []
            for c in range(ncol):
                for r in range(nrow):
                    idx = r * ncol + c
                    if idx < n:
                        order.append(idx)
            
            legend_handles = [legend_handles[i] for i in order]
            legend_labels = [labels[i] for i in order]
            
            # 1. Get the boundaries of your subplots
            right_edge = max(ax.get_position().x1 for ax in fig.axes)
            top_edge = max(ax.get_position().y1 for ax in fig.axes)
        
            # 2. Define your small vertical gap (e.g., 1% of figure height)
            vertical_gap = 0.02
            
            fig.legend(
                legend_handles,
                legend_labels,
                # 'lower right' pins the BOTTOM-RIGHT corner of the legend.
                # This ensures it sits ABOVE the plot and grows LEFT.
                loc='lower right',
                bbox_to_anchor=(right_edge, top_edge + vertical_gap),
                bbox_transform=fig.transFigure,
                ncol=ncol,
                columnspacing=1.0,   # Distance between the 2 items (default is 2.0)
                handlelength=1.5,    # Length of the colored lines (default is 2.0)
                handletextpad=0.5,   # Distance between line and its text (default is 0.8)
                borderaxespad=0,     # Keeps the right edge flush
                frameon=True,
                **legend_kwargs
            )

        figure.size(fig)
        figure.log_toggle(fig, key='l')
        figure.enable_popout(fig, key='p')

        lines_all.append(per_fig_lines)


    fig_out={
        'fig': figs[0],
        'axes': axes_all[0],
        'lines': lines_all[0],
        'meta': {
            'n_source': n_source,
            'n_signal': n_signal,
            'ncols': ncols,
            'ylog': ylog,
            'labels': labels,
            'ylabel': ylabel
        }
    }

    if return_all:
        fig_out['figs'] = figs
        fig_out['axes_all'] = axes_all
        fig_out['lines_all'] = lines_all

    return fig_out


def plot_timefreq(
    t_list,
    y_list,
    *,
    labels=None,
    color=None,
    linestyle=('-',),
    linewidth=(1.2,),
    marker=(None,),
    alpha=(1.0,),
    time_xlabel='t [s]',
    freq_xlabel='f [Hz]',
    ylabel=None,
    fft_ylabel=None,
    suptitle='',
    ylog_freq=False,
    time_xlim=None,
    freq_xlim=None,
    legend=True,
    cursor=True,
    layout_kwargs=None,
    legend_kwargs=None,
    **plot_kwargs
):
    """
    Plot time series and one-sided FFT side-by-side for each signal row.

    Parameters
    ----------
    t_list : array-like or list of array-like
        Time vectors per source.
    y_list : array-like or list of array-like
        Signal matrices per source with shape (nsignal, npoints).
        One time vector is used per source and converted internally to
        row-wise time and frequency data before delegating to `plotxy()`.

    Returns
    -------
    dict
        Figure, axes, line handles, and metadata.
    """

    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]

    y_list = [_to_2d(y) for y in y_list]
    n_source = len(y_list)

    if not isinstance(t_list, (list, tuple)):
        t_list = [t_list]
    if len(t_list) == 1 and n_source > 1:
        t_list = t_list * n_source

    t_list = [_to_1d(t) for t in t_list]

    if len(t_list) != n_source:
        raise ValueError(
            f't_list length ({len(t_list)}) does not match '
            f'y_list length ({n_source})'
        )

    n_signal = y_list[0].shape[0]

    if ylabel is None:
        ylabel = [f'$y_{i+1}$' for i in range(n_signal)]
    if isinstance(ylabel, str):
        ylabel = [ylabel]

    if fft_ylabel is None:
        fft_ylabel = [f'|FFT({lab})|' for lab in ylabel]
    if isinstance(fft_ylabel, str):
        fft_ylabel = [fft_ylabel]

    if color is None:
        color = misc.color(n_source)

    x_tf = []
    y_tf = []

    for t, y in zip(t_list, y_list):
        x_rows = []
        y_rows = []

        for i in range(n_signal):
            dt = np.mean(np.diff(t))
            freq = np.fft.rfftfreq(t.size, d=dt)
            amp = np.abs(np.fft.rfft(y[i, :]))

            x_rows.extend([t, freq])
            y_rows.extend([y[i, :], amp])

        x_tf.append(x_rows)
        y_tf.append(y_rows)

    ylabel_tf = [val for pair in zip(ylabel, fft_ylabel) for val in pair]
    ylog_tf = [val for pair in zip([False] * n_signal, [ylog_freq] * n_signal) for val in pair]
    xlim_tf = [val for pair in zip([time_xlim] * n_signal, [freq_xlim] * n_signal) for val in pair]

    fig_out = plotxy(
        x_tf,
        y_tf,
        labels=labels,
        color=color,
        linestyle=linestyle,
        linewidth=linewidth,
        marker=marker,
        alpha=alpha,
        xlabel=[time_xlabel, freq_xlabel],
        ylabel=ylabel_tf,
        suptitle=suptitle,
        ylog=ylog_tf,
        xlim=xlim_tf,
        legend=legend,
        cursor=cursor,
        ncols=2,
        layout_kwargs=layout_kwargs if layout_kwargs is not None else figure.layout(n_signal, 2),
        legend_kwargs=legend_kwargs,
        **plot_kwargs
    )

    fig_out['time_lines'] = fig_out['lines'][0::2]
    fig_out['freq_lines'] = fig_out['lines'][1::2]
    fig_out['meta']['fft_ylabel'] = fft_ylabel
    fig_out['meta']['ylog_freq'] = ylog_freq

    return fig_out


def plotxy_old(
    x_list,
    y_list,
    *,
    labels=None,
    color=None,
    linestyle=['-'],
    linewidth=[1.2],
    xlabel='x',
    ylabel=None,
    ylog=False,
    legend=True,
    cursor=False,
    ncols=None,
    layout_kwargs=None,
    legend_kwargs=None,
    **plot_kwargs
):
    """
    Multi-source row-wise plotting utility.

    Each row of y defines one subplot.
    Each subplot contains one curve per data source.

    Parameters
    ----------
    x_list : array-like or list of array-like
        X-data per source.
    y_list : array-like or list of array-like
        Y-data per source (2D: rows = signals).
    labels : list of str, optional
        Legend labels for sources.
    color : list of tuple, optional
        RGB colors per source.
    linestyle : list of str
        Line styles.
    linewidth : list of float
        Line widths.
    xlabel : str
        X-axis label.
    ylabel : list of str
        Labels per subplot row.
    ylog : bool
        Use logarithmic y-axis.
    legend : bool
        Enable figure-level legend.
    cursor : bool
        Enable mplcursors interaction.
    ncols : int
        Number of subplot columns.
    layout_kwargs : dict
        Forwarded to figure.layout/subplot.
    legend_kwargs : dict
        Forwarded to fig.legend.
    plot_kwargs : dict
        Additional arguments to matplotlib plot().

    Returns
    -------
    figs : Figure or list of Figure
    axes_all : list of ndarray
        Axes grouped per figure.
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
    
    rows = []
    errors = []
    
    for j, (x, y) in enumerate(zip(x_list, y_list)):
        rows.append((j, x.size, *y.shape))
    
        if y.shape[0] != n_signal:
            errors.append(
                f'y_list[{j}]: rows={y.shape[0]} (expected {n_signal})'
            )
        if y.shape[1] != x.size:
            errors.append(
                f'idx {j}: x.size={x.size}, y.cols={y.shape[1]}'
            )
    
    if errors:
        header = ' idx (source) | x.size | y.rows | y.cols '
        sep = '-' * len(header)
        table = '\n'.join(
            f'{j:4d} | {xs:6d} | {yr:6d} | {yc:6d}'
            for j, xs, yr, yc in rows
        )
    
        raise ValueError(
            'Input dimension check failed:\n'
            + '\n'.join(errors)
            + '\n\nOverview of all sources:\n'
            + header + '\n' + sep + '\n' + table
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
        ylabel = [f'$y_{i+1}$' for i in range(n_signal)]
    if len(ylabel) != n_signal:
        raise ValueError(
            f'ylabel length ({len(ylabel)}) must match number of rows ({n_signal})'
        )

    if color is None:
        color = misc.color(n_source)
    if len(linewidth)==1:
        linestyle = [linestyle[0]] * n_source
    if len(linewidth)==1:
        linewidth = [linewidth[0]] * n_source

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
        
        if layout_kwargs is None:
            figsize, layout_kwargs, subsize_out=figure.layout(nrows, ncols)
    
        axes, fig, _ = figure.subplot(
            nrows, ncols, **(layout_kwargs or {})
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
                figure.axistight(ax, p=(0, 0.05), axes=('x','ylog'))
                
                # Force labels only 10^n
                ax.yaxis.set_major_locator(mticker.LogLocator(base=10.0, subs=(1.0,)))  # Major ticks only at 10^n
                ax.yaxis.set_major_formatter(mticker.LogFormatterMathtext(base=10.0)) # Format as 10^n
                ax.yaxis.set_minor_locator(mticker.NullLocator()) # Remove minor ticks completely
                
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
            
            # 1. Get the boundaries of your subplots
            right_edge = max(ax.get_position().x1 for ax in fig.axes)
            top_edge = max(ax.get_position().y1 for ax in fig.axes)
        
            # 2. Define your small vertical gap (e.g., 1% of figure height)
            vertical_gap = 0.02
            
            fig.legend(
                legend_handles,
                labels,
                # 'lower right' pins the BOTTOM-RIGHT corner of the legend.
                # This ensures it sits ABOVE the plot and grows LEFT.
                loc='lower right',
                bbox_to_anchor=(right_edge, top_edge + vertical_gap),
                bbox_transform=fig.transFigure,
                ncol=n_source,
                columnspacing=1.0,   # Distance between the 2 items (default is 2.0)
                handlelength=1.5,    # Length of the colored lines (default is 2.0)
                handletextpad=0.5,   # Distance between line and its text (default is 0.8)
                borderaxespad=0,     # Keeps the right edge flush
                frameon=True,
                **legend_kwargs
            )
            
        figure.size(fig)
        figure.log_toggle(fig, key='l')
        figure.enable_popout(fig, key='p')

    if len(figs)==1:
        figs=figs[0]

    return figs, axes_all

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

#%%

def plot3d(x, y, **plotxy_kwargs):
    """
    Plot list of 3D matrices using 2D flattening.
    
    Parameters
    ----------
    x : array-like
    y : list of ndarray (n1, n2, n3)
    
    Returns
    -------
    dict
        Output from plotxy.
    """

    if isinstance(y, np.ndarray):
        y = [y]

    if not isinstance(y, (list, tuple)):
        raise ValueError('y must be a list (or tuple) of 3D arrays')

    y_list = []
    x_list = x

    ncols = None

    for yk in y:
        yk = np.asarray(yk)
        if yk.ndim != 3:
            raise ValueError('Each element of y must have shape (n1, n2, n3)')

        n1, n2, _ = yk.shape
        ncols = n2 if ncols is None else ncols

        # Flatten this matrix row-by-row
        y2d = misc.matrix_3d_to_2d(yk)   # shape (n1*n2, n3)

        y_list.append(y2d)

    # Enforce matrix layout (number of columns = matrix columns)
    plotxy_kwargs.setdefault('ncols', ncols)
    
    ylabel=misc.labels_2d(n1, n2)
    plotxy_kwargs.setdefault('ylabel', ylabel)
    

    # Single plotxy call
    fig_out=plotxy(x_list, y_list, **plotxy_kwargs)
    
    return fig_out
    
#%%

from matplotlib.colors import LogNorm

def matrix_grid(
    M,
    xlabels=None,
    ylabels=None,
    ax=None,
    cmap='viridis',
    vmin=None,
    vmax=None,
    scale='linear',          # 'linear' or 'log'
    show_values=False,
    value_fmt='{:.2e}',
    colorbar=True,
    title='Matrix plot',
):
    """
    Plot a matrix as a colored grid.

    Parameters
    ----------
    M : ndarray, shape (ny, nx)
        Matrix to plot.
    xlabels : list of str, optional
        Tick labels for columns.
    ylabels : list of str, optional
        Tick labels for rows.
    ax : matplotlib Axes, optional
        Axes to plot into. If None, a new figure is created.
    cmap : str
        Colormap.
    vmin, vmax : float, optional
        Color scale limits.
    scale : {'linear', 'log'}
        Color scaling.
    show_values : bool
        If True, annotate each cell with its value.
    value_fmt : str
        Format string for annotations.
    colorbar : bool
        If True, show colorbar.
    title : str
        Figure title.
    """

    M = np.asarray(M)
    if M.ndim != 2:
        raise ValueError('M must be a 2D matrix')

    ny, nx = M.shape

    if xlabels is not None and len(xlabels) != nx:
        raise ValueError('xlabels must have length equal to number of columns')
    if ylabels is not None and len(ylabels) != ny:
        raise ValueError('ylabels must have length equal to number of rows')

    if ax is None:
        fig, ax = plt.subplots(figsize=(1.1 * nx, 1.1 * ny))
    else:
        fig = ax.figure

    if scale == 'log':
        if np.any(M <= 0):
            raise ValueError('Log scale requires strictly positive values')
        norm = LogNorm(vmin=vmin, vmax=vmax)
        im = ax.imshow(M, cmap=cmap, norm=norm)
    elif scale == 'linear':
        im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax)
    else:
        raise ValueError("scale must be 'linear' or 'log'")

    ax.set_xticks(np.arange(nx))
    ax.set_yticks(np.arange(ny))

    if xlabels is not None:
        ax.set_xticklabels(xlabels)
    if ylabels is not None:
        ax.set_yticklabels(ylabels)

    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.set_title(title, pad=20)

    # Grid lines
    ax.set_xticks(np.arange(-0.5, nx, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, ny, 1), minor=True)
    ax.grid(which='minor', color='k', linestyle='-', linewidth=0.3)
    ax.tick_params(which='minor', bottom=False, left=False)

    if show_values:
        for i in range(ny):
            for j in range(nx):
                val = M[i, j]
                ax.text(
                    j, i,
                    value_fmt.format(val),
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='white' if im.norm(val) > 0.6 else 'black',
                )

    if colorbar:
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Value')

    ax.set_aspect('equal')
    fig.tight_layout()

    return ax


#%%

def corr(
    cov,
    labels=None,
    ax=None,
    cmap='coolwarm',
    vmin=-1.0,
    vmax=1.0,
    show_values=False,
    value_fmt='{:.2f}',
    colorbar=True,
    title='Correlation matrix',
):
    """
    Plot correlation matrix derived from a covariance matrix.

    Parameters
    ----------
    cov : ndarray, shape (n, n)
        Covariance matrix.
    labels : list of str, optional
        Axis labels. Defaults to ['x_1', ..., 'x_n'].
    ax : matplotlib Axes, optional
        Axes to plot into. If None, a new figure is created.
    cmap : str
        Colormap for correlation values.
    vmin, vmax : float
        Color scale limits (default [-1, 1]).
    show_values : bool
        If True, annotate each cell with its correlation value.
    value_fmt : str
        Format string for annotations.
    colorbar : bool
        If True, show colorbar.
    title : str
        Figure title.
    """

    cov = np.asarray(cov)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError('cov must be a square matrix')

    n = cov.shape[0]

    # Convert covariance → correlation
    std = np.sqrt(np.diag(cov))
    if np.any(std == 0):
        raise ValueError('Zero variance encountered in covariance matrix')

    corr = cov / np.outer(std, std)
    corr = np.clip(corr, -1.0, 1.0)

    # Labels
    if labels is None:
        labels = [f'$x_{{{i+1}}}$' for i in range(n)]
    if len(labels) != n:
        raise ValueError('labels must have length n')

    # Axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(1.2 * n, 1.2 * n))
    else:
        fig = ax.figure

    im = ax.imshow(corr, cmap=cmap, vmin=vmin, vmax=vmax)

    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.set_title(title, pad=20)

    # Grid for square layout
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which='minor', color='k', linestyle='-', linewidth=0.3)
    ax.tick_params(which='minor', bottom=False, left=False)

    # Annotations
    if show_values:
        for i in range(n):
            for j in range(n):
                ax.text(
                    j, i,
                    value_fmt.format(corr[i, j]),
                    ha='center',
                    va='center',
                    fontsize=9,
                    color='black' if abs(corr[i, j]) < 0.6 else 'white',
                )

    # Colorbar
    if colorbar:
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Correlation')

    ax.set_aspect('equal')
    fig.tight_layout()

    return corr, ax

#%%

from matplotlib.tri import Triangulation
from matplotlib.colors import LogNorm
from mpl_toolkits.mplot3d.art3d import Line3DCollection

def surfiso(x,f,*,
    xlabel='x',ylabel='y',zlabel='z',
    facealpha=0.8,
    displayname='',
    isolines=20,
    linestyle='-',
    linewidth=0.3,
    view=(40, 15),
    cbar=True,
    cbarlocation='right',
    xtick=None,
    ytick=None,
    xlpos=(0.0, 0.0, 0.0),
    xlog=False,
    ylog=False,
    zlog=False,
    markercolor=(0.5, 0.5, 0.5),
    markersize=None,
    cmap='GnBu'
):
    
    """
    Plot triangulated 3D surface with optional isolines.
    
    Parameters
    ----------
    x : ndarray, shape (N, 2)
        2D coordinates.
    f : ndarray, shape (N,)
        Scalar field values.
    xlabel, ylabel, zlabel : str
        Axis labels.
    facealpha : float
        Surface transparency.
    isolines : int or array-like
        Number or explicit levels.
    linestyle : str
        Line style for isolines.
    linewidth : float
        Isoline width.
    view : (float, float)
        (azimuth, elevation).
    xlog, ylog, zlog : bool
        Log scaling flags.
    cmap : str
        Colormap.
    
    Returns
    -------
    h_surf : Poly3DCollection
        Surface handle.
    h_iso : list
        List of Line3DCollection handles.
    """

    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError('x must have shape (N, 2)')

    f = _as_1d(f)
    if x.shape[0] != f.shape[0]:
        raise ValueError('x and f must have equal number of rows')

    fig = plt.gcf()
    ax = plt.gca()
    if not hasattr(ax, 'zaxis'):
        fig.delaxes(ax)
        ax = fig.add_subplot(111, projection='3d')
    
    tri = Triangulation(x[:, 0], x[:, 1])
    z = f

    if zlog:
        if np.any(z <= 0):
            raise ValueError('zlog=True requires f > 0')
        norm = LogNorm(vmin=z.min(), vmax=z.max())
        h_surf = ax.plot_trisurf(tri, z, cmap=cmap, norm=norm,
                                 linewidth=0.0, alpha=facealpha)
    else:
        h_surf = ax.plot_trisurf(tri, z, cmap=cmap,
                                 linewidth=0.0, alpha=facealpha, shade=False)

    if displayname:
        h_surf.set_label(displayname)

    if xlog:
        ax.set_xscale('log')
    if ylog:
        ax.set_yscale('log')
    if zlog:
        ax.set_zscale('log')

    if zlog and np.isscalar(isolines):
        levels = np.logspace(np.log10(z.min()), np.log10(z.max()), int(isolines))
    else:
        levels = _iso_values_from_spec(z, isolines)

    segs_by_level = isoline_segments_on_triangulation(tri, z, levels)

    h_iso = []
    for _, segs in segs_by_level:
        if segs.size == 0:
            h_iso.append(None)
            continue
        lc = Line3DCollection(segs, linewidths=linewidth, linestyles=linestyle)
        lc.set_color(markercolor)
        ax.add_collection3d(lc)
        h_iso.append(lc)

    if markersize is not None:
        ax.plot(x[:, 0], x[:, 1], z, 'o',
                color=markercolor, markersize=markersize)

    ax.minorticks_off()
    if xtick is not None:
        ax.set_xticks(np.asarray(xtick, dtype=float))
    if ytick is not None:
        ax.set_yticks(np.asarray(ytick, dtype=float))

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    try:
        lab = ax.xaxis.get_label()
        lab.set_position((lab.get_position()[0] + xlpos[0],
                          lab.get_position()[1] + xlpos[1]))
    except Exception:
        pass

    ax.view_init(elev=view[1], azim=view[0])

    if cbar:
        cb = plt.colorbar(h_surf, ax=ax, location=cbarlocation)
        if zlog:
            ticks = cb.get_ticks()
            ticks = ticks[(ticks > 0) & np.isfinite(ticks)]
            if ticks.size:
                e = np.round(np.log10(ticks)).astype(int)
                cb.set_ticks(10.0 ** e)
                cb.set_ticklabels([rf'$10^{{{ei}}}$' for ei in e])

    ax.set_xlim(x[:, 0].min(), x[:, 0].max())
    ax.set_ylim(x[:, 1].min(), x[:, 1].max())
    dz = 0.05 * (z.max() - z.min()) if z.max() > z.min() else 1.0
    ax.set_zlim(z.min(), z.max() + dz)

    return h_surf, h_iso

def _as_1d(a):
    return np.asarray(a, dtype=float).ravel()


def _iso_values_from_spec(fvals, isolines):
    """
    MATLAB behavior:
      - scalar n: n equally spaced values strictly inside [min, max]
      - vector: use values directly
    """
    fmin = float(np.min(fvals))
    fmax = float(np.max(fvals))
    if np.isscalar(isolines):
        n = int(isolines)
        if n <= 0:
            return np.array([], dtype=float)
        return np.linspace(fmin, fmax, n + 2)[1:-1]
    return np.asarray(isolines, dtype=float).ravel()


def isoline_segments_on_triangulation(tri, f, levels):
    """
    Compute isoline segments on a triangulated surface.
    Returns list of (level, segments), segments shape (M, 2, 3).
    """
    x = tri.x
    y = tri.y
    triangles = tri.triangles
    f = _as_1d(f)

    if f.shape[0] != x.shape[0]:
        raise ValueError('f length must match number of vertices')

    p = np.column_stack([x, y, f])
    ftri = f[triangles]
    ptri = p[triangles]

    levels = np.asarray(levels, dtype=float).ravel()
    out = []

    def _interp(pa, pb, fa, fb, v):
        t = (v - fa) / (fb - fa)
        return pa + t[..., None] * (pb - pa)

    edges = [(0, 1), (1, 2), (2, 0)]

    for v in levels:
        g = ftri - v
        cross = []
        pts = []

        for a, b in edges:
            ga = g[:, a]
            gb = g[:, b]
            mask = (ga * gb) < 0.0
            cross.append(mask)

            pa = ptri[:, a, :]
            pb = ptri[:, b, :]
            fa = ftri[:, a]
            fb = ftri[:, b]

            pt = np.full((g.shape[0], 3), np.nan)
            ok = mask & (fb != fa)
            if np.any(ok):
                pt[ok] = _interp(pa[ok], pb[ok], fa[ok], fb[ok], v)
            pts.append(pt)

        cross = np.column_stack(cross)
        active = np.sum(cross, axis=1) == 2

        segs = []
        for ti in np.where(active)[0]:
            eids = np.where(cross[ti])[0]
            p0 = pts[eids[0]][ti]
            p1 = pts[eids[1]][ti]
            if np.all(np.isfinite(p0)) and np.all(np.isfinite(p1)):
                segs.append([p0, p1])

        out.append((v, np.asarray(segs)))

    return out


from .legacy import plotxy_old


