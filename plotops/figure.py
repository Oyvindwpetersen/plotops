#%%

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk
from PyQt5 import QtCore   # or PyQt6 / PySide2 depending on backend
import os

#%%

def subplot(nh, nw,
            layout=None,
            *,
            gap=0.05,
            marg_h=0.1,
            marg_w=0.05,
            weight_h=None,
            weight_w=None,
            fig=None,
            xlabel=None,
            ylabel=None,
            xlog=False,
            ylog=False,
            xlim=None,
            ylim=None,
            grid=True,
            **kwargs):
    '''
    MATLAB-equivalent tight_subplot using absolute normalized gaps and margins.

    This version optionally accepts a layout dictionary returned from
    `figure.layout(...)`.

    Parameters
    ----------
    nh, nw : int
        Number of rows and columns.

    layout : dict, optional
        Dictionary returned by `layout(...)`. If provided,
        its normalized 'gap', 'marg_h', 'marg_w' values are used.

    xlabel, ylabel : str | list of str | None
        Axis labels to apply after subplot creation. `xlabel` is applied to the
        bottom row axes, while `ylabel` is applied axis-by-axis in row-major order.
    xlog, ylog : bool | list of bool
        Log scaling flags. Scalars are broadcast to all axes.
    xlim, ylim : tuple | list of tuple | None
        Optional axis limits. Scalars/tuples are broadcast to all axes.
    grid : bool | list of bool
        Grid visibility per axis. Scalars are broadcast to all axes.

    Returns
    -------
    axes : ndarray of Axes, shape (nh, nw)
    fig  : matplotlib.figure.Figure
    pos  : list of [left, bottom, width, height]
    '''

    # -------------------------------------------------
    # Unpack layout dict if provided
    # -------------------------------------------------
    if isinstance(layout, dict):
        gap = layout.get('gap', gap)
        marg_h = layout.get('marg_h', marg_h)
        marg_w = layout.get('marg_w', marg_w)

        # Optional: apply figure size automatically
        if 'figsize' in layout:
            h_cm, w_cm = layout['figsize']
            if fig is None:
                import matplotlib.pyplot as plt
                fig = plt.figure()
            cm = 1 / 2.54
            fig.set_size_inches(w_cm * cm, h_cm * cm, forward=True)

    # -------------------------------------------------
    # Normalize inputs (unchanged logic)
    # -------------------------------------------------
    import numpy as np
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.figure()

    def _to_n(value, n, name):
        if value is None:
            return [None] * n
        if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
            return [value] * n
        value = list(value)
        if len(value) == 1:
            return value * n
        if len(value) != n:
            raise ValueError(f'{name} length ({len(value)}) must be 1 or {n}')
        return value

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

    weight_h /= weight_h.sum()
    weight_w /= weight_w.sum()

    H = 1.0 - sum(marg_h) - gap[0] * (nh - 1)
    W = 1.0 - sum(marg_w) - gap[1] * (nw - 1)

    if H <= 0 or W <= 0:
        raise ValueError('Margins and gaps leave no space for axes')

    axh = H * weight_h
    axw = W * weight_w

    axes_flat = []
    pos = []

    y = 1.0 - marg_h[1]
    for ih in range(nh):
        y -= axh[ih]
        x = marg_w[0]

        for iw in range(nw):
            p = [x, y, axw[iw], axh[ih]]
            pos.append(p)

            axes_flat.append(fig.add_axes(p))

            x += axw[iw] + gap[1]

        y -= gap[0]

    n_axes = len(axes_flat)
    xlog_list = _to_n(xlog, n_axes, 'xlog')
    ylog_list = _to_n(ylog, n_axes, 'ylog')
    xlim_list = _to_n(xlim, n_axes, 'xlim')
    ylim_list = _to_n(ylim, n_axes, 'ylim')
    grid_list = _to_n(grid, n_axes, 'grid')
    ylabel_list = _to_n(ylabel, n_axes, 'ylabel')

    if xlabel is None:
        xlabel_list = [None] * n_axes
    else:
        if isinstance(xlabel, (list, tuple)) and not isinstance(xlabel, (str, bytes)):
            xlabel_values = list(xlabel)
            if len(xlabel_values) == nw:
                xlabel_list = [None] * n_axes
                for idx, ax in enumerate(axes_flat):
                    row = idx // nw
                    col = idx % nw
                    if row == nh - 1:
                        xlabel_list[idx] = xlabel_values[col]
            else:
                xlabel_list = _to_n(xlabel, n_axes, 'xlabel')
        else:
            xlabel_list = [None] * n_axes
            for idx in range(n_axes):
                if idx // nw == nh - 1:
                    xlabel_list[idx] = xlabel

    for idx, ax in enumerate(axes_flat):
        if xlog_list[idx]:
            ax.set_xscale('log')
        if ylog_list[idx]:
            ax.set_yscale('log')
        if xlabel_list[idx] is not None:
            ax.set_xlabel(xlabel_list[idx])
        if ylabel_list[idx] is not None:
            ax.set_ylabel(ylabel_list[idx])
        if xlim_list[idx] is not None:
            ax.set_xlim(xlim_list[idx])
        if ylim_list[idx] is not None:
            ax.set_ylim(ylim_list[idx])
        ax.grid(bool(grid_list[idx]))

    axes = np.asarray(axes_flat, dtype=object).reshape(nh, nw)

    return axes, fig, pos


