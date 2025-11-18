import numpy as np

# == compute complex visibility can be variable in time:
cvis = {'fit':{},
        # -- WL and dWL have same length N:
        'WL':np.array([]),
        'dWL':np.array([]),
        # -- all these have same length P:
        'MJD': np.array([]),   
        'u':np.array([]),
        'v':np.array([]),
        # -- result, both have NxP dims
        'V': np.array([]), # complex visibility (normalised)
        'F': np.array([]), # flux
    }   

def computeSingleVis(cvis, param):
    res = {}
    # -- compute 'V' and 'F' based on parameters 'param', 'WL', etc.
    res['V'] = np.ones((len(cvis['u'], cvis['WL'])))
    res['F'] = np.ones((len(cvis['MJD'], cvis['WL'])))
    return res

# == combine components: 
# only works if WL, dWL, MJD, u, v and the same!
P = componentSplit(param)
TMP = [computeSingleVis(cvis, p) for p in P]
cvis['F'] = sum([t['F'] for t in TMP])
cvis['V'] = sum([t['F']*t['V'] for t in TMP])/cvis['F']

# -- based on cvis, compute observables
pass