#! /usr/bin/python

import os
import csv
import scipy.stats as stats

'''
# whether an ent exists in a domain
'''
def ent_existence(ent, my_dom):
    CA_Apts = ['LAX', 'SFO']
    NY_Apts = ['EWR', 'JFK']
    MegaCity_Apts = ['LAX', 'JFK', 'EWR']
    West_Apts = ['LAX', 'SFO', 'DFW']
    East_Apts = ['JFK', 'EWR', 'ORD', 'ATL', 'CLT']
    Coastal_Apts = ['LAX', 'SFO', 'EWR', 'JFK', 'BOS']
    Apt_Hub = {'DL': ['ATL', 'JFK', 'LAX'], 'AA': ['DFW', 'JFK', 'LAX', 'ORD'], 'UA': ['ORD', 'DEN', 'LAX', 'ORD'],
               'B6': ['JFK'], 'VX': ['LAX', 'SFO'], 'WN': ['ORD', 'LAX'], 'F9': ['DEN'], 'NK': []}
    Listed_Car = ['AA', 'DL', 'UA']
    Small_Car = ['F9', 'NK', 'VX', 'B6']
    Big_Car = ['AA', 'DL', 'UA', 'WN']

    tmp = my_dom.split('_')
    car, ori, des = tmp[0], tmp[1], tmp[2]
    if ent == 'e1':
        return True if ori in CA_Apts else False
    if ent == 'e2':
        return True if des in CA_Apts else False
    if ent == 'e3':
        return True if (ori in CA_Apts and des in CA_Apts) else False
    if ent == 'e4':
        return True if ori in East_Apts else False
    if ent == 'e5':
        return True if ori in West_Apts else False
    if ent == 'e6':
        return True if (ori in East_Apts) and (des in East_Apts) else False
    if ent == 'e7':
        return True if (ori in West_Apts) and (des in West_Apts) else False
    if ent == 'e8':
        return True if ori == 'LAX' else False
    if ent == 'e9':
        return True if ori == 'SFO' else False
    if ent == 'e10':
        return True if ori == 'JFK' else False
    if ent == 'e11':
        return True if ori == 'ORD' else False
    if ent == 'e12':
        return True if ori == 'ATL' else False
    if ent == 'e13':
        return True if ori == 'DFW' else False
    if ent == 'e14':
        return True if ori == 'CLT' else False
    if ent == 'e15':
        return True if des == 'EWR' else False
    if ent == 'e16':
        return True if des == 'LAX' else False
    if ent == 'e17':
        return True if des == 'SFO' else False
    if ent == 'e18':
        return True if des == 'JFK' else False
    if ent == 'e19':
        return True if des == 'ORD' else False
    if ent == 'e20':
        return True if des == 'ATL' else False
    if ent == 'e21':
        return True if des == 'DFW' else False
    if ent == 'e22':
        return True if des == 'CLT' else False
    if ent == 'e23':
        return True if des == 'EWR' else False
    if ent == 'e24':
        return True if car == 'DL' else False
    if ent == 'e25':
        return True if car == 'AA' else False
    if ent == 'e26':
        return True if car == 'B6' else False
    if ent == 'e27':
        return True if car == 'UA' else False
    if ent == 'e28':
        return True if car == 'VX' else False
    if ent == 'e29':
        return True if car == 'WN' else False
    if ent == 'e30':
        return True if ori in NY_Apts else False
    if ent == 'e31':
        return True if ori in MegaCity_Apts else False
    if ent == 'e32':
        return True if ori in Apt_Hub[car] else False
    if ent == 'e33':
        return True if des in Apt_Hub[car] else False
    if ent == 'e34':
        return True if car == 'NK' else False
    if ent == 'e35':
        return True if des == 'DEN' else False
    if ent == 'e36':
        return True if des == 'BOS' else False
    if ent == 'e37':
        return True if ori in Coastal_Apts else False
    if ent == 'e38':
        return True if des in Coastal_Apts else False
    if ent == 'e39':
        return True if car in Listed_Car else False
    if ent == 'e40':
        return True if car in Small_Car else False
    if ent == 'e41':
        return True if car in Big_Car else False


DIR = 'your_home_dir/ExpRes1'
ENT_DIR = os.path.join(DIR, 'Entailments')
COR_DIR = os.path.join(DIR, 'Corr')
if not os.path.exists(COR_DIR):
    os.mkdir(COR_DIR)

'''
# Read transferability indexes
'''
print 'Read transferability indexes \n'
F_Index = {}
f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
reader = csv.DictReader(f)
for row in reader:
    F_Index[row['S-T']] = float(row['AUC-FI'])
f.close()