def subplot_old(nh, nw,
                  gap=0.05,
                  marg_h=0.1,
                  marg_w=0.05,
                  weight_h=None,
                  weight_w=None,
                  fig=None,
                  **kwargs):
    """
    MATLAB-equivalent tight_subplot using absolute normalized gaps and margins.

    Parameters
    ----------
    nh, nw : int
        Number of rows and columns.
    gap : float or (float, float)
        Absolute gap size in normalized figure units (gap_h, gap_w).
    marg_h : float or (float, float)
        Absolute margins (bottom, top) in normalized units.
    marg_w : float or (float, float)
        Absolute margins (left, right) in normalized units.
    weight_h : array-like, optional
        Relative row heights (length nh).
    weight_w : array-like, optional
        Relative column widths (length nw).
    fig : matplotlib.figure.Figure, optional
        Figure to use (created if None).
    Returns
    -------
    axes : list of Axes
        Axes handles (row-wise, top-left first).
    pos : list of list
        [left, bottom, width, height] for each axes.
    """

    # --- normalize inputs ---
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
        raise ValueError('weight_h must have length nh')
    if len(weight_w) != nw:
        raise ValueError('weight_w must have length nw')

    weight_h /= weight_h.sum()
    weight_w /= weight_w.sum()

    # --- available space ---
    H = 1.0 - sum(marg_h) - gap[0] * (nh - 1)
    W = 1.0 - sum(marg_w) - gap[1] * (nw - 1)

    if H <= 0 or W <= 0:
        raise ValueError('Margins and gaps leave no space for axes')

    axh = H * weight_h
    axw = W * weight_w

    axes = []
    pos = []

    # --- build axes (top-left first) ---
    y = 1.0 - marg_h[1]
    for ih in range(nh):
        y -= axh[ih]
        x = marg_w[0]

        for iw in range(nw):
            p = [x, y, axw[iw], axh[ih]]
            pos.append(p)

            axes.append(fig.add_axes(p))

            x += axw[iw] + gap[1]

        y -= gap[0]

    return axes, fig, pos 


#%%

