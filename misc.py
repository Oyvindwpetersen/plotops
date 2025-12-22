import numpy as np

#%%
        
def color(n, type=1):
    """
    Generate a list of RGB colors.

    Parameters
    ----------
    n : int
        Number of colors requested.
    type : int, optional
        Palette type selector.
        type=1 : color-blind–safe (default)
        type=2 : same palette, reordered for higher contrast

    Returns
    -------
    colors_out : list of tuple
        List of RGB tuples in [0, 1].
    """

    # Color-blind–safe qualitative palette (Okabe–Ito style)
    rgb_rel = [
        (0/256,   114/256, 178/256),  # blue
        (213/256, 94/256,  0/256),    # red
        (0/256,   158/256, 115/256),  # green
        (230/256, 159/256, 0/256),    # orange
        (178/256, 75/256,  215/256),  # purple
        (86/256,  180/256, 233/256),  # light blue
        (0.0,     0.0,     0.0),      # black
    ]

    # Higher-contrast ordering (optional)
    rgb_bright = [
        (0/256,   114/256, 178/256),  # blue
        (213/256, 94/256,  0/256),    # red
        (230/256, 159/256, 0/256),    # orange
        (0/256,   158/256, 115/256),  # green
        (178/256, 75/256,  215/256),  # purple
        (0.0,     0.0,     0.0),      # black
        (86/256,  180/256, 233/256),  # light blue
    ]

    if type == 1:
        palette = rgb_rel
    elif type == 2:
        palette = rgb_bright
    else:
        raise ValueError('type must be 1 or 2')

    if n > len(palette):
        raise ValueError(f'Maximum n = {len(palette)} for this palette')

    return palette[:n]


def matrix_3d_to_2d(y):
    """
    Flatten y[i,j,:] row-by-row into y_2d[k,:].

    y shape: (n1, n2, n3)
    output shape: (n1*n2, n3)
    """
    y = np.asarray(y)
    if y.ndim != 3:
        raise ValueError('y must be a 3D array (n1, n2, n3)')

    n1, n2, _ = y.shape
    return y.reshape(n1 * n2, -1)
