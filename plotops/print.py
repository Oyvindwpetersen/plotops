#%%

import os
import sys
import subprocess
import string

#%%

def _open_file(path):
    """Open a file with the default application (cross-platform)."""
    path = os.path.abspath(path)

    if sys.platform.startswith('win'):
        os.startfile(path)  # noqa: S606
    elif sys.platform == 'darwin':
        subprocess.run(['open', path], check=False)
    else:
        subprocess.run(['xdg-open', path], check=False)


def _index_to_letters(i):
    """Convert 0-based index to letters: 0->a, 25->z, 26->aa."""
    letters = string.ascii_lowercase
    out = []
    i += 1  # switch to 1-based for base-26 conversion
    while i > 0:
        i, rem = divmod(i - 1, 26)
        out.append(letters[rem])
    return ''.join(reversed(out))


def savefig(
    fig,
    filename,
    folder='.',
    figsize=(10, 16),
    formats=('pdf',),
    label_size=10,
    title_size=12,
    legend_size=9,
    legend_loc=None,
    fontname='Arial',
    dpi=1200,
    renderer=None,
    tight=False,
    openfile=True,
    panel_labels=True,
    panel_loc=(-0.14, -0.10),
    panel_suffix=')',
    panel_weight='semibold'
):
    """
    Save a matplotlib figure with consistent publication settings.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure handle.
    filename : str
        Base filename without extension.
    folder : str
        Output folder (relative or absolute).
    figsize : (float, float)
        Figure size (height,width) in cm.
    formats : str or iterable of str
        Output formats, e.g. 'pdf', 'png', ('pdf','jpg').
    label_size : float
        Font size for x/y labels.
    title_size : float
        Font size for titles.
    legend_size : float
        Font size for legend.
    legend_loc : str or int or None
        Optional legend location override (matplotlib convention).
        If None, keep the legend's existing placement.
    fontname : str
        Font family name (default: Arial).
    dpi : int
        Resolution for raster formats.
    renderer : str or None
        Backend renderer (e.g. 'pdf', 'agg'). Rarely needed.
    tight : bool
        Use bbox_inches='tight'.
    openfile : bool
        If True, open only the first saved file in the `formats` list.
    panel_labels : bool or iterable of str
        If True, add subplot labels ('a)', 'b)', ... ) at save time only.
        If iterable, use the provided labels in axis order.
    panel_loc : (float, float)
        Label position in axes coordinates (default: lower-left outside axes).
    panel_suffix : str
        Suffix appended to auto-generated labels.
    panel_weight : str
        Font weight for panel labels (default: semibold).
    """

    # --- ensure formats iterable ---
    if isinstance(formats, str):
        formats = (formats,)
    formats = tuple(formats)

    # --- ensure folder exists ---
    os.makedirs(folder, exist_ok=True)

    # --- resolve folder for printing (and for clarity) ---
    folder_abs = os.path.abspath(folder)
    print_folder = folder_abs if (folder == '.' or not os.path.isabs(folder)) else folder

    # --- set figure size ---
    cm = 1 / 2.54
    fig.set_size_inches(figsize[1] * cm, figsize[0] * cm, forward=True)

    # --- update text properties ---
    def _style_legend(leg):
        if leg is None:
            return

        leg.set_title(leg.get_title().get_text())
        leg.set_frame_on(True)

        if legend_loc is not None:
            leg.set_bbox_to_anchor(None)
            try:
                leg.set_loc(legend_loc)
            except Exception:
                leg._loc = legend_loc  # fallback for older matplotlib

        for txt in leg.get_texts():
            txt.set_fontsize(legend_size)
            txt.set_fontname(fontname)

    axis_legends = []
    for ax in fig.axes:
        ax.title.set_fontsize(title_size)
        ax.title.set_fontname(fontname)

        ax.xaxis.label.set_fontsize(label_size)
        ax.yaxis.label.set_fontsize(label_size)
        ax.xaxis.label.set_fontname(fontname)
        ax.yaxis.label.set_fontname(fontname)

        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontsize(label_size)
            tick.set_fontname(fontname)

        leg = ax.get_legend()
        if leg is not None:
            axis_legends.append(leg)
            _style_legend(leg)

    fig_legends = list(getattr(fig, 'legends', []))
    for leg in fig_legends:
        _style_legend(leg)

    if axis_legends and fig_legends:
        print(
            'Warning: figure contains both axis-level and figure-level legends. '
            'savefig() styled both; verify the exported legend layout.'
        )

    # --- panel labels only for export ---
    panel_artists = []
    if panel_labels and len(fig.axes) > 1:
        if isinstance(panel_labels, bool):
            labels = [_index_to_letters(i) + panel_suffix for i in range(len(fig.axes))]
        else:
            labels = list(panel_labels)
            if len(labels) < len(fig.axes):
                raise ValueError('panel_labels iterable must have at least one label per axis')

        for i, ax in enumerate(fig.axes):
            va = 'top' if panel_loc[1] < 0 else 'bottom'
            t = ax.text(
                panel_loc[0],
                panel_loc[1],
                labels[i],
                transform=ax.transAxes,
                ha='left',
                va=va,
                fontsize=title_size,
                fontname=fontname,
                fontweight=panel_weight
            )
            panel_artists.append(t)

    # --- save ---
    first_out = None
    for k, fmt in enumerate(formats):
        out = os.path.join(folder, f'{filename}.{fmt}')
        fig.savefig(
            out,
            dpi=dpi,
            format=fmt,
            bbox_inches='tight' if tight else None,
            backend=renderer
        )

        if first_out is None:
            first_out = out

        print(f'saving {filename} to {print_folder} in {fmt}')

    # --- remove temporary panel labels so interactive view stays unchanged ---
    for artist in panel_artists:
        artist.remove()

    # --- open only first saved file ---
    if openfile and first_out is not None:
        _open_file(first_out)
#%%
