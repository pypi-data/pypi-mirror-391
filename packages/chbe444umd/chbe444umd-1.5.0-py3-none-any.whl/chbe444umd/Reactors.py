# Reaction Rate Field Plot: Reaction System Definition
# Written for CHBE444: Design I, University of Maryland
# (C) Ganesh Sriram, 2025
# Originally written in MATLAB in 2017

# Wishlist
# - Tab completion of reactor attributes and functions
# - Mark points and tau values on reactor curve:
# - - allow multiple points to be specified
# - Curves and tangents
# - - separate the individual paths of a CSTR curve
# - - draw CSTR tangents, especially when multiple tangents are possible

import numpy as np
import scipy as sci
import matplotlib.pyplot as plt


class ReactorRegistry:
    def __init__(self):
        self._store = {}

    def add(self, reactor):
        name = reactor.name
        if name in self._store:
            raise ValueError(f"Reactor {name!r} already registered.")
        self._store[name] = reactor
        setattr(self, name, reactor)

    def __getitem__(self, key):
        return self._store[key]

    def __iter__(self):
        return iter(self._store)  # iterates keys

    def __len__(self):
        return len(self._store)

    def items(self):
        return self._store.items()

    def keys(self):
        return self._store.keys()

    def values(self):
        return self._store.values()

    def __repr__(self):
        if not self._store:
            return "Reactors()"
        lines = ["Reactors("]
        for name, obj in self._store.items():
            lines.append(f"{name}:\n{obj!r}")
        lines.append(")")
        return "\n".join(lines)


reactors = ReactorRegistry()


