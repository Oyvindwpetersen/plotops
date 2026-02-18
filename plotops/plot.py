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
    legend=True,
    cursor=True,
    ncols=None,
    layout_kwargs=None,
    legend_kwargs=None,
    **plot_kwargs
):
    """
    Plot multiple data sources row-wise.
    
    Parameters
    ----------
    x_list : array-like or list
    y_list : array-like or list (2D per source)
    labels : list of str, optional
    ncols : int, optional
    
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

    # -------------------------------------------------
    # normalize inputs
    # -------------------------------------------------
    
    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]
    
    # Convert y first so shape is known
    y_list = [_to_2d(y) for y in y_list]
    n_source = len(y_list)
    
    # Handle missing x_list
    if x_list is None or (isinstance(x_list, (list, tuple)) and len(x_list) == 0):
        N = y_list[0].shape[1]
        x_default = np.arange(1, N + 1)
        x_list = [x_default.copy() for _ in range(n_source)]
    
    # Now normalize x_list
    if not isinstance(x_list, (list, tuple)):
        x_list = [x_list]
    
    if len(x_list) == 1 and n_source > 1:
        x_list = x_list * n_source
    
    x_list = [_to_1d(x) for x in x_list]
    
    if len(x_list) != n_source:
        raise ValueError(
            f'x_list length ({len(x_list)}) does not match '
            f'y_list length ({n_source})'
        )

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
        if layout_kwargs is None:
            layout_kwargs = figure.layout(nrows, ncols)
                                      
        axes, fig, _ = figure.subplot(nrows, ncols, **(layout_kwargs or {}))
        axes = np.atleast_1d(axes)

        figs.append(fig)
        axes_all.append(axes)

        legend_handles = []
        per_fig_lines = []

        for local_i, global_i in enumerate(range(i0, i1)):
            ax = axes[local_i]
            ax_lines = []

            for j in range(n_source):
                h, = ax.plot(
                    x_list[j],
                    y_list[j][global_i, :],
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

            if xlog:
                ax.set_xscale('log')
                
            if ylog:
                ax.set_yscale('log')

            ax.set_ylabel(ylabel[global_i])
            ax.grid(True)

            if ylog:
                figure.axistight(ax, p=(0, 0.05), axes=('x','ylog'))
            else:
                figure.axistight(ax, p=(0, 0.05), axes=('x','y'))

            if cursor:
                mplcursors.cursor(ax, hover=False)

            per_fig_lines.append(ax_lines)

        for idx, ax in enumerate(axes):
            row = idx // ncols
            if row == nrows - 1:
                ax.set_xlabel(xlabel)

        if suptitle != '':
            fig.suptitle(suptitle, fontweight='bold', fontsize=10)

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

    # Ensure y is iterable
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

def corr(
    cov,
    labels=None,
    ax=None,
    cmap='coolwarm',
    vmin=-1.0,
    vmax=1.0,
    show_values=True,
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
        labels = [f'$x_{i+1}$' for i in range(n)]
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


