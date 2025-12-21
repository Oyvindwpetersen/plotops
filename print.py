#%%

import os

#%%

def savefig(
    fig,
    filename,
    folder='.',
    size_cm=(16, 10),
    formats=('pdf',),
    label_size=10,
    title_size=12,
    legend_size=9,
    legend_loc='best',
    fontname='Arial',
    dpi=1200,
    renderer=None,
    tight=False
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
        Output folder.
    size_cm : (float, float)
        Figure size (width, height) in cm.
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
    """

    # --- ensure formats iterable ---
    if isinstance(formats, str):
        formats = (formats,)

    # --- ensure folder exists ---
    os.makedirs(folder, exist_ok=True)

    # --- set figure size ---
    cm = 1 / 2.54
    fig.set_size_inches(size_cm[0]*cm, size_cm[1]*cm, forward=True)

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
            leg._loc = legend_loc
            for txt in leg.get_texts():
                txt.set_fontsize(legend_size)
                txt.set_fontname(fontname)

    # --- save ---
    for fmt in formats:
        out = os.path.join(folder, f'{filename}.{fmt}')
        fig.savefig(
            out,
            dpi=dpi,
            format=fmt,
            bbox_inches='tight' if tight else None,
            backend=renderer
        )


#%%