class Reactor:
    """
    Container for reactor interacting with a reactive system.

    Reactor properties (name, flow, feed and time) must be specified as
    illustrated below.

    name:          name = 'PFR from fresh feed' (optional)
    type:          flow_type = 'pfr' (not case-sensitive)
                   PFR options:  'pfr', 'plug', 'plug flow', 'tube'
                   CSTR options: 'cstr', 'mixed', 'tank', 'stirred tank',
                                 'continuously stirred tank'
    feed:          feed = [1, 0] (specify according to axes)
    time constant: time = 10 (reactor is simulated from tau = 0 to this time)
    """

    def __init__(self, flow_type, feed, time=0, name='',
                 curve=None, tau=None, x=None, y=None, xy=None,
                 slope_x=None, slope_y=None):
        self.flow_type = flow_type
        self.feed = feed
        self.time = time
        self.name = name
        self.curve = []
        self.tau = np.array([])
        self.x = np.array([])
        self.y = np.array([])
        self.xy = np.array([])
        self.slope_x = []
        self.slope_y = []
        self.pfr_identifiers = (
            'pfr', 'plug', 'plug flow', 'tube'
        )
        self.cstr_identifiers = (
            'cstr', 'mixed', 'stirred tank', 'tank',
            'continuously stirred tank'
        )
        if reactors is not None:
            reactors.add(self)

    def __repr__(self):
        if np.array(self.tau).size == 0:
            disp_text = (f'Reactor:\n'
                     f'    name:\t{self.name}\n'
                     f'    flow type:\t{self.flow_type}\n'
                     f'    feed:\t{self.feed}')
        else:
            n_tau = np.array(self.tau).size
            disp_text = (f'Reactor:\n'
                     f'    name:\t{self.name}\n'
                     f'    flow type:\t{self.flow_type}\n'
                     f'    feed:\t{self.feed}\n'
                     f'    time:\t{self.time}\n'
                     f'    curve:\tarray of curve objects\n'
                     f'    tau:\t{n_tau}×1 numpy array of tau values\n'
                     f'    x:\t\t{n_tau}×1 numpy array of x values\n'
                     f'    y:\t\t{n_tau}×1 numpy array of y values\n'
                     f'    xy:\t\t{n_tau}×2 numpy array of [x, y] values\n'
                     f'    slope_i:\t{n_tau}×1 numpy arrays of slope data')
        return disp_text

    def simulate(self, system, ax, time_limit=10,
                 n_points=1000, show_feed=True):
        """
        Simulate and plot a reactor.

        reactor.simulate(time_limit=10, n_points=1000, show_feed=True)
            time_limit: default time limit for tau
            n_points:   number of integration or calculation points
            show_feed:  whether feed should be displayed as a point
        """
        def ratet(t, x):
            return system.rate(x)

        xF = self.feed
        if np.size(self.feed, 0) != 2:
            raise ValueError('The feed should have exactly 2 coordinates')
        if show_feed:
            ax.plot(xF[0], xF[1], 'ko', markersize=6)

        if self.flow_type.lower() in self.pfr_identifiers:
            if self.time == 0:
                int_t = time_limit
            else:
                int_t = self.time
            with np.errstate(all='ignore'):
                res = sci.integrate.solve_ivp(ratet, [0, int_t], xF,
                                              t_eval=np.linspace(
                                                0, int_t, n_points)
                                              )
                self.curve = ax.plot(res.y[0, :], res.y[1, :], 'r-')
                self.tau = np.array(res.t)
                self.x = np.array(res.y[0])
                self.y = np.array(res.y[1])
                self.xy = np.column_stack((self.x, self.y))
                rates_pfr = system.rate(res.y)
                self.slope_x = rates_pfr[0, :]
                self.slope_y = rates_pfr[1, :]

        if self.flow_type.lower() in self.cstr_identifiers:
            h_lim = system.h_lim
            v_lim = system.v_lim
            xx = np.linspace(h_lim[0], h_lim[1], n_points)
            yy = np.linspace(v_lim[0], v_lim[1], n_points)
            X, Y = np.meshgrid(xx, yy)

            def cstrpt(x, y):
                r = system.rate([x, y])
                with np.errstate(all='ignore'):
                    f = y - xF[1] - r[1] / r[0] * (x - xF[0])
                    return f

            self.curve = ax.contour(X, Y, cstrpt(X, Y),
                                          levels=[0],
                                          colors='b',
                                          linestyles='-',
                                          linewidths=1.5)
            xy = np.transpose(self.curve.allsegs[0][0])
            self.tau = np.array(
                (xy - np.array(xF)[:, None]) /
                system.rate([xy[0, :], xy[1, :]])
            )[0, :]
            # tau is calculated in duplicate from both axes, so use only one
            self.x = np.array(xy[0, :])
            self.y = np.array(xy[1, :])
            self.xy = np.column_stack((self.x, self.y))

            self.slope_x = self.x[1:] - self.x[:-1]
            self.slope_x = np.hstack(([self.slope_x[0]], self.slope_x[:-1]))
            self.slope_y = self.y[1:] - self.y[:-1]
            self.slope_y = np.hstack(([self.slope_y[0]], self.slope_y[:-1]))
            # Add dummy value to each slope array to make up for element
            # lost while taking difference
        return ax

    def plot_point(self, ax, tau=[], x=[], y=[],
                   near_point=[], distance=1.5):
        """
        Locate and plot a point on a reactor curve corresponding to a
        specified value of tau, x or y. Optionally, this point could be
        constrained to be within a specified distance from a specified point
        (near_point) in the concentration space.

        reactor.plot_point(ax, tau=0, x=0, y=0, near_point=[], distance=1.5)
            ax:         Axes on which the point should be plotted
            tau, x, y:  Scalars specifying the point to be locate At least one
                        of these inputs must be provided
                        If multiple inputs are present, they are matched
                        in the order tau, x, y
                        Thus, y will be matched only if tau and x are both []
                        And x will be matched only if tau is []
            near_point: 2x1 numpy array (defaults to reactor feed)
            distance:   Scalar indicating the search distance from the specified
                        point (defaults to 1.5)
                        If only one point meets the given criteria (tau,
                        x or y), set this distance to a large number,
                        e.g., 1.5
        """
        if not near_point:
            near_point = self.feed  # point defaults to reactor feed
        else:
            near_point = np.array(near_point)

        d = np.sqrt((self.x - near_point[0])**2 + (self.y - near_point[1])**2)
        xx = np.where(d < distance, self.x, np.nan)
        yy = np.where(d < distance, self.y, np.nan)
        tt = np.where(d < distance, self.tau, np.nan)

        # if statements are typed in reverse order of precedence
        if y and yy.any():
            idx = np.abs(yy - y).argmin()
        if x and xx.any():
            idx = np.abs(xx - x).argmin()
        if tau and tt.any():
            idx = np.abs(tt - tau).argmin()
        tau = tt[idx]
        x = xx[idx]
        y = yy[idx]
        label = f' $\\tau=$ {np.round(tau, 3)}, ({np.round(x, 3)}, {np.round(y, 3)})'
        if self.flow_type in self.pfr_identifiers:
            ax.plot(x, y, 'ro', markersize=6)
            ax.text(x, y, label, ha='left', va='center')
        elif self.flow_type in self.cstr_identifiers:
            ax.plot(x, y, 'bo', markersize=6)
            ax.text(x, y, label, ha='left', va='center')
        return ax

    def plot_tangent(self, ax, from_point, near_point=[], distance=1.5):
        """
        Plot a tangent to a reactor curve from a specified point
        (from_point). Optionally, the tangent could be constrained to
        touch the curve within a specified distance from another point
        (near_point) in the concentration space.

        reactor.plot_tangent(ax, from_point, near_point=[])
            ax:         Axes on which the tangent should be plotted
            from_point: Point from where tangent should be plotted, 2x1
                        numpy array
            near_point: 2x1 numpy array (defaults to reactor feed)
            distance:   Scalar indicating the search distance from the
                        specified point (defaults to 1.5)
                        If only one point meets the given criteria (tau,
                        x or y), set this distance to a large number,
                        e.g., 1.5
            tol:        Tolerance for tangent
                        Set to around 1e-2, adjust if no tangents are found
        """

        from_point = np.array(from_point)
        if not near_point:
            near_point = self.feed  # point defaults to reactor feed
        else:
            near_point = np.array(near_point)

        d = np.sqrt((self.x - near_point[0])**2 + (self.y - near_point[1])**2)
        xx = np.where(d < distance, self.x, np.nan)
        yy = np.where(d < distance, self.y, np.nan)

        xy = np.column_stack((xx, yy))

        angle_point_to_reactor = np.atan2(
            xy[:, 1] - from_point[1],
            xy[:, 0] - from_point[0]
        )

        angle_tangent = np.atan2(self.slope_y, self.slope_x)

        def angle_diff(a, b):
            return np.arctan2(np.sin(a - b), np.cos(a - b))

        idx = np.abs(
            angle_diff(angle_point_to_reactor, angle_tangent)
        ).argmin()

        if np.abs((angle_point_to_reactor[idx] - angle_tangent[idx])) < 1e-2:
            (line, ) = ax.plot((from_point[0], xy[idx, 0]),
                               (from_point[1], xy[idx, 1]), 'k-')
        else:
            print('Tangent not feasible from the given point (within tolerance)')
        return ax, line
