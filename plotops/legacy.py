import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import mplcursors

from . import misc


def subplot_old(
    nh,
    nw,
    gap=0.05,
    marg_h=0.1,
    marg_w=0.05,
    weight_h=None,
    weight_w=None,
    fig=None,
    skipaxes=False,
    **kwargs,
):
    if fig is None:
        fig = plt.figure()

    if np.isscalar(gap):
        gap = (gap, gap)
    if np.isscalar(marg_h):
        marg_h = (marg_h, marg_h)
    if np.isscalar(marg_w):
        marg_w = (marg_w, marg_w)

    if weight_h is None:
        weight_h = np.ones(nh)
    if weight_w is None:
        weight_w = np.ones(nw)

    weight_h = np.asarray(weight_h, dtype=float)
    weight_w = np.asarray(weight_w, dtype=float)

    if len(weight_h) != nh:
        raise ValueError("weight_h must have length nh")
    if len(weight_w) != nw:
        raise ValueError("weight_w must have length nw")

    weight_h /= weight_h.sum()
    weight_w /= weight_w.sum()

    H = 1.0 - sum(marg_h) - gap[0] * (nh - 1)
    W = 1.0 - sum(marg_w) - gap[1] * (nw - 1)

    if H <= 0 or W <= 0:
        raise ValueError("Margins and gaps leave no space for axes")

    axh = H * weight_h
    axw = W * weight_w

    axes = []
    pos = []

    y = 1.0 - marg_h[1]
    for ih in range(nh):
        y -= axh[ih]
        x = marg_w[0]

        for iw in range(nw):
            p = [x, y, axw[iw], axh[ih]]
            pos.append(p)

            if not skipaxes:
                axes.append(fig.add_axes(p))

            x += axw[iw] + gap[1]

        y -= gap[0]

    return axes, fig, pos


def layout_old(
    nrow,
    ncol,
    *,
    subsize=(3.0, 6.0),
    figsize=None,
    gap=(1.5, 2.0),
    marg_h=(1.2, 1.0),
    marg_w=(1.5, 0.8),
    latex=None,
    aspect=None,
):
    if int(nrow) != nrow or int(ncol) != ncol or nrow <= 0 or ncol <= 0:
        raise ValueError("nrow and ncol must be positive integers")
    nrow = int(nrow)
    ncol = int(ncol)

    if subsize is None and figsize is None:
        raise ValueError("Provide subsize or figsize")

    if subsize is not None and figsize is not None:
        subsize = None

    gap_h, gap_w = _as_pair(gap)
    mh0, mh1 = _as_pair(marg_h)
    mw0, mw1 = _as_pair(marg_w)

    target_w = None
    target_h = None

    if latex is not None:
        if isinstance(latex, str):
            target_w = _latex_figwidth_cm(latex)
        elif isinstance(latex, dict):
            if "width" in latex:
                target_w = float(latex["width"])
            if "height" in latex:
                target_h = float(latex["height"])
        else:
            raise ValueError("latex must be None, a string preset, or a dict")

        if target_w is not None and target_w <= 0:
            raise ValueError("latex width must be positive")
        if target_h is not None and target_h <= 0:
            raise ValueError("latex height must be positive")

    if subsize is not None:
        h_ax, w_ax = _as_pair(subsize)
        if h_ax <= 0 or w_ax <= 0:
            raise ValueError("subsize must be positive")

        if target_w is not None:
            usable_w = target_w - mw0 - mw1 - (ncol - 1) * gap_w
            if usable_w <= 0:
                raise ValueError("Margins/gaps too large for requested latex width")
            w_ax = usable_w / ncol
            w_fig = target_w
        else:
            w_fig = ncol * w_ax + (ncol - 1) * gap_w + mw0 + mw1

        if target_h is not None:
            h_fig = target_h
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError("Margins/gaps too large for requested latex height")
            h_ax = usable_h / nrow
        elif (target_w is not None) and (aspect is not None):
            aspect = float(aspect)
            if aspect <= 0:
                raise ValueError("aspect must be positive")
            h_fig = w_fig / aspect
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError("Margins/gaps too large for aspect-implied height")
            h_ax = usable_h / nrow
        else:
            h_fig = nrow * h_ax + (nrow - 1) * gap_h + mh0 + mh1
    else:
        h_fig, w_fig = _as_pair(figsize)
        if h_fig <= 0 or w_fig <= 0:
            raise ValueError("figsize must be positive")

        if target_w is not None:
            w_fig = target_w
        if target_h is not None:
            h_fig = target_h

        usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
        usable_w = w_fig - mw0 - mw1 - (ncol - 1) * gap_w
        if usable_h <= 0 or usable_w <= 0:
            raise ValueError("Margins and gaps leave no space for axes")

        h_ax = usable_h / nrow
        w_ax = usable_w / ncol

    if h_fig <= 0 or w_fig <= 0:
        raise ValueError("Computed figure size is not positive")

    dict_tight = _dict_tight_from_cm(
        (h_fig, w_fig),
        gap_cm=gap,
        marg_h_cm=marg_h,
        marg_w_cm=marg_w,
    )

    return (h_fig, w_fig), dict_tight, (h_ax, w_ax)