def layout(
    nrow,
    ncol,
    *,
    subsize=(3.0, 6.0),
    figsize=None,
    gap=(1.5, 2.0),
    marg_h=(1.2, 1.0),
    marg_w=(2, 0.8),
    latex=None,
    aspect=None
):
    """
    Compute figure and subplot sizing in cm, and a normalized tight-layout dict.

    Modes
    -----
    Mode A (subsize-driven):
        Provide `subsize` and leave `figsize=None`.
    Mode B (figure-driven):
        Provide `figsize` and leave `subsize=None`.

    Parameters
    ----------
    nrow, ncol : int
        Number of subplot rows and columns.
    subsize : None | (float, float)
        (h_ax, w_ax) size of ONE subplot in cm.
    figsize : None | (float, float)
        (h_fig, w_fig) of the full figure in cm.
    gap : float | (float, float)
        Inter-subplot gaps in cm: (gap_h, gap_w).
    marg_h : float | (float, float)
        Figure margins in cm: (bottom, top).
    marg_w : float | (float, float)
        Figure margins in cm: (left, right).
    latex : None | str | dict
        Optional LaTeX sizing preset (width/height overrides).
    aspect : None | float
        Only used in subplot-driven mode when `latex` sets width but not height.
        Enforces: height = width / aspect (aspect = W/H).

    Returns
    -------
    out : dict
        Dictionary with both absolute (cm) and normalized (0..1) layout:

        - 'figsize'    : (h_fig_cm, w_fig_cm)
        - 'subsize_cm' : (h_ax_cm, w_ax_cm)
        - 'gap_cm'     : (gap_h_cm, gap_w_cm)
        - 'marg_h_cm'  : (bottom_cm, top_cm)
        - 'marg_w_cm'  : (left_cm, right_cm)
        - 'gap'        : [gap_h_norm, gap_w_norm]
        - 'marg_h'     : [bottom_norm, top_norm]
        - 'marg_w'     : [left_norm, right_norm]

    Raises
    ------
    ValueError
        If inputs are inconsistent or margins/gaps leave no space.
    """

    if int(nrow) != nrow or int(ncol) != ncol or nrow <= 0 or ncol <= 0:
        raise ValueError('nrow and ncol must be positive integers')
    nrow = int(nrow)
    ncol = int(ncol)

    if subsize is None and figsize is None:
        raise ValueError('Provide subsize or figsize')

    # If both are given -> figsize takes precedence (keeps your original behavior)
    if subsize is not None and figsize is not None:
        subsize = None

    gap_h, gap_w = _as_pair(gap)
    mh0, mh1 = _as_pair(marg_h)
    mw0, mw1 = _as_pair(marg_w)

    # ------------------------------------------------------------
    # Parse latex option into target width/height overrides
    # ------------------------------------------------------------
    target_w = None
    target_h = None

    if latex is not None:
        if isinstance(latex, str):
            target_w = _latex_figwidth_cm(latex)
        elif isinstance(latex, dict):
            if 'width' in latex:
                target_w = float(latex['width'])
            if 'height' in latex:
                target_h = float(latex['height'])
        else:
            raise ValueError('latex must be None, a string preset, or a dict')

        if target_w is not None and target_w <= 0:
            raise ValueError('latex width must be positive')
        if target_h is not None and target_h <= 0:
            raise ValueError('latex height must be positive')

    # ------------------------------------------------------------
    # Mode A: subplot-driven
    # ------------------------------------------------------------
    if subsize is not None:
        h_ax, w_ax = _as_pair(subsize)
        if h_ax <= 0 or w_ax <= 0:
            raise ValueError('subsize must be positive')

        if target_w is not None:
            usable_w = target_w - mw0 - mw1 - (ncol - 1) * gap_w
            if usable_w <= 0:
                raise ValueError('Margins/gaps too large for requested latex width')
            w_ax = usable_w / ncol
            w_fig = target_w
        else:
            w_fig = ncol * w_ax + (ncol - 1) * gap_w + mw0 + mw1

        if target_h is not None:
            h_fig = target_h
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError('Margins/gaps too large for requested latex height')
            h_ax = usable_h / nrow
        elif (target_w is not None) and (aspect is not None):
            aspect = float(aspect)
            if aspect <= 0:
                raise ValueError('aspect must be positive')
            h_fig = w_fig / aspect
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError('Margins/gaps too large for aspect-implied height')
            h_ax = usable_h / nrow
        else:
            h_fig = nrow * h_ax + (nrow - 1) * gap_h + mh0 + mh1

    # ------------------------------------------------------------
    # Mode B: figure-driven
    # ------------------------------------------------------------
    else:
        h_fig, w_fig = _as_pair(figsize)  # NOTE: (h, w)
        if h_fig <= 0 or w_fig <= 0:
            raise ValueError('figsize must be positive')

        if target_w is not None:
            w_fig = target_w
        if target_h is not None:
            h_fig = target_h

        usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
        usable_w = w_fig - mw0 - mw1 - (ncol - 1) * gap_w
        if usable_h <= 0 or usable_w <= 0:
            raise ValueError('Margins and gaps leave no space for axes')

        h_ax = usable_h / nrow
        w_ax = usable_w / ncol

    if h_fig <= 0 or w_fig <= 0:
        raise ValueError('Computed figure size is not positive')

    # ------------------------------------------------------------
    # Compute normalized tight layout values (merged from _dict_tight_from_cm)
    # ------------------------------------------------------------
    if min(gap_h, gap_w, mh0, mh1, mw0, mw1) < 0:
        raise ValueError('gap/margins must be non-negative')

    fig_layout = {
        # absolute (cm)
        'figsize': (h_fig, w_fig),
        'subsize_cm': (h_ax, w_ax),
        'gap_cm': (gap_h, gap_w),
        'marg_h_cm': (mh0, mh1),
        'marg_w_cm': (mw0, mw1),

        # normalized (0..1), compatible with figure.subplot(...)
        'gap':    [gap_h / h_fig, gap_w / w_fig],
        'marg_h': [mh0 / h_fig,   mh1 / h_fig],
        'marg_w': [mw0 / w_fig,   mw1 / w_fig],
    }

    return fig_layout



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
    aspect=None
):
    '''
    Compute figure size (cm), subsize size (cm), and a normalized tight-layout
    dictionary compatible with your `subsize(...)` function (gap/margins in
    normalized figure units).

    This merges the two workflows:

    Mode A (subsize-driven)
    -----------------------
    Provide `subsize` and leave `figsize=None`:
      - Computes figure size from subsize size + gaps + margins.
      - If `latex` is provided, it overrides the figure width and adapts subsize width.
        Height can be controlled by `aspect` or by specifying latex height.

    Mode B (figure-driven)
    ----------------------
    Provide `figsize` and leave `subsize=None`:
      - Computes subsize size from figure size + gaps + margins.
      - If `latex` is provided, it can override the figure width (and optionally height).

    Parameters
    ----------
    nrow, ncol : int
        Number of subplot rows and columns.
    subsize : None | (float, float)
        (h_ax, w_ax) size of ONE subplot in cm. If provided, `figsize` must be None.
    figsize : None | (float, float)
        (h_fig, w_fig) of the full figure in cm. If provided, `subsize` must be None.
    gap : float | (float, float)
        Inter-subplot gaps in cm: (gap_h, gap_w).
    marg_h : float | (float, float)
        Figure margins in cm: (bottom, top).
    marg_w : float | (float, float)
        Figure margins in cm: (left, right).
    latex : None | str | dict
        Optional LaTeX sizing preset.

        If str: one of 'single', 'double', 'beamer' (common widths in cm).
          - In subplot-driven mode: overrides figure width; subplot width adapts.
          - In figure-driven mode: overrides figure width; height kept from fig.

        If dict:
          - Must include 'width' to override width, and may include 'height' to override height.
          - In subplot-driven mode: sets target width, optionally target height.
          - In figure-driven mode: overrides width and/or height.

    aspect : None | float
        Only used in subplot-driven mode when `latex` sets the width but not the height.
        Enforces: height = width / aspect  (aspect = W/H).
        Example: aspect=1.6.

    Returns
    -------
    figsize_out : (float, float)
        (h_fig, w_fig) of the figure.
    dict_tight : dict
        Normalized tight layout dictionary:
          {'gap':[gap_h_norm, gap_w_norm], 'marg_h':[bottom_norm, top_norm], 'marg_w':[left_norm, right_norm]}
    subsize_out : (float, float)
        (h_ax, w_ax) resulting subplot size in cm.

    Raises
    ------
    ValueError
        If both `subsize` and `figsize` are provided, or both are None,
        or if margins/gaps leave no space.
    '''
    if int(nrow) != nrow or int(ncol) != ncol or nrow <= 0 or ncol <= 0:
        raise ValueError('nrow and ncol must be positive integers')
    nrow = int(nrow)
    ncol = int(ncol)

    if subsize is None and figsize is None:
        raise ValueError('Provide subsize or figsize')

    # If both are given -> figsize takes precedence
    if subsize is not None and figsize is not None:
        subsize = None

    gap_h, gap_w = _as_pair(gap)
    mh0, mh1 = _as_pair(marg_h)
    mw0, mw1 = _as_pair(marg_w)

    # ------------------------------------------------------------
    # Parse latex option into target width/height overrides
    # ------------------------------------------------------------
    target_w = None
    target_h = None

    if latex is not None:
        if isinstance(latex, str):
            target_w = _latex_figwidth_cm(latex)
        elif isinstance(latex, dict):
            if 'width' in latex:
                target_w = float(latex['width'])
            if 'height' in latex:
                target_h = float(latex['height'])
        else:
            raise ValueError('latex must be None, a string preset, or a dict')

        if target_w is not None and target_w <= 0:
            raise ValueError('latex width must be positive')
        if target_h is not None and target_h <= 0:
            raise ValueError('latex height must be positive')

    # ------------------------------------------------------------
    # Mode A: subplot-driven
    # ------------------------------------------------------------
    if subsize is not None:
        h_ax, w_ax = _as_pair(subsize)
        if h_ax <= 0 or w_ax <= 0:
            raise ValueError('subsize must be positive')

        if target_w is not None:
            usable_w = target_w - mw0 - mw1 - (ncol - 1) * gap_w
            if usable_w <= 0:
                raise ValueError('Margins/gaps too large for requested latex width')
            w_ax = usable_w / ncol
            w_fig = target_w
        else:
            w_fig = ncol * w_ax + (ncol - 1) * gap_w + mw0 + mw1

        # Height strategy in subplot-driven mode:
        if target_h is not None:
            h_fig = target_h
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError('Margins/gaps too large for requested latex height')
            h_ax = usable_h / nrow
        elif (target_w is not None) and (aspect is not None):
            aspect = float(aspect)
            if aspect <= 0:
                raise ValueError('aspect must be positive')
            h_fig = w_fig / aspect
            usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
            if usable_h <= 0:
                raise ValueError('Margins/gaps too large for aspect-implied height')
            h_ax = usable_h / nrow
        else:
            h_fig = nrow * h_ax + (nrow - 1) * gap_h + mh0 + mh1

    # ------------------------------------------------------------
    # Mode B: figure-driven
    # ------------------------------------------------------------
    else:
        h_fig, w_fig = _as_pair(figsize)  # NOTE: (h, w)
        if h_fig <= 0 or w_fig <= 0:
            raise ValueError('figsize must be positive')

        if target_w is not None:
            w_fig = target_w
        if target_h is not None:
            h_fig = target_h

        usable_h = h_fig - mh0 - mh1 - (nrow - 1) * gap_h
        usable_w = w_fig - mw0 - mw1 - (ncol - 1) * gap_w
        if usable_h <= 0 or usable_w <= 0:
            raise ValueError('Margins and gaps leave no space for axes')

        h_ax = usable_h / nrow
        w_ax = usable_w / ncol

    if h_fig <= 0 or w_fig <= 0:
        raise ValueError('Computed figure size is not positive')

    dict_tight = _dict_tight_from_cm(
        (h_fig, w_fig),
        gap_cm=gap,
        marg_h_cm=marg_h,
        marg_w_cm=marg_w
    )

    figsize_out = (h_fig, w_fig)
    subsize_out = (h_ax, w_ax)

    return figsize_out, dict_tight, subsize_out


