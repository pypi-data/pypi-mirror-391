# (C) Ganesh Sriram, 2025, gsriram@umd.edu
# Licensed under GNU Public License 3.0
# Originally written in MATLAB in 2018

# Wishlist
# - improve distillation design optimization
# - determine optimal feed tray
# - improve distillation block diagram and variable names in its function


class system:
    # Define a class 'system' to describe a ternary system
    
    def __init__(self, components, Antoine, Wilson_a, Wilson_b):

        self.components = components
        self.Antoine = Antoine
        self.Wilson_a = Wilson_a
        self.Wilson_b = Wilson_b

    # components: components in ternary mixture
    # Antoine: Antoine equation constants from NIST WebBook in NIST format
    # Wilson_a: a_ij parameters for Wilson activity coefficient correlation
    # Wilson_b: b_ij parameters for Wilson activity coefficient correlation
    # + diagonal elements a_ii and b_ii are always zero
    # + for an ideal liquid mixture, set all a_ij, b_ij to zero
    # + for non-ideal mixtures, obtain from literature or Aspen
    # + To get them from Aspen, create an Aspen file (apwz or apw) file
    #   containing the 3 compounds in the mixture
    # + Go to Methods on the left menu pane and select WILSON as the
    #   method with default settings
    # + Then navigate to Methods ≫ Parameters ≫ Binary Interaction ≫ Wilson
    # + Read the parameters a_ij and b_ij from the displayed table

    def __repr__(self):
        rows_Ant = '\n'.join(f'          {comp}: {row}' 
                           for comp, row in self.Antoine.items())
        rows_a = '\n'.join(f'        {comp}: {row}' 
                           for comp, row in self.Wilson_a.items())
        rows_b = '\n'.join(f'        {comp}: {row}' 
                           for comp, row in self.Wilson_b.items())
        disp_text = (f'System:\n'
                     f'    components: {self.components}\n'
                     f'    Antoine:\n{rows_Ant}\n'
                     f'    Wilson_b:\n{rows_a}\n'
                     f'    Wilson_b:\n{rows_b}\n')
        return disp_text


def make_system(components, Antoine, Wilson_a, Wilson_b):
    name = system(components=components,
                  Antoine=Antoine,
                  Wilson_a=Wilson_a,
                  Wilson_b=Wilson_b)
    return name


class properties:
    # Define a class 'properties' to describe a ternary mixture 
    # with a specific composition

    def __init__(self, P, molefrac, yeq, xeq, T_bubl, T_dew):
        self.P = P
        self.molefrac = molefrac
        self.yeq = yeq
        self.xeq = xeq
        self.T_bubl = T_bubl
        self.T_dew = T_dew

    def __repr__(self):
        x = self.molefrac
        disp_text = (f'Mixture VLE properties:\n'
                     f'    Pressure (P, bar): {self.P}\n'
                     f'    Overall composition (x): {x}\n'
                     f'    If this mixture were a saturated liquid:\n'
                     f'        Vapor in equilibrium (yeq): {self.yeq}\n'
                     f'        Bubble T (T_bubl, °C): {self.T_bubl}\n'
                     f'    If this mixture were a saturated vapor:\n'
                     f'        Liquid in equilibrium (xeq): {self.xeq}\n'
                     f'        Dew T (T_dew, °C): {self.T_dew} °C\n'
                     f'    Compositions are reported as mole fractions\n')
        return disp_text


class flash_res:
    # Define a class 'flash_res' to describe the results of a 
    # flash calculation

    def __init__(self, xF, x, y, T, P, Lfrac, Vfrac):
        self.xF = xF
        self.x = x
        self.y = y
        self.P = P
        self.T = T
        self.Lfrac = Lfrac
        self.Vfrac = Vfrac
        
    def __repr__(self):
        disp_text = (f'Flash results:\n'
                     f'    Feed: {self.xF}\n'
                     f'    Liquid product (x): {self.x}\n'
                     f'    Vapor product (y): {self.y}\n'
                     f'    Temperature (T, °C): {self.T}\n'
                     f'    Pressure (P, bar): {self.P}\n'
                     f'    Liquid fraction (Lfrac): {self.Lfrac}\n'
                     f'    Vapor fraction (Vfrac): {self.Vfrac}\n'
                     f'    Compositions are reported as mole fractions\n')
        return disp_text