def enable_log_toggle_old(fig, key="l"):
    def on_key(event):
        if event.key != key:
            return

        ax = fig.gca()

        if ax.get_yscale() == "linear":
            ax.set_yscale("log")
        else:
            ax.set_yscale("linear")

        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("key_press_event", on_key)


def plotxy_old(
    x_list,
    y_list,
    *,
    labels=None,
    color=None,
    linestyle=["-"],
    linewidth=[1.2],
    xlabel="x",
    ylabel=None,
    ylog=False,
    legend=True,
    cursor=False,
    ncols=None,
    layout_kwargs=None,
    legend_kwargs=None,
    **plot_kwargs,
):
    from . import figure

    if not isinstance(x_list, (list, tuple)):
        x_list = [x_list]

    if not isinstance(y_list, (list, tuple)):
        y_list = [y_list]

    n_source = len(y_list)

    if len(x_list) == 1 and n_source > 1:
        x_list = x_list * n_source

    if len(x_list) != n_source:
        raise ValueError(
            f"x_list length ({len(x_list)}) does not match "
            f"y_list length ({n_source})"
        )

    x_list = [_to_1d(x) for x in x_list]
    y_list = [_to_2d(y) for y in y_list]

    n_signal = y_list[0].shape[0]

    rows = []
    errors = []

    for j, (x, y) in enumerate(zip(x_list, y_list)):
        rows.append((j, x.size, *y.shape))

        if y.shape[0] != n_signal:
            errors.append(f"y_list[{j}]: rows={y.shape[0]} (expected {n_signal})")
        if y.shape[1] != x.size:
            errors.append(f"idx {j}: x.size={x.size}, y.cols={y.shape[1]}")

    if errors:
        header = " idx (source) | x.size | y.rows | y.cols "
        sep = "-" * len(header)
        table = "\n".join(
            f"{j:4d} | {xs:6d} | {yr:6d} | {yc:6d}"
            for j, xs, yr, yc in rows
        )

        raise ValueError(
            "Input dimension check failed:\n"
            + "\n".join(errors)
            + "\n\nOverview of all sources:\n"
            + header
            + "\n"
            + sep
            + "\n"
            + table
        )

    if labels is None:
        labels = [str(j + 1) for j in range(n_source)]
    if len(labels) != n_source:
        raise ValueError(
            f"labels length ({len(labels)}) must match number of sources ({n_source})"
        )

    if ylabel is None:
        ylabel = [f"$y_{i+1}$" for i in range(n_signal)]
    if len(ylabel) != n_signal:
        raise ValueError(
            f"ylabel length ({len(ylabel)}) must match number of rows ({n_signal})"
        )

    if color is None:
        color = misc.color(n_source)
    if len(linewidth) == 1:
        linestyle = [linestyle[0]] * n_source
    if len(linewidth) == 1:
        linewidth = [linewidth[0]] * n_source

    if len(color) != n_source:
        raise ValueError(f"color length ({len(color)}) must match number of sources")
    if len(linestyle) != n_source:
        raise ValueError(
            f"linestyle length ({len(linestyle)}) must match number of sources"
        )
    if len(linewidth) != n_source:
        raise ValueError(
            f"linewidth length ({len(linewidth)}) must match number of sources"
        )

    if ncols is None:
        ncols = 1

    max_rows_per_fig = 6 if ncols == 1 else n_signal
    max_figs = 8

    figs = []
    axes_all = []

    n_figs = int(np.ceil(n_signal / max_rows_per_fig))
    if n_figs > max_figs:
        print("Warning: more than 8 figures requested. Truncating output.")
        n_figs = max_figs

    for f in range(n_figs):
        i0 = f * max_rows_per_fig
        i1 = min((f + 1) * max_rows_per_fig, n_signal)
        nrows = int(np.ceil((i1 - i0) / ncols))

        fig_layout = layout_kwargs if layout_kwargs is not None else figure.layout(nrows, ncols)
        axes, fig, _ = figure.subplot(nrows, ncols, **(fig_layout or {}))

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
                    **plot_kwargs,
                )
                if global_i == 0:
                    legend_handles.append(h)

            if ylog:
                ax.set_yscale("log")

            ax.set_ylabel(ylabel[global_i])
            ax.grid(True)

            if ylog:
                figure.axistight(ax, p=(0, 0.05), axes=("x", "ylog"))
                ax.yaxis.set_major_locator(mticker.LogLocator(base=10.0, subs=(1.0,)))
                ax.yaxis.set_major_formatter(mticker.LogFormatterMathtext(base=10.0))
                ax.yaxis.set_minor_locator(mticker.NullLocator())
            else:
                figure.axistight(ax, p=(0, 0.05), axes=("x", "y"))

            if cursor:
                mplcursors.cursor(ax, hover=False)

        for idx, ax in enumerate(axes):
            row = idx // ncols
            if row == nrows - 1:
                ax.set_xlabel(xlabel)

        if legend:
            legend_kwargs = legend_kwargs or {}
            right_edge = max(ax.get_position().x1 for ax in fig.axes)
            top_edge = max(ax.get_position().y1 for ax in fig.axes)

            fig.legend(
                legend_handles,
                labels,
                loc="lower right",
                bbox_to_anchor=(right_edge, top_edge + 0.02),
                bbox_transform=fig.transFigure,
                ncol=n_source,
                columnspacing=1.0,
                handlelength=1.5,
                handletextpad=0.5,
                borderaxespad=0,
                frameon=True,
                **legend_kwargs,
            )

        figure.size(fig)
        figure.log_toggle(fig, key="l")
        figure.enable_popout(fig, key="p")

    if len(figs) == 1:
        figs = figs[0]

    return figs, axes_all