def latex_preset_defaults(preset='single'):
    '''
    Convenience defaults (cm) for gaps and margins that usually work well with LaTeX sizing.

    Parameters
    ----------
    preset : str
        'single' | 'double' | 'beamer'

    Returns
    -------
    defaults : dict
        Dictionary with:
        - 'fig_width_cm'
        - 'gap_cm'    : (gap_h_cm, gap_w_cm)
        - 'marg_h_cm' : (bottom_cm, top_cm)
        - 'marg_w_cm' : (left_cm, right_cm)
    '''
    fig_width_cm = _latex_figwidth_cm(preset)

    if str(preset).lower() in ('double', 'twocol', 'two-col', '2col', '2-col'):
        gap_cm = (0.6, 0.6)
        marg_h_cm = (1.2, 0.9)
        marg_w_cm = (1.1, 0.7)
    elif str(preset).lower() in ('beamer', 'slide'):
        gap_cm = (0.7, 0.7)
        marg_h_cm = (1.0, 0.8)
        marg_w_cm = (1.0, 0.8)
    else:  # single
        gap_cm = (0.5, 0.5)
        marg_h_cm = (1.1, 0.9)
        marg_w_cm = (1.0, 0.7)

    return {
        'fig_width_cm': fig_width_cm,
        'gap_cm': gap_cm,
        'marg_h_cm': marg_h_cm,
        'marg_w_cm': marg_w_cm,
    }


