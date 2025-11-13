# Reaction Rate Field Plot: Reaction System Definition
# Written for CHBE444: Design I, University of Maryland
# (C) Ganesh Sriram, 2025
# Originally written in MATLAB in 2017

# Wishlist
# - Inequality constraints on axis variables to account for mass balances
# - Allow rates to be specified in terms of partial pressures
# - Allow units other than SI or METCBAR

import numpy as np
import matplotlib.pyplot as plt


class ReactionSystem:
    """
    Container for components and reactions in a reactive system.

    Please specify system properties (attributes) as illustrated
    below.

    Components:
        component_ids = ('A', 'B', 'C')
        component_names = {'A': 'n-pentane',
                           'B': '2-methylbutane',
                           'C': '2,2-dimethylpropane'}
    Use component_id for short names (EtOH) or molecular formulas
    Use component_names for full names

    Axes:
        axes = {0: 'A', 1: 'B'}

    Reaction indices:
        reactions = {'r1', 'r2'}

    Stoichiometry
        stoich = {'r1': {'A': -1, 'B': 1},
                  'r2': {'B': -1, 'C': 1}}

    Short-form kinetics
        kinetics = {'r1': lambda C: 3 * x['A'],
                    'r2': lambda C: 2 * x['B']}

    Long-form kinetics
        k1 = 3  # s^-1
        k2 = 2  # s^-1
        def r1(C):
            return k1 * x['A']
        def r2(C):
            return k2 * x['B']
        kinetics = {'r1': r1,
                    'r2': r2}

    Note on kinetics
        x['A'], x['B'], etc., are concentration (or equivalent) variables
        along the axes corresponding to 'A', 'B', etc. In some problems,
        it may be convenient to use moles or partial pressures for x[i].
    """

    def __init__(self, component_ids, component_names, axes, h_lim, v_lim,
                 reactions, stoich, kinetics):
        self.component_ids = tuple(component_ids)
        self.components = tuple(self.component_ids)
        self.component_names = component_names
        self.names = self.component_names
        self.axes = axes
        self.h_lim = h_lim
        self.v_lim = v_lim
        self.reactions = reactions
        self.stoich = stoich
        self.kinetics = kinetics

    def __repr__(self):
        rows_stoich = '\n'.join(f'        {rxn}: {s}'
                                for rxn, s in self.stoich.items())
        rows_kinetics = '\n'.join(f'        {rxn}: {k}'
                                  for rxn, k in self.kinetics.items())
        disp_text = (f'Reaction system:\n'
                     f'    component ids:\n\t{self.components}\n'
                     f'    component names:\n\t{self.component_names}\n'
                     f'    axes:\n\t{self.axes}\n'
                     f'    horizontal axis limits:\n\t{self.h_lim}\n'
                     f'    vertical axis limits:\n\t{self.v_lim}\n'
                     f'    reactions:\n\t{sorted(self.reactions)}\n'
                     f'    stoichiometry:\n{rows_stoich}\n'
                     f'    kinetics:\n{rows_kinetics}\n')
        return disp_text

    def rate(self, x):
        """ Reaction rate as a function of concentration vector x."""

        X = {'A': 0, 'B': 0}  # X is the concentration vector (or equivalent)
        r_rxn = dict.fromkeys(self.reactions, 0)
        r_comp = dict.fromkeys(self.axes, 0)

        for i in self.components:
            if i in self.axes:
                X[i] = x[self.axes[i]]

        for j in self.reactions:
            r_rxn[j] += self.kinetics[j](X)

        for i in self.components:
            if i in self.axes:
                for j in self.reactions:
                    if i in self.stoich[j]:
                        r_comp[i] += self.stoich[j][i] * r_rxn[j]

        r_comp = np.array(list(r_comp.values()))
        return r_comp

    def plot_rate_field(
        self,
        n_vec=51, n_vec_h=None, n_vec_v=None,
        arrow_scale=None, arrow_scale_h=None, arrow_scale_v=None,
        fsize=12, font=12
        ):

        """
        Plot rate field in concentration space.

        Example usage:
            system.draw_rate_field(
                n_vec_h=51, n_vec_v=51,
                fsize=12, font=12)

            n_vec: number of rate vectors along any dimension, defaults to 51
            n_vec_h: number of rate vectors along horizontal dimension (x-axis)
                     defaults to 51, can also be set by n_vec
            n_vec_v: number of rate vectors along vertical dimension (x-axis)
                     defaults to 51, can also be set by n_vec
            arrow_scale: scale of arrow along any dimension, defaults to n_vec
            arrow_scale_h: scale of arrow along horizontal dimension,
                           defaults to n_vec_x
            arrow_scale_v: scale of arrow along vertical dimension,
                           defaults to n_vec_y
            fsize: figure size, defaults to 12
            font: main font used for axis label, etc., defaults to 12
            h_lim, v_lim: horizontal and vertical axis limits,
            default to [0, 1]
        """

        fig, ax = plt.subplots(figsize=(fsize, fsize), facecolor='white')
        h_lim = self.h_lim
        v_lim = self.v_lim
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1)
        ax.set_xlim(h_lim)
        ax.set_ylim(v_lim)
        ax.grid(True)

        for i in self.components:
            if i in self.axes:
                if self.axes[i] == 0:
                    ax.set_xlabel(self.names[i], fontsize=font)
                if self.axes[i] == 1:
                    ax.set_ylabel(self.names[i], fontsize=font)

        if n_vec_h is None:
            n_vec_h = n_vec
            arrow_scale_h = n_vec_h
        if n_vec_v is None:
            n_vec_v = n_vec
            arrow_scale_v = n_vec_v

        if arrow_scale is None:
            arrow_scale = n_vec
        else:
            if arrow_scale_h is None:
                arrow_scale_h = arrow_scale
            if arrow_scale_v is None:
                arrow_scale_v = arrow_scale

        X = np.linspace(h_lim[0], h_lim[1], n_vec_h)
        Y = np.linspace(v_lim[0], v_lim[1], n_vec_v)

        xx, yy = np.meshgrid(X, Y)
        uu, vv = np.meshgrid(X, Y)

        for i in range(np.size(xx, 0)):
            for j in range(np.size(yy, 1)):
                uu[i, j], vv[i, j] = self.rate([xx[i, j], yy[i, j]])

        mag = np.hypot(uu, vv)
        un, vn = uu, vv
        with np.errstate(invalid='ignore'):
            un = np.where(np.isnan(un), np.nan,
                          np.where(mag > 0,
                                   np.divide(uu, mag), 0))
            vn = np.where(np.isnan(vn), np.nan,
                          np.where(mag > 0,
                                   np.divide(vv, mag), 0))
        ax.quiver(X, X, un, vn, color='#888888',
                  scale=arrow_scale,
                  alpha=0.4)
        return fig, ax, plt

    draw_rate_field = plot_rate_field


System = ReactiveSystem = ReactionSystem