def _to_1d(x):
    x = np.asarray(x)
    if x.ndim == 2 and 1 in x.shape:
        return x.reshape(-1)
    if x.ndim != 1:
        raise ValueError("x must be 1D or (1,N)/(N,1)")
    return x


def _to_2d(y):
    y = np.asarray(y)
    if y.ndim == 1:
        return y.reshape(1, -1)
    if y.ndim != 2:
        raise ValueError("y must be 1D or 2D")
    return y


def _as_pair(x):
    if isinstance(x, (int, float)):
        return (float(x), float(x))
    x = tuple(x)
    if len(x) != 2:
        raise ValueError("Expected scalar or length-2 iterable")
    return (float(x[0]), float(x[1]))


def _latex_figwidth_cm(preset="single"):
    preset = str(preset).lower()
    if preset in ("single", "half", "onecol", "one-col", "1col", "1-col"):
        return 8.6
    if preset in ("double", "twocol", "two-col", "2col", "2-col"):
        return 17.8
    if preset in ("beamer", "slide"):
        return 12.8
    raise ValueError("Unknown preset. Use 'single', 'double', 'half', or 'beamer'.")


def _dict_tight_from_cm(fig_cm, gap_cm, marg_h_cm, marg_w_cm):
    h_cm, w_cm = _as_pair(fig_cm)
    gap_h, gap_w = _as_pair(gap_cm)
    mh0, mh1 = _as_pair(marg_h_cm)
    mw0, mw1 = _as_pair(marg_w_cm)

    if h_cm <= 0 or w_cm <= 0:
        raise ValueError("fig_cm must be positive")
    if min(gap_h, gap_w, mh0, mh1, mw0, mw1) < 0:
        raise ValueError("gap/margins must be non-negative")

    return {
        "gap": [gap_h / h_cm, gap_w / w_cm],
        "marg_h": [mh0 / h_cm, mh1 / h_cm],
        "marg_w": [mw0 / w_cm, mw1 / w_cm],
    }