def _as_pair(x):
    '''
    Normalize a scalar or a 2-tuple to a 2-tuple.

    Parameters
    ----------
    x : float | int | (float, float)
        If scalar, returned as (x, x). If iterable, must have length 2.

    Returns
    -------
    pair : (float, float)
        Two-element tuple.
    '''
    if isinstance(x, (int, float)):
        return (float(x), float(x))
    x = tuple(x)
    if len(x) != 2:
        raise ValueError('Expected scalar or length-2 iterable')
    return (float(x[0]), float(x[1]))


def _latex_figwidth_cm(preset='single'):
    '''
    Return common LaTeX figure widths in cm (de facto standards).
    '''
    preset = str(preset).lower()
    if preset in ('single', 'half', 'onecol', 'one-col', '1col', '1-col'):
        return 8.6
    if preset in ('double', 'twocol', 'two-col', '2col', '2-col'):
        return 17.8
    if preset in ('beamer', 'slide'):
        return 12.8
    raise ValueError("Unknown preset. Use 'single', 'double', 'half', or 'beamer'.")


def _dict_tight_from_cm(
    fig_cm,
    gap_cm,
    marg_h_cm,
    marg_w_cm
):
    '''
    Convert absolute gaps/margins in cm to normalized (0..1) values.

    Parameters
    ----------
    fig_cm : (float, float)
        (h_fig_cm, w_fig_cm) of the full figure.
    gap_cm : float | (float, float)
        (gap_h_cm, gap_w_cm)
    marg_h_cm : float | (float, float)
        (bottom_cm, top_cm).
    marg_w_cm : float | (float, float)
        (left_cm, right_cm).
    '''
    h_cm, w_cm = _as_pair(fig_cm)  # NOTE: (h, w)
    gap_h, gap_w = _as_pair(gap_cm)
    mh0, mh1 = _as_pair(marg_h_cm)
    mw0, mw1 = _as_pair(marg_w_cm)

    if h_cm <= 0 or w_cm <= 0:
        raise ValueError('fig_cm must be positive')
    if min(gap_h, gap_w, mh0, mh1, mw0, mw1) < 0:
        raise ValueError('gap/margins must be non-negative')

    return {
        'gap':    [gap_h / h_cm, gap_w / w_cm],
        'marg_h': [mh0 / h_cm,   mh1 / h_cm],
        'marg_w': [mw0 / w_cm,   mw1 / w_cm],
    }