'''
# Read domains and entailments
'''
print 'Read domains and entailment sets\n'
fs = os.listdir(ENT_DIR)
doms, ents = [], {}
for f in fs:
    dom = f[0:20]
    if dom not in doms:
        doms.append(dom)
        cls_f = open(os.path.join(ENT_DIR, '%s_class_ents.csv' % dom))
        cls_e = [line.strip() for line in cls_f.readlines()]
        cls_f.close()
        rol_f = open(os.path.join(ENT_DIR, '%s_role_ents.csv' % dom))
        rol_e = [line.strip() for line in rol_f.readlines()]
        rol_f.close()
        ents[dom] = cls_e + rol_e

'''
# Add external axioms from DBPedia
print 'Add DBPedia axioms\n'
for dom in doms:
    x_f = open(os.path.join(ENT_DIR, '%s_x_axioms.csv' % dom))
    axioms = [line.strip() for line in x_f.readlines()]
    x_f.close()
    if dom in ents:
        ents[dom] = ents[dom] + axioms
    else:
        ents[dom] = axioms
'''
'''
# Add external axioms simulated
print 'Add external axioms simulated\n'
E_MAPPING = {'e1': 'ori,locatedIn,CA', 'e2': 'des,locatedIn,CA', 'e3': 'inCADep,dep', 'e4': 'ori,locatedIn,East',
             'e5': 'ori,locatedIn,West', 'e6': 'inEastDep,dep', 'e7': 'inWestDep,dep', 'e8': 'dep,hasOri,LAX',
             'e9': 'dep,hasOri,SFO', 'e10': 'dep,hasOri,JFK', 'e11': 'dep,hasOri,ORD', 'e12': 'dep,hasOri,ATL',
             'e13': 'dep,hasOri,DFW', 'e14': 'dep,hasOri,CLT', 'e15': 'dep,hasOri,EWR', 'e16': 'dep,hasDes,LAX',
             'e17': 'dep,hasDes,SFO', 'e18': 'dep,hasDes,JFK', 'e19': 'dep,hasDes,ORD', 'e20': 'dep,hasDes,ATL',
             'e21': 'dep,hasDes,DFW', 'e22': 'dep,hasDes,CLT', 'e23': 'dep,hasDes,EWR', 'e24': 'dep,hasCar,DL',
             'e25': 'dep,hasCar,AA', 'e26': 'dep,hasCar,B6', 'e27': 'dep,hasCar,UA', 'e28': 'dep,hasCar,VX',
             'e29': 'dep,hasCar,WN', 'e30': 'ori,serveFor,New_York', 'e31': 'serviceForMegaCity,ori',
             'e32': 'car,hasHub,ori', 'e33': 'car,hasHub,des', 'e34': 'NK,hasCar,NK', 'e35': 'dep,hasDes,DEN',
             'e36': 'dep,hasDes,BOS', 'e37': 'coastalAirport,ori', 'e38': 'coastalAirport,des',
             'e39': 'listedCarrier,car', 'e40': 'smallCarrier,car', 'e41': 'bigCarrier,car'
             }
for dom in doms:
    e = []
    for ent_id in E_MAPPING.keys():
        if ent_existence(ent_id, dom):
            e.append(E_MAPPING[ent_id])
    if dom in ents:
        ents[dom] = ents[dom] + e
    else:
        ents[dom] = e
'''

'''
# Calculate entailment indexes of inv/new/obs
'''
print 'Calculate indexes of inv/new/obs \n'
tra_v, inv_v, new_v, obs_v = [], [], [], []
for s_dom in doms:
    for t_dom in doms:
        F_id = '%s-%s' % (s_dom, t_dom)
        if s_dom == t_dom:
            continue
        tra_v.append(F_Index[F_id])
        s_ents, t_ents = ents[s_dom], ents[t_dom]
        new = len(set(t_ents) - set(s_ents)) / float(len(t_ents))
        new_v.append(new)
        obs = len(set(s_ents) - set(t_ents)) / float(len(s_ents))
        obs_v.append(obs)
        inv = len(set(s_ents).intersection(t_ents)) / float(len(set(s_ents).union(t_ents)))
        inv_v.append(inv)

'''
# Boson correlation analysis between inv/new/obs and transferability
'''
print 'Boson correlation analysis \n'
inv_corr, inv_p_val = stats.pearsonr(tra_v, inv_v)
new_corr, new_p_val = stats.pearsonr(tra_v, new_v)
obs_corr, obs_p_val = stats.pearsonr(tra_v, obs_v)
print 'inv_corr: %f, inv_p_vale: %f' % (inv_corr, inv_p_val)
print 'new_corr: %f, new_p_vale: %f' % (new_corr, new_p_val)
print 'obs_corr: %f, obs_p_vale: %f' % (obs_corr, obs_p_val)
