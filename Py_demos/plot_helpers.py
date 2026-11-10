"""Plotting helpers shared by the Python demo notebooks."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.ticker import MaxNLocator


def plot_surface_static(
    x_grid,
    y_grid,
    fit,
    se=None,
    *,
    mask=None,
    points=None,
    se_mult=1,
    views=((30, -60), (25, 30)),
    xlabel="x",
    ylabel="y",
    zlabel="effect",
    title=None,
):
    """Static 3D plot of a 2D smooth effect, drawn with matplotlib from several angles.

    This is a static alternative to an interactive plotly surface, e.g. for viewing
    the notebook on GitHub, which doesn't run JavaScript.

    Args:
        x_grid, y_grid: 2D grids of the two covariates (from ``np.meshgrid``).
        fit: Effect at each grid point. Any shape with as many values as the grid,
            e.g. ``gam.partial_effect(..., compute_se=True).fit``.
        se: Standard errors of the effect, same size as ``fit``. If given, the
            surfaces ``fit ± se_mult * se`` are drawn in translucent grey.
        mask: Boolean grid, True where the surface should not be drawn (e.g. grid
            points far from the data, where the smooth extrapolates).
        points: Optional ``(x, y, z)`` of points to draw, e.g. partial residuals.
        se_mult: Multiplier of the standard errors (2 gives an approx. 95% band).
        views: ``(elevation, azimuth)`` pairs, one subplot for each.
        xlabel, ylabel: Axis labels.
        zlabel: Label of the colour bar.
        title: Title of the whole figure.
    """
    shape = np.shape(x_grid)
    hide = np.zeros(shape, dtype=bool) if mask is None else np.asarray(mask)

    def to_grid(values):
        return np.where(hide, np.nan, np.asarray(values, dtype=float).reshape(shape))

    surface = to_grid(fit)
    bands = []
    if se is not None:
        se = to_grid(se)
        bands = [surface + se_mult * se, surface - se_mult * se]
    norm = Normalize(np.nanmin(surface), np.nanmax(surface))

    fig = plt.figure(figsize=(7 * len(views), 6))
    for k, (elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, len(views), k + 1, projection="3d")
        ax.plot_surface(x_grid, y_grid, surface, cmap="viridis", norm=norm,
                        rstride=1, cstride=1, linewidth=0, alpha=0.9)
        for band in bands:
            ax.plot_surface(x_grid, y_grid, band, color="grey", alpha=0.25,
                            rstride=1, cstride=1, linewidth=0)
        if points is not None:
            ax.scatter(*points, s=2, c="black")
        ax.view_init(elev=elev, azim=azim)
        ax.set(xlabel=xlabel, ylabel=ylabel)
        # Fewer ticks; matplotlib 3D axes also put a z label on top of the ticks,
        # so the z values are labelled by the colour bar instead
        for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
            axis.set_major_locator(MaxNLocator(4))
        ax.set_title(f"elevation {elev}°, azimuth {azim}°")
    if title is not None:
        fig.suptitle(title)
    fig.subplots_adjust(wspace=0.1)
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap="viridis"), ax=fig.axes,
                 shrink=0.6, label=zlabel)
    plt.show()