#%%

def syncx(axes):
    """
    Share x-axes across multiple matplotlib Axes.

    Parameters
    ----------
    axes : list of matplotlib.axes.Axes
        List of axes. The first axis is used as reference.
        All subsequent axes will share its x-axis.

    Notes
    -----
    Zooming or panning in one axis updates all linked axes.
    """
    
    if not axes:
        return

    base = axes[0]
    for ax in axes[1:]:
        ax.sharex(base)

#%%

def axistight(ax, p=0.05, axes=('y',)):
    """
    Expand axis limits with relative padding (MATLAB-like behavior).

    Parameters
    ----------
    ax : matplotlib.axes.Axes or iterable of Axes
        Axis (or list of axes) to modify.
    p : float or sequence of float
        Relative padding fraction of data range.
    axes : iterable of str
        Axis specification strings:
        'x', 'y', '+x', '-y', 'x0', 'ylog', etc.

        Prefix '+' or '-' expands only one side.
        Suffix '0' forces lower bound to zero.
        Suffix 'log' applies padding in log10 space.
    """


    # --- allow ax to be a list/tuple ---
    if isinstance(ax, (list, tuple)):
        for a in ax:
            axistight(a, p=p, axes=axes)
        return

    # --- from here: ax is a single Axes ---
    ax.autoscale(enable=True, tight=True)

    if np.isscalar(p):
        p = [p] * len(axes)

    for frac, spec in zip(p, axes):
        log = spec.endswith('log')
        base = spec[:-3] if log else spec          # remove trailing 'log'
        axis = base[-1]                           # now 'x' or 'y'
    
        side = 'both'
        keep_zero = False
    
        if base.startswith('+'):
            side = 'positive'
        elif base.startswith('-'):
            side = 'negative'
        elif base.endswith('0'):
            keep_zero = True
    
        if axis == 'x':
            lim = ax.get_xlim()
            ax.set_xlim(_expand_limits(lim, frac, side, log, keep_zero))
        elif axis == 'y':
            lim = ax.get_ylim()
            ax.set_ylim(_expand_limits(lim, frac, side, log, keep_zero))

        
