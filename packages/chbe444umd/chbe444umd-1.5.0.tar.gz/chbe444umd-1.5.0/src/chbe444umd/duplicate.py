# Reaction Rate Field Plot: Reaction System Definition
# Written for CHBE444: Design I, University of Maryland
# (C) Ganesh Sriram, 2025
# Originally written in MATLAB in 2017

import pickle


def duplicate_figure(fig):
    pkl = pickle.dumps(fig)  # serialize figure
    fignew = pickle.loads(pkl)  # deserialize into fignew
    axnew = fignew.axes[0]
    return fignew, axnew