class distill_res:
    # Define a class 'distill_res' to describe the results of a 
    # distillation calculation

    def __init__(self, xF, xD, xB, D, B, q, r, s, 
                 nstg, fstg, xLr, yVr, Tr, xLs, yVs, Ts, P):
        self.xF = xF
        self.xD = xD
        self.xB = xB
        self.D = D
        self.B = B
        self.q = q
        self.r = r
        self.s = s
        self.nstg = nstg
        self.fstg = fstg
        self.xLr = xLr
        self.yVr = yVr
        self.Tr = Tr
        self.xLs = xLs
        self.yVs = yVs
        self.Ts = Ts
        self.P = P
        
    def __repr__(self):
        stage_text_r = "Stagewise results (R-section):\n"
        stage_text_r += '         #'
        stage_text_r += '        xL (liq)                '
        stage_text_r += '        yV (vap)                '
        stage_text_r += '         T (°C)\n'
        
        for i in range(len(self.Tr)):
            xLr_row = '  '.join(f'{val:8.4f}' for val in self.xLr[i])
            yVr_row = '  '.join(f'{val:8.4f}' for val in self.yVr[i])
            stage_text_r += f'      {i+1:4d}      {xLr_row}    {yVr_row}    {self.Tr[i, 0]:8.2f}\n'
        
        stage_text_s = "Stagewise results (S-section):\n"
        stage_text_s += '         #'
        stage_text_s += '        xL (liq)                '
        stage_text_s += '        yV (vap)                '
        stage_text_s += '         T (°C)\n'

        for i in range(len(self.Ts)):
            xLs_row = '  '.join(f'{val:8.4f}' for val in self.xLs[i])
            yVs_row = '  '.join(f'{val:8.4f}' for val in self.yVs[i])
            stage_text_s += f'      {i+1:4d}      {xLs_row}    {yVs_row}    {self.Ts[i, 0]:8.2f}\n'

        
        disp_text = (f'Distillation parameters:\n'
                     f'    Feed: {self.xF}\n'
                     f'    Distillate composition (xD): {self.xD}\n'
                     f'    Bottoms composition (xB): {self.xB}\n'
                     f'    Distillate flow rate (D): {self.D}\n'
                     f'    Bottoms flow rate (B): {self.B}\n'
                     f'    Feed quality (q): {self.q}\n'
                     f'    Reflux ratio (r): {self.r}\n'
                     f'    Boilup ratio (s): {self.s}\n'
                     f'    Number of stages (nstg): {self.nstg}\n'
                     f'    Feed stage (fstg): {self.fstg}\n'
                     f'    Pressure (P, bar): {self.P}\n'
                     f'{stage_text_r}'
                     f'{stage_text_s}'
                     f'Compositions are reported as mole fractions\n'
                     f'Flows are molar relative to the feed\n')
        return disp_text