def _expand_limits(lim, frac, side='both', log=False, keep_zero=False):
    """
    Expand axis limits by a fraction of the data range.

    Parameters
    ----------
    lim : (low, high)
    frac : float
        Relative padding (e.g. 0.05)
    side : {'both', 'positive', 'negative'}
    log : bool
        Operate in log10 space
    keep_zero : bool
        Force lower limit to zero
    """
    lo, hi = lim

    if log:
        lo, hi = np.log10([lo, hi])

    rng = hi - lo
    if rng <= 0:
        return lim

    dlo = frac * rng if side in ('both', 'negative') else 0.0
    dhi = frac * rng if side in ('both', 'positive') else 0.0

    lo -= dlo
    hi += dhi

    if log:
        lo, hi = 10**lo, 10**hi

    if keep_zero:
        lo = 0.0

    return lo, hi

#%%

def tile(nw, nh, side=None, gap_px=10, extra_vgap_px=50,
         edge_px=20, top_gap_px=60, bottom_gap_px=100):
    """
    Tile all open matplotlib figure windows on the screen.

    Parameters
    ----------
    nw : int
        Number of columns of windows.
    nh : int
        Number of rows of windows.
    side : {'l', 'r', None}, optional
        Restrict tiling to left or right half of screen.
    gap_px : int
        Horizontal gap between windows (pixels).
    extra_vgap_px : int
        Additional vertical gap (pixels).
    edge_px : int
        Screen margin on left/right edges.
    top_gap_px : int
        Margin at top of screen.
    bottom_gap_px : int
        Margin at bottom of screen.

    Raises
    ------
    ValueError
        If screen size is insufficient.
    """


    figs = [plt.figure(n) for n in plt.get_fignums()]
    if not figs:
        print('No open figures to tile.')
        return

    # --- get screen size ---
    root = tk.Tk()
    root.withdraw()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.destroy()

    # --- usable screen region ---
    x0 = edge_px
    y0 = top_gap_px
    usable_w = screen_w - 2 * edge_px
    usable_h = screen_h - top_gap_px - bottom_gap_px

    # --- left / right half ---
    if side == 'l':
        usable_w //= 2
    elif side == 'r':
        x0 += usable_w // 2
        usable_w //= 2

    # --- effective vertical gap ---
    vgap = gap_px + extra_vgap_px

    # --- window size ---
    win_w = (usable_w - (nw - 1) * gap_px) // nw
    win_h = (usable_h - (nh - 1) * vgap) // nh

    if win_w <= 0 or win_h <= 0:
        raise ValueError('Screen too small for requested layout.')

    backend = matplotlib.get_backend().lower()

    # --- tile figures ---
    for k, fig in enumerate(figs):
        row = k // nw
        col = k % nw
        if row >= nh:
            break

        x = x0 + col * (win_w + gap_px)
        y = y0 + row * (win_h + vgap)

        mgr = fig.canvas.manager
        fig.set_size_inches(win_w / fig.dpi, win_h / fig.dpi, forward=True)

        # --- TkAgg ---
        if 'tk' in backend:
            mgr.window.wm_geometry(f'{win_w}x{win_h}+{x}+{y}')

        # --- QtAgg ---
        elif 'qt' in backend:
            mgr.window.setGeometry(x, y, win_w, win_h)
            
            _bring_to_front(fig)
                        
        else:
            print(f'Backend {backend} does not support window tiling.')
            
        
