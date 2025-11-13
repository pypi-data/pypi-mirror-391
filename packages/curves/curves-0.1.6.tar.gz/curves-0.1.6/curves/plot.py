# -*- coding: utf-8 -*-

# curves
# ------
# functional curve algebra (created by auxilium)
#
# Author:   sonntagsgesicht
# Version:  0.1.4, copyright Friday, 11 October 2024
# Website:  https://github.com/sonntagsgesicht/curves
# License:  Apache License 2.0 (see LICENSE file)


from warnings import warn

try:
    from matplotlib import use, pyplot as plt
except ImportError:
    warn("using plotter to plot curves requires 'matplotlib' "
         "consider 'pip install matplotlib'")


def lin(start: int | float | slice | list | tuple = 1.0,
        stop:  int | float | None = None,
        step:  int | float | None = None,
        num: int = 1_000):
    """generate grid of values

    :param start: (float, slice, list or tuple) first grid point (included)
    :param stop: (float) last grid point (excluded)
    :param step: (float) step size between points (optional)
    :param num: (int) number of grid points if **step** is None
        (optional: default is 1_000)
    :return: list of grid points as float

    **stop** and **step** are ignored if **start** is slice or tuple
    since their values are taken from **start** entries.

    >>> from curves import lin

    >>> lin(1.0, step=0.25)
    [0.0, 0.25, 0.5, 0.75]

    >>> lin(1.1, step=0.25)
    [0.0, 0.25, 0.5, 0.75, 1.0]

    >>> lin(0.25, 1.0, step=0.5)
    [0.25, 0.75]

    >>> lin([0.25, 1.0, 0.5])
    [0.25, 0.75]

    >>> lin(slice(0.25, 1.0, 0.5))
    [0.25, 0.75]

    >>> lin(0.25, 1.0, num=3)
    [0.25, 0.5, 0.75]

    """
    if isinstance(start, slice):
        start, stop, step = start.start, start.stop, start.step
    if isinstance(start, (list, tuple)):
        if len(start) == 2:
            start, stop = start
        else:
            start, stop, step = start
    if stop is None:
        if start < 0:
            stop = 0.0
        else:
            start, stop = 0.0, start
    if step is None:
        step = (stop - start) / num
    if start + step < start < stop or stop < start < start + step:
        raise ValueError()
    r = [start]
    while r[-1] + step < stop:
        r.append(r[-1] + step)
    return r


def plot(x, *curve, legend=True, kind='plot', params=None,
         xlim=(), ylim=(), aspect=False, ax=None,
         figsize=None, show=True, **curves):
    """plot curves with 'matplotlib'

    :param x: (int, float, list, tuple or slice)
        if **x** is either **int**, **float** or **slice**
        |lin()| is invoked to generate **x** values.
    :param curve: (callable) function to be plotted
        with labels given by str representation
    :param legend: (bool) if **True** the legend is shown
        (optional: default is **True**)
    :param kind: (str) kind of plot type, e.g. 'dots', 'bars'
        (optional: default is **'plot'**)
    :param params: (dict) additional parameters to define curve display style
        (optional: no default)
    :param xlim: (tuple[float, float])
        (optional: no default)
    :param ylim: (tuple[float, float])
        (optional: no default)
    :param aspect: (float) defines box aspect ratio
        (optional: default is **None**)
    :param ax: (ax or None)
        (optional: default is current ax)
    :param figsize: (tuple[float, float] or None) if given,
        a figure with given **figsize** is created.
        (optional: no default)
    :param show: (bool)
        (optional: default is **True**)
    :param curves: (callable) function to be plotted
        with labels given by key values
    :return: ax

    >>> from math import sqrt, pi
    >>> from curves import X, plot, lin
    >>> from curves.functions import sin, cos, exp

    set *x* values

    >>> x = lin(-5, 5, num=500)  # x values from -1 to 1

    define the function

    >>> std_norm_pdf = 1 / sqrt(2 * pi) * exp(-(X ** 2) / 2)

    and plot it

    >>> plot(x, phi=std_norm_pdf)  # doctest: +SKIP

    as simple as

    >>> plot(x, sin, -sin, cos, -cos)  # doctest: +SKIP


    """
    if figsize:
        plt.figure(figsize=figsize)
    ax = _plot(x, *curve, kind=kind, params=params, ax=ax, **curves)
    if aspect:
        ax.set_box_aspect(aspect)

    ax.set_title('curve plot')
    ax.set_xlabel(r'time $t$')
    ax.set_ylabel(r'$x(t)$')

    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if legend:
        ax.legend()
    if show:
        plt.show()
    else:
        return ax


def _plot(x, *curve, kind='plot', params=None, ax=None, **curves):
    ax = ax or plt.gca()
    plot = getattr(ax, kind)
    if isinstance(x, (int, float, slice)):
        x = lin(x)
    x = tuple(x)
    params = params or {}
    for c in curve:
        y = [c(_) for _ in x] if callable(c) else c
        label = getattr(c, '__latex__', str(c))
        if 50 < len(label):
            label = label[:50] + ' ...'
        plot(x, y, label=label, **params)
    for k in curves:
        c = curves[k]
        y = [c(_) for _ in x] if callable(c) else c
        label = getattr(k, '__latex__', str(k))
        if 50 < len(label):
            label = label[:50] + ' ...'
        plot(x, y, label=label, **params)
    return ax


class Plotter:

    def __init__(self, x, legend=True, kind='plot',
                 params=None, xlim=(), ylim=(), aspect=False,
                 backend=None, figsize=(10, 5), show=True):
        """

        :param x:
        :param legend:
        :param kind:
        :param params:
        :param xlim:
        :param ylim:
        :param aspect:
        :param backend:
        :param figsize:
        :param show:

        """
        self.x = lin(x) if isinstance(x, (int, float, slice)) else x
        self._ax = {'legend': legend, 'kind': kind, 'params': params,
                    'xlim': xlim, 'ylim': ylim, 'aspect': aspect}
        self.figsize = figsize
        self.show = show
        if backend:
            # WebAgg, TkAgg, QtCairo, QtAgg, module://backend_interagg, MacOSX
            use(backend)

    def __call__(self, *curve, legend=None, kind=None, params=None,
                 xlim=(), ylim=(), aspect=None, **curves):
        plt.gcf().set_size_inches(*self.figsize)
        ax = plot(self.x, *curve,
                  legend=legend or self._ax['legend'],
                  kind=kind or self._ax['kind'],
                  params=params or self._ax['params'],
                  xlim=xlim or self._ax['xlim'],
                  ylim=ylim or self._ax['ylim'],
                  aspect=self._ax['aspect'] if aspect is None else aspect,
                  show=self.show,
                  **curves)
        return ax

    def __getitem__(self, item):
        return Plotter(item, figsize=self.figsize, show=self.show, **self._ax)


plotter = Plotter(25)
"""plotter instance"""