def vle_calc(system, axes, P=1.013,
             fsize=8, n_vectors=31, arrow_scale=31, xy_tol=-1e-6,
             Tmin=None, Tmax=None,
             contour_T_heavy=10, contour_T_medium=5, contour_T_light=1,
             plot_residue=False, residue_feeds=None, 
             integration_time=10, show_feeds=False):

    # Plot equilibrium vectors, constant-temperature contours and residue
    # curves for ternary vapor-liquid mixtures in [x_A,x_B] or [y_A,y_B] space
    # Perform flash and distillation calclations
    # A homogeneous non-ideal liquids phase is described by the Wilson
    # activity coefficient model; the vapor phase is assumed ideal
    # Vapor pressures are described by the Antoine equation in NIST format
    # (log10, bar, K)

    import numpy as np
    import scipy as sci
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from collections import namedtuple
    import pickle
    import warnings
    
    # System properties

    components = system.components
    Antoine = system.Antoine
    Wilson_a = system.Wilson_a
    Wilson_b = system.Wilson_b

    assert axes is not None, 'Axes need to be specified'

    ax0 = False
    for j in components:  # check whether axis 0 is specified
        if j in axes:
            if axes[j] == 0:
                ax0 = True

    assert ax0, 'Axis 0 needs to be specified'

    ax1 = False
    for j in components:  # check whether axis 1 is specified
        if j in axes:
            if axes[j] == 1:
                ax1 = True

    assert ax1, 'Axis 1 needs to be specified'

    for j in components:  # identify implicit component if not specified
        if j not in axes:
            axes[j] = 2

    # Constants and functions

    T0 = 273.15  # 0 °C in K

    def Psat(T):  # vapor pressure (bar) as a function of T (°C)
        Psat = np.zeros(3)
        for j in components:
            assert 'A' in Antoine[j], \
                f'Antoine parameter A is missing for {j}'
            assert 'B' in Antoine[j], \
                f'Antoine parameter B is missing for {j}'
            assert 'C' in Antoine[j], \
                f'Antoine parameter C is missing for {j}'

            A = Antoine[j]['A']
            B = Antoine[j]['B']
            C = Antoine[j]['C']

            Ps = 10 ** (A - B / (T + T0 + C))
            Psat[axes[j]] = Ps
        return Psat

    if Tmin is None:  # minimum boiling point amongst the 3 components
        Tmin = np.inf
        for jj in range(3):
            res = sci.optimize.root_scalar(lambda T: (Psat(T) - P)[jj], x0=0)
            if res.root < Tmin:
                Tmin = res.root

    if Tmax is None:  # maximum boiling point amongst the 3 components
        Tmax = -T0
        for jj in range(3):
            res = sci.optimize.root_scalar(lambda T: (Psat(T) - P)[jj], x0=0)
            if res.root > Tmax:
                Tmax = res.root

    Tr = (Tmin + Tmax) / 2  # representative temperature of the system

    def gamma(x, T):
        # Wilson activity coefficient as a function of x and T (°C)

        A = np.zeros([3, 3])
        for i in components:
            for j in components:
                A[axes[i]][axes[j]] = np.exp(Wilson_a[i][j] +
                                             Wilson_b[i][j] /
                                             (T + T0))
        lng = 1 - np.log(A @ x) - np.transpose(A) @ (x / (A @ x))
        g = np.exp(lng)
        return g

    def delxt(t, x):
        # derivative of x with respect to t, expressed as f(t, x)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', RuntimeWarning)
            res = sci.optimize.root_scalar(lambda T: 1 - np.sum(x *
                                                                gamma(x, T) *
                                                                Psat(T) / P),
                                           x0=Tr)
        T = res.root
        g = gamma(x, T)
        Ps = Psat(T)
        delx = x - x * g * Ps / P
        return delx

    def delx(x):
        # derivative of x with respect to t, expressed as f(x)

        res = sci.optimize.root_scalar(lambda T: 1 - np.sum(x *
                                                            gamma(x, T) *
                                                            Psat(T) / P),
                                       x0=Tr)
        T = res.root
        g = gamma(x, T)
        Ps = Psat(T)
        delx = x - x * g * Ps / P
        return delx, T

    def yeq(x):
        dx, T = delx(x)
        y = x - dx
        return y, T

    def xeq(y):
        Y = np.append(y, Tr)
        res = sci.optimize.root(lambda X: np.append(Y[0:3] * P - X[0:3] *
                                                    gamma(X[0:3], X[3]) *
                                                    Psat(X[3]),
                                                    np.sum(X[0:3]) - 1),
                                x0=Y)
        x = res.x[0:3]
        T = res.x[3]
        return x, T

    # Initialize figure

    fig, ax = plt.subplots(figsize=(fsize, fsize), facecolor='white')
    ax.set_aspect('equal', adjustable='box')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    font = 12
    for j in components:
        if axes[j] == 0:
            ax.set_xlabel(j, fontsize=font)
        if axes[j] == 1:
            ax.set_ylabel(j, fontsize=font)
    ax.grid(True)

    # Calculate and plot equilibrium field

    X = np.linspace(0, 1, n_vectors)
    xx, yy = np.meshgrid(X, X)
    xx = np.where(1 - xx - yy < xy_tol, np.nan, xx)
    yy = np.where(1 - xx - yy < xy_tol, np.nan, yy)

    uu, vv = np.meshgrid(X, X)
    uu = np.where(1 - uu - vv < xy_tol, np.nan, uu)
    vv = np.where(1 - uu - vv < xy_tol, np.nan, vv)

    for i in range(np.size(xx, 0)):
        for j in range(np.size(yy, 1)):
            if ~np.isnan(xx[i, j]) and ~np.isnan(yy[i, j]):
                uv, _ = delx([xx[i, j], yy[i, j], 1 - xx[i, j] - yy[i, j]])
                uu[i, j], vv[i, j] = uv[0], uv[1]

    mag = np.hypot(uu, vv)

    un, vn = uu, vv

    with np.errstate(invalid='ignore'):
        un = np.where(np.isnan(un), np.nan, np.where(mag > 0,
                                                     np.divide(uu, mag), 0))
        vn = np.where(np.isnan(vn), np.nan, np.where(mag > 0,
                                                     np.divide(vv, mag), 0))

    ax.quiver(X, X, un, vn, color='#8888ff', scale=arrow_scale, alpha=0.4)

    # Plot residue curve if requested

    if plot_residue:
        xF = np.zeros(3)  # initialize feed vector
        assert residue_feeds is not None, \
            'Feed point(s) must be specified if residue curve is requested'

        row_sums = {i: sum(d.values()) for i, d in residue_feeds.items()}
        for i, total in row_sums.items():
            assert abs(total - 1) < 1e-8, (
                'Residue curve feed mole fractions must add up to 1\n' +
                f'Row {i} does not sum to 1 (got {total})')
        
        for i in residue_feeds:
            for j in residue_feeds[i]:
                xF[axes[j]] = residue_feeds[i][j]
            if show_feeds:
                ax.plot(xF[0], xF[1], 'ko', markersize=6)
            with np.errstate(all='ignore'):
                int_t = integration_time
                res = sci.integrate.solve_ivp(delxt, [0, int_t], xF,
                                              t_eval=np.linspace(0, int_t, 100))
                ax.plot(res.y[0, :], res.y[1, :], 'k-')
                res = sci.integrate.solve_ivp(delxt, [0, -int_t], xF,
                                              t_eval=np.linspace(0, -int_t, 100))
                ax.plot(res.y[0, :], res.y[1, :], 'k-')

    # Calculate and plot temperature contours

    x_contours = 51  # spacing of x for contour plotting
    XT = np.linspace(0, 1, x_contours)
    X0, X1 = np.meshgrid(XT, XT)
    Y0, Y1 = np.meshgrid(XT, XT)
    TT0, TT1 = np.meshgrid(XT, XT)

    for i in range(np.size(XT)):
        for j in range(np.size(XT)):
            if XT[i] + XT[j] <= 1:
                x = [XT[i], XT[j], 1 - XT[i] - XT[j]]
                res = sci.optimize.root_scalar(lambda T:
                                               1 - np.sum(x * gamma(x, T) *
                                                          Psat(T) / P),
                                               x0=Tr)
                T = res.root

                X0[i, j] = XT[i]
                X1[i, j] = XT[j]
                TT0[i, j] = T

                y = x * gamma(x, T) * Psat(T) / P
                Y0[i, j] = y[0]
                Y1[i, j] = y[1]
                TT1[i, j] = T
            else:
                TT0[i, j] = np.nan
                TT1[i, j] = np.nan

    def clevels(c):  # contour levels
        tmin = np.round(Tmin / c) * c
        tmax = np.round(Tmax / c + 1) * c
        clevels = np.arange(tmin, tmax, c)
        return clevels

    cl = ax.contour(X0, X1, TT0,
                    levels=clevels(contour_T_heavy),
                    linewidths=0.5, colors='#0000ff')
    ax.clabel(cl, inline=True, fontsize=8)
    ax.contour(X0, X1, TT0,
               levels=clevels(contour_T_medium),
               linewidths=0.25, colors='#0000ff')
    ax.contour(X0, X1, TT0,
               levels=clevels(contour_T_light),
               linewidths=0.05, colors='#0000ff')

    cl = ax.contour(Y0, Y1, TT1,
                    levels=clevels(contour_T_heavy),
                    linewidths=0.5, colors='#ff0000')
    ax.clabel(cl, inline=True, fontsize=8)
    ax.contour(Y0, Y1, TT1,
               levels=clevels(contour_T_medium),
               linewidths=0.25, colors='#ff0000')
    ax.contour(Y0, Y1, TT1,
               levels=clevels(contour_T_light),
               linewidths=0.05, colors='#ff0000')

    # Wrap up, save and display plot

    ax.plot([0, 1], [0, 0], 'k-')  # right triangle, horizontal line
    ax.plot([0, 0], [0, 1], 'k-')  # right triangle, vertical line
    ax.plot([0, 1], [1, 0], 'k-')  # right triangle, diagonal line

    plt.draw()

    def mix_props(x):
        ye, Tb = yeq(x)
        xe, Td = xeq(x)
        p = properties(P=P,
                       molefrac=x,
                       yeq=ye,
                       xeq=xe,
                       T_bubl=Tb,
                       T_dew=Td)
        return p

    def atanm(x):
        # Modified arctan function, returns a result in the range (0, {pi})
        res = np.atan(x)
        if res < 0:
            res = res + np.pi
        return res

    def angle_dx(x):
        dx, T = delx(x)
        if abs(dx[0]) <= 1e-6:
            angle = np.pi / 2
        else:
            slope = dx[1] / dx[0]
            angle = atanm(slope)
        return angle

    def angle_xy(x, y):
        if np.abs(x[0] - y[0]) <= 1e-6:
            angle = np.pi / 2
        else:
            slope = (x[1] - y[1]) / (x[0] - y[0])
            angle = atanm(slope)
        return angle

    def flashT_obj(x, xF, T):
        z = ((angle_dx(x) - angle_xy(x, xF)) ** 2 +         
             (yeq(x)[1] - T) ** 2 +
             (xeq(yeq(x)[0])[1] - T) ** 2)
        return z
   
    def flashT(xF, T):
        eq_cons = {'type': 'eq',
               'fun' : lambda x: np.sum(x) - 1}
    
        bounds = sci.optimize.Bounds([0, 0, 0], [1, 1, 1])
        
        res = sci.optimize.minimize(lambda x: flashT_obj(x, xF, T),
                                    x0=xF,
                                    method='SLSQP',
                                    constraints=[eq_cons],
                                    bounds=bounds,
                                    tol=1e-9)
        
        x = res.x
        y = yeq(x)[0]
        T = yeq(x)[1]
        Vfrac = np.linalg.norm(x - xF) / np.linalg.norm(x - y)
        
        res = flash_res(xF=xF,
                        x=x,
                        y=y,
                        T=T,
                        P=P,
                        Lfrac=1 - Vfrac,
                        Vfrac=Vfrac)
        return res

    def flashVfrac_obj(x, xF, Vfrac):
        x = np.array(x)
        Tx = mix_props(x).T_bubl
        xF = np.array(xF)
        y, Ty = yeq(x)
        
        z = ((angle_dx(x) - angle_xy(x, xF)) ** 2 +         
             (np.linalg.norm(x - xF) / np.linalg.norm(x - y) - Vfrac) ** 2 +
             (Tx - Ty) ** 2)
        return z
        
    def flashVfrac(xF, Vfrac):
        eq_cons = {'type': 'eq',
               'fun' : lambda x: np.sum(x) - 1}
    
        bounds = sci.optimize.Bounds([0, 0, 0], [1, 1, 1])
        
        res = sci.optimize.minimize(lambda x: flashVfrac_obj(x, xF, Vfrac),
                                    x0=xF,
                                    method='SLSQP',
                                    constraints=[eq_cons],
                                    bounds=bounds,
                                    tol=1e-9)

        x = res.x
        y = yeq(x)[0]
        T = yeq(x)[1]
        Vfrac = np.linalg.norm(x - xF) / np.linalg.norm(x - y)
        
        res = flash_res(xF=xF,
                        x=x,
                        y=y,
                        T=T,
                        P=P,
                        Lfrac=1 - Vfrac,
                        Vfrac=Vfrac)
        return res
    
    def flash_bfd(flash_res):
        # Draw a BFD of a flash evaporator

        res = flash_res

        P_str = np.round(res.P, 2)
        T_str = np.round(res.T, 2)
        xF_str = np.round(res.xF, 2)

        if res.x is None:
            x_str = '?'
        else:
            x_str = np.round(res.x, 2)

        if res.y is None:
            y_str = '?'
        else:
            y_str = np.round(res.y, 2)

        if res.Lfrac is None:
            Lfrac_str = '?'
        else:
            Lfrac_str = np.round(res.Lfrac, 2)

        if res.Vfrac is None:
            Vfrac_str = '?'
        else:
            Vfrac_str = np.round(res.Vfrac, 2)

        fig1, ax1 = plt.subplots()
        plt.axis('off')
        _ = ax1.set_xlim(-4, 4)
        _ = ax1.set_ylim(-4, 4)

        patches.ArrowStyle.Curve

        feed = patches.Arrow(-3, 0, 2, 0, width=0.5, color='black')
        ax1.add_patch(feed)

        ax1.text(-1.1, 0.2,
                f'xF = {xF_str}',
                horizontalalignment='right',
                verticalalignment='bottom',
                fontsize=8,
                color='black')

        vap = patches.Arrow(1, 1.6, 2, 0, width=0.5, color='red')
        ax1.add_patch(vap)

        ax1.text(1.1, 1.8,
            f'y = {y_str}',
            horizontalalignment='left',
            verticalalignment='bottom',
            fontsize=8,
            color='red')

        liq = patches.Arrow(1, -1.6, 2, 0, width=0.5, color='blue')
        ax1.add_patch(liq)

        ax1.text(1.1, -1.4,
            f'x = {x_str}',
            horizontalalignment='left',
            verticalalignment='bottom',
            fontsize=8,
            color='blue')

        unit = patches.Rectangle((-1, -2), 2, 4,
                                 linewidth=2,
                                 edgecolor='black',
                                 facecolor='white',
                                 alpha=1)
        ax1.add_patch(unit)

        ax1.text(0, 0.5, 'Flash',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=10)

        ax1.text(0, 0, f'P = {P_str} bar',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=8)

        ax1.text(0, -0.5, f'T = {T_str} °C',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=8)

        ax1.text(2, 0, f'Vfrac = {Vfrac_str}',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=8)

        return fig1, ax1

    def distill(xF, D=None, xD=None, B=None, xB=None,
                r=None, s=None, q=None,
                nstg=None, fstg=None,
                mode=None, calc_begin=None,
                plot_distill=True):

        # nstg and fstg are 1-based (provided by user)
        # Nstg and Fstg are 0-based (used in this function)

        if nstg is not None:
            Nstg = nstg - 1
        if fstg is not None:
            Fstg = fstg - 1
        
        if mode in ('minstages', 'minreflux'):
            assert xD is not None or xB is not None, (
                "Either xD or xB must be specified " +
                "if mode is 'minstages' or 'minreflux'")

            if xD is not None:
                assert D is not None, (
                    'If xD is specified, D must be specified')

            if xB is not None:
                assert B is not None, (
                    'If xB is specified, B must be specified')

            if xD is None:
                D = 1 - B
                xD = (xF - B * np.array(xB)) / D
            elif xB is None:
                B = 1 - D
                xB = (xF - D * np.array(xD)) / B

            xD = np.array(xD)
            xB = np.array(xB)

            s = (
                q - 1 
                + (q + r) * np.linalg.norm(xF - xB)
                  / np.linalg.norm(xD - xF)
            )
            
        xF = np.array(xF)

        assert mode in (None, 'minstages', 'minreflux'), (
            f"mode must be set to None (default calculation), "
            f"'minstages' or 'minreflux' (got {mode})")

        count_qrs = sum(x is not None for x in (q, r, s))

        if mode in (None, 'minreflux'):
            assert count_qrs >= 2, (
                'feed quality (q) and reflux ratio (r) must be specified')

        if mode is None:
            assert nstg is not None, (
                'Number of stages (nstg) must be specified')
            assert fstg is not None, (
                'Feed stage (fstg) must be specified')    
            stages_r = np.arange(0, Fstg)
            stages_s = np.arange(Nstg, Fstg, -1)
        elif mode == 'minstages':
            r = 1e+6                      
            assert nstg is not None, (
                'Number of stages (nstg) must be specified')  
            if calc_begin is None:
                calc_begin = 'distillate'
            assert calc_begin in ('distillate', 'bottoms'), (
                f"For 'minstages' mode, calc_begin must either be " +
                f"'distillate' or 'bottoms' (got {calc_begin})")
            if calc_begin == 'distillate':
                stages_r = np.arange(0, Nstg)
            elif calc_begin == 'bottoms':
                stages_s = np.arange(Nstg, 0, -1)
        elif mode == 'minreflux':
            nstg = 200
            Nstg = nstg - 1
            stages_r = np.arange(0, Nstg - 1)
            stages_s = np.arange(Nstg, 1, -1)

        xLr = np.full((nstg, 3), np.nan)
        yVr = np.full((nstg, 3), np.nan)
        Tr = np.full((nstg, 1), np.nan)
        
        xLs = np.full((nstg, 3), np.nan)
        yVs = np.full((nstg, 3), np.nan)
        Ts = np.full((nstg, 1), np.nan)

        if mode in ('minstages', 'minreflux'):
            # Rectifying section profile
            
            xLr[0, :] = xD
            yVr[0, :] = yeq(xD)[0]
            Tr[0] = yeq(xD)[1]
            
            if ((mode in (None, 'minreflux')) or
                (mode == 'minstages' and calc_begin == 'distillate')):        
                for j in stages_r:
                    yVr[j + 1, :] = r / (r + 1) * xLr[j, :] + 1 / (r + 1) * np.array(xD)
                    xLr[j + 1, :] = xeq(yVr[j + 1, :])[0]
                    Tr[j + 1] = xeq(yVr[j + 1, :])[1]
                
            # Stripping section profile
            
            xLs[nstg-1, :] = xB
            yVs[nstg-1, :] = yeq(xB)[0]
            Ts[nstg-1] = yeq(xB)[1]
    
            if ((mode in (None, 'minreflux')) or 
                (mode == 'minstages' and calc_begin == 'bottoms')):     
                for j in stages_s:
                    xLs[j - 1, :] = s / (s + 1) * yVs[j, :] + 1 / (s + 1) * np.array(xB)
                    yVs[j - 1, :] = yeq(xLs[j - 1, :])[0]
                    Ts[j - 1] = yeq(xLs[j - 1, :])[1]
        else:
            def distill_obj(xD):
                # D is input by user, xD is the optimization variable

                B = 1 - D
                xB = (xF - D * np.array(xD)) / B

                assert 0 <= q <= 1, 'Provide q in the range (0, 1)'

                s = (
                    q - 1 
                    + (q + r) * np.linalg.norm(xF - xB)
                      / np.linalg.norm(xD - xF)
                )
                
                res = vle3.flashVfrac(xF, q)
                xF_obj = res.x
                yF_obj = res.y

                obj = 0

                # Rectifying section profile
            
                xLr[0, :] = xD
                yVr[0, :] = yeq(xD)[0]
                Tr[0] = yeq(xD)[1]
                
                for j in stages_r:
                    yVr[j + 1, :] = r / (r + 1) * xLr[j, :] + 1 / (r + 1) * np.array(xD)
                    xLr[j + 1, :] = xeq(yVr[j + 1, :])[0]
                    Tr[j + 1] = xeq(yVr[j + 1, :])[1]

                obj += (
                    np.linalg.norm(xF_obj - xLr[Fstg]) ** 2 +
                    np.linalg.norm(yF_obj - yVr[Fstg]) ** 2
                )
                
                # Stripping section profile
                
                xLs[nstg-1, :] = xB
                yVs[nstg-1, :] = yeq(xB)[0]
                Ts[nstg-1] = yeq(xB)[1]
        
                for j in stages_s:
                    xLs[j - 1, :] = s / (s + 1) * yVs[j, :] + 1 / (s + 1) * np.array(xB)
                    yVs[j - 1, :] = yeq(xLs[j - 1, :])[0]
                    Ts[j - 1] = yeq(xLs[j - 1, :])[1]

                obj += (
                    np.linalg.norm(xF_obj - xLs[Fstg]) ** 2 +
                    np.linalg.norm(yF_obj - yVs[Fstg]) ** 2
                )
                
                return obj
            
            # print(distill_obj(xF))
            # print(distill_obj(np.array([1, 0, 0])))
            # print(distill_obj(np.array([0, 0, 1])))
            
            eq_cons = {'type': 'eq',
               'fun' : lambda x: np.sum(x) - 1}

            bounds = sci.optimize.Bounds([0, 0, 0], [1, 1, 1])

            res = sci.optimize.minimize(lambda x: distill_obj(x),
                                        x0=xF+0.01,
                                        method='SLSQP',
                                        constraints=[eq_cons],
                                        bounds=bounds,
                                        tol=1e-3)

            # print(res.fun)
            # print(res)
            
            xD = res.x

            B = 1 - D
            xB = (xF - D * np.array(xD)) / B

            s = (
                q - 1 
                + (q + r) * np.linalg.norm(xF - xB)
                  / np.linalg.norm(xD - xF)
            )

            # Rectifying section profile
        
            xLr[0, :] = xD
            yVr[0, :] = yeq(xD)[0]
            Tr[0] = yeq(xD)[1]
            
            for j in stages_r:
                yVr[j + 1, :] = r / (r + 1) * xLr[j, :] + 1 / (r + 1) * np.array(xD)
                xLr[j + 1, :] = xeq(yVr[j + 1, :])[0]
                Tr[j + 1] = xeq(yVr[j + 1, :])[1]
                
            # Stripping section profile
            
            xLs[nstg-1, :] = xB
            yVs[nstg-1, :] = yeq(xB)[0]
            Ts[nstg-1] = yeq(xB)[1]
    
            for j in stages_s:
                xLs[j - 1, :] = s / (s + 1) * yVs[j, :] + 1 / (s + 1) * np.array(xB)
                yVs[j - 1, :] = yeq(xLs[j - 1, :])[0]
                Ts[j - 1] = yeq(xLs[j - 1, :])[1]
    
        res = distill_res(xF=xF, xB=xB, xD=xD, D=D, B=B, q=q, r=r, s=s,
                          nstg=nstg, fstg=fstg,
                          xLr=xLr, yVr=yVr, Tr=Tr,
                          xLs=xLs, yVs=yVs, Ts=Ts,
                          P=P)
        
        return res

    def distill_bfd(distill_res):
        # Draw a BFD of a distillation column

        res = distill_res

        P_str = np.round(res.P, 2)
        xF_str = np.round(res.xF, 2)

        if res.xB is None:
            x_str = '?'
        else:
            x_str = np.round(res.xB, 2)

        if res.xD is None:
            y_str = '?'
        else:
            y_str = np.round(res.xD, 2)

        fig1, ax1 = plt.subplots()
        plt.axis('off')
        _ = ax1.set_xlim(-4, 4)
        _ = ax1.set_ylim(-4, 4)

        patches.ArrowStyle.Curve

        feed = patches.Arrow(-3, 0, 2, 0, width=0.5, color='black')
        ax1.add_patch(feed)

        ax1.text(-1.1, 0.2,
                f'xF = {xF_str}',
                horizontalalignment='right',
                verticalalignment='bottom',
                fontsize=8,
                color='black')

        vap = patches.Arrow(1, 2.6, 2, 0, width=0.5, color='red')
        ax1.add_patch(vap)

        ax1.text(1.1, 2.8,
            f'xD = {y_str}',
            horizontalalignment='left',
            verticalalignment='bottom',
            fontsize=8,
            color='red')

        liq = patches.Arrow(1, -2.6, 2, 0, width=0.5, color='blue')
        ax1.add_patch(liq)

        ax1.text(1.1, -2.4,
            f'xB = {x_str}',
            horizontalalignment='left',
            verticalalignment='bottom',
            fontsize=8,
            color='blue')

        unit = patches.Rectangle((-1, -3), 2, 6,
                                 linewidth=2,
                                 edgecolor='black',
                                 facecolor='white',
                                 alpha=1)
        ax1.add_patch(unit)

        ax1.text(0, 0.5, 'Column',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=10)

        ax1.text(0, 0, f'P = {P_str} bar',
                 horizontalalignment='center',
                 verticalalignment='center',
                 fontsize=8)
        
        return fig1, ax1

    def duplicate(fig):
        pkl = pickle.dumps(fig)  # serialize figure
        fignew = pickle.loads(pkl)  # deserialize into fignew
        axnew = fignew.axes[0]
        
        return fignew, axnew
    
    bundle = namedtuple('vle3', ['Psat', 'yeq', 'xeq',
                                 'mix_props', 'flashT', 'flashVfrac',
                                 'distill', 'flash_bfd', 'distill_bfd',
                                 'fig', 'ax', 'plt', 'duplicate'])
    
    return bundle(Psat=Psat, yeq=yeq, xeq=xeq,
                  mix_props=mix_props, flashT=flashT,
                  flashVfrac=flashVfrac, distill=distill,
                  flash_bfd=flash_bfd, distill_bfd=distill_bfd,
                  fig=fig, ax=ax, plt=plt, duplicate=duplicate)