def _bring_to_front(fig):
    mgr = fig.canvas.manager
    win = mgr.window

    try:
        # Make sure window is shown
        #win.show()

        # Temporarily toggle "always on top"
        win.setWindowState(
            win.windowState() & ~QtCore.Qt.WindowMinimized
        )
        win.raise_()
        win.activateWindow()

        win.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        win.show()
        win.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
        win.show()

    except Exception as e:
        print('Could not raise window:', e)
  
#%%
  
def size(fig, width_frac=0.5, height_frac=0.5, y_center_frac=2/3):
    """
    Resize and position a matplotlib figure window.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to resize.
    width_frac : float
        Fraction of screen width.
    height_frac : float
        Fraction of screen height.
    y_center_frac : float
        Vertical center position measured from bottom
        (fraction of screen height).
    """

    
    root = tk.Tk()
    root.withdraw()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.destroy()

    win_w = int(screen_w * width_frac)
    win_h = int(screen_h * height_frac)

    x = int((screen_w - win_w) / 2)
    y = int(screen_h * (1 - y_center_frac) - win_h / 2)

    mgr = fig.canvas.manager
    fig.set_size_inches(win_w / fig.dpi, win_h / fig.dpi, forward=True)

    backend = matplotlib.get_backend().lower()

    if 'tk' in backend:
        mgr.window.wm_geometry(f'{win_w}x{win_h}+{x}+{y}')
    elif 'qt' in backend:
        mgr.window.setGeometry(x, y, win_w, win_h)
    
    _bring_to_front(fig)
    
#%%

def enable_log_toggle_old(fig, key='l'):
    
    def on_key(event):
        if event.key != key:
            return

        ax = fig.gca()   # <- THIS is the fix

        if ax.get_yscale() == 'linear':
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')

        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', on_key)


#%%

def log_toggle(fig, key='l'):
    """
    Enable interactive toggling of y-axis between linear and log scale.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Target figure.
    key : str
        Keyboard key used to toggle scale.

    Notes
    -----
    Log scaling is applied only if all y-data are positive.
    """

    def on_key(event):
        if event.key != key:
            return

        ax = fig.gca()   # must be fig, not plt

        if ax.get_yscale() == 'linear':
            for line in ax.lines:
                y = line.get_ydata()
                if np.any(y <= 0):
                    print('Log not valid')
                    return
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')

        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('key_press_event', on_key)

    
#%%
    
def enable_active_axes_tracking(fig):
    state = {'ax': None}

    def on_click(event):
        if event.inaxes is not None:
            state['ax'] = event.inaxes

    fig.canvas.mpl_connect('button_press_event', on_click)
    return state

def popout_active_axes(fig, state):
    ax = state.get('ax', None)
    if ax is None:
        return

    import matplotlib.pyplot as plt

    new_fig, new_ax = plt.subplots()

    for line in ax.lines:
        new_ax.plot(
            line.get_xdata(),
            line.get_ydata(),
            label=line.get_label(),
            linestyle=line.get_linestyle(),
            linewidth=line.get_linewidth(),
            color=line.get_color(),
            marker=line.get_marker(),
        )

    new_ax.set_xlim(ax.get_xlim())
    new_ax.set_ylim(ax.get_ylim())
    new_ax.set_xscale(ax.get_xscale())
    new_ax.set_yscale(ax.get_yscale())

    new_ax.set_xlabel(ax.get_xlabel())
    new_ax.set_ylabel(ax.get_ylabel())
    new_ax.set_title(ax.get_title())

    new_ax.grid(True)

    if ax.get_legend() is not None:
        new_ax.legend()

    new_fig.tight_layout()

    try:
        size(new_fig)
    except Exception:
        pass

    try:
        _bring_to_front(new_fig)
    except Exception:
        pass

    new_fig.canvas.draw_idle()
    return new_fig, new_ax

def enable_popout(fig, key='p'):
    """
    Enable pop-out of active axes into new figure.

    Parameters
    ----------
    fig : Figure
    key : str
        Keyboard trigger.
    """
    state = enable_active_axes_tracking(fig)

    def on_key(event):
        if event.key != key:
            return
        popout_active_axes(fig, state)

    fig.canvas.mpl_connect('key_press_event', on_key)

#%%

from .legacy import enable_log_toggle_old, layout_old, subplot_old
