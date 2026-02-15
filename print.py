#%%

import os
import sys
import subprocess

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


def savefig(
    fig,
    filename,
    folder='.',
    figsize=(10, 16),
    formats=('pdf',),
    label_size=10,
    title_size=12,
    legend_size=9,
    legend_loc='best',
    fontname='Arial',
    dpi=1200,
    renderer=None,
    tight=False,
    openfile=True
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
    legend_loc : str or int
        Legend location (matplotlib convention).
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
            leg.set_title(leg.get_title().get_text())
            leg.set_frame_on(True)
            leg.set_bbox_to_anchor(None)
            try:
                leg.set_loc(legend_loc)
            except Exception:
                leg._loc = legend_loc  # fallback for older matplotlib
            for txt in leg.get_texts():
                txt.set_fontsize(legend_size)
                txt.set_fontname(fontname)

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

    # --- open only first saved file ---
    if openfile and first_out is not None:
        _open_file(first_out)
#%%