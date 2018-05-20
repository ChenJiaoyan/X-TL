#! /usr/bin/python

import os
import csv
import scipy.stats as stats

DIR = 'your_home_dir/ExpRes1'
COR_DIR = os.path.join(DIR, 'Corr')
if not os.path.exists(COR_DIR):
    os.mkdir(COR_DIR)

'''
enquiry over entailment closure and explanatory knowledge
entailment mapping: 
'''
E_MAPPING = {
    'e1': 'locatedIn(ori, CA)',
    'e2': 'locatedIn(des, CA)',
    'e3': 'inCADep(dep)',
    'e4': 'locatedIn(ori, East)',
    'e5': 'locatedIn(ori, West)',
    'e6': 'inEastDep(dep)',
    'e7': 'inWestDep(dep)',
    'e8': 'hasOri(dep, LAX)',
    'e9': 'hasOri(dep, SFO)',
    'e10': 'hasOri(dep, JFK)',
    'e11': 'hasOri(dep, ORD)',
    'e12': 'hasOri(dep, ATL)',
    'e13': 'hasOri(dep, DFW)',
    'e14': 'hasOri(dep, CLT)',
    'e15': 'hasOri(dep, EWR)',
    'e16': 'hasDes(dep, LAX)',
    'e17': 'hasDes(dep, SFO)',
    'e18': 'hasDes(dep, JFK)',
    'e19': 'hasDes(dep, ORD)',
    'e20': 'hasDes(dep, ATL)',
    'e21': 'hasDes(dep, DFW)',
    'e22': 'hasDes(dep, CLT)',
    'e23': 'hasDes(dep, EWR)',
    'e24': 'hasCar(dep, DL)',
    'e25': 'hasCar(dep, AA)',
    'e26': 'hasCar(dep, B6)',
    'e27': 'hasCar(dep, UA)',
    'e28': 'hasCar(dep, VX)',
    'e29': 'hasCar(dep, WN)',
    'e30': 'serveFor(ori, NewYork)',
    'e31': 'serviceForMegaCity(ori)',
    'e32': 'hasHub(car, ori)',
    'e33': 'hasHub(car, des)',
    'e34': 'hasCar(dep, NK)',
    'e35': 'hasDes(dep, DEN)',
    'e36': 'hasDes(dep, BOS)',
    'e37': 'coastalAirport(ori)',
    'e38': 'coastalAirport(des)',
    'e39': 'listedCarrier(car)',
    'e40': 'smallCarrier(car)',
    'e41': 'bigCarrier(car)',
}


def ent_existence(ent, dom):
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

    tmp = dom.split('_')
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


def co_existence_quaternary(ent, tra):
    tmp = tra.split('-')
    dom_s, dom_t = tmp[0], tmp[1]
    exs_s = ent_existence(ent=ent, dom=dom_s)
    exs_t = ent_existence(ent=ent, dom=dom_t)
    if exs_s and not exs_t:
        return 1
    elif not exs_s and exs_t:
        return 2
    elif exs_s and exs_t:
        return 3
    else:
        return 0


def co_existence_binary(ent, tra):
    tmp = tra.split('-')
    dom_s, dom_t = tmp[0], tmp[1]
    exs_s = ent_existence(ent=ent, dom=dom_s)
    exs_t = ent_existence(ent=ent, dom=dom_t)
    if exs_s and exs_t:
        return 1
    else:
        return 0


def write_csv(contents, f_name):
    csv_f = open(f_name, 'wb')
    writer = csv.writer(csv_f)
    writer.writerows(contents)
    csv_f.close()


'''
# extract feature specificity/generality indexes (SI/GI)
# calculate feature transferability index (TI)
print '--------- Calculate Transferability Indexes -------------'
HT_Dir = os.path.join(DIR, 'HT_Result')
ST_Dir = os.path.join(DIR, 'ST_Result')
S_Dir = os.path.join(DIR, 'Sample')
domains = os.listdir(S_Dir)
R_Beta = {}
for domain in domains:
    r_beta = np.load(os.path.join(S_Dir, domain, 'local_test_res.npy'))
    R_Beta[domain] = np.average(r_beta, axis=0)
header = ['S-T', 'T-ACC', 'T-AUC', 'HT-ACC', 'HT-AUC', 'HT-ACC-SI', 'HT-AUC-SI', 'ST-ACC', 'ST-AUC', 'ST-ACC-SI',
          'ST-AUC-SI', 'ACC-FI', 'AUC-FI']
lines = [header]
for i, d1 in enumerate(domains):
    if i % 10 == 0:
        print 'i: %d ' % i
    for d2 in domains:
        tra = '%s-%s' % (d1, d2)
        tra_f = '%s.npy' % tra
        if os.path.exists(os.path.join(HT_Dir, tra_f)) and os.path.exists(os.path.join(ST_Dir, tra_f)):
            r_ht = np.average(np.load(os.path.join(HT_Dir, tra_f)), axis=0)
            r_st = np.average(np.load(os.path.join(ST_Dir, tra_f)), axis=0)
            line = [tra] + list(R_Beta[d2]) + list(r_ht) + list((R_Beta[d2] - r_ht) / r_ht) + list(r_st) + list(
                (r_st - R_Beta[d2]) / R_Beta[d2]) + list((r_st - R_Beta[d2]) / R_Beta[d2] - (R_Beta[d2] - r_ht) / r_ht)
            lines.append(line)
write_csv(lines, os.path.join(COR_DIR, 'tra.csv'))
print '--------- Done -------------'
'''

'''
# Calculate the correlation between entailment narrators and feature indexes
# One-way ANOVA test: categorical vs numerical variables
# Lower p-value --> higher probability to reject H0 --> higher probability the transferability differs between groups
# --> higher correlation between the narrator and the transferability
# result: it seems p-value is close to 0 for many entailments ;), and hard to analysis with four cases
ents = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7']
for e in ents:
    acc0, acc1, acc2, acc3 = [], [], [], []
    auc0, auc1, auc2, auc3 = [], [], [], []
    f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
    reader = csv.DictReader(f)
    for row in reader:
        F_id = row['S-T']
        co_ex = co_existence_quaternary(ent=e, tra=F_id)
        acc, auc = float(row['ACC-FI']), float(row['AUC-FI'])
        if co_ex == 0:
            acc0.append(acc)
            auc0.append(auc)
        elif co_ex == 1:
            acc1.append(acc)
            auc1.append(auc)
        elif co_ex == 2:
            acc2.append(acc)
            auc2.append(auc)
        else:
            acc3.append(acc)
            auc3.append(auc)
    f.close()
#    _, p_val_acc = stats.f_oneway(acc0, acc1, acc2, acc3)
    _, p_val_auc = stats.f_oneway(auc0, auc1, auc2, auc3)
    print '\n entailment: %s' % e
#    print 'p-value with Accuracy: %f' % p_val_acc
    print 'p-value with AUC: %f' % p_val_auc
#    print 'Acc. Imp. Avg., 0: %f, 1: %f, 2: %f, 3: %f' % (
#    np.average(acc0), np.average(acc1), np.average(acc2), np.average(acc3))
    print 'AUC Imp. Avg., 0: %f, 1: %f, 2: %f, 3: %f \n' % (
    np.average(auc0), np.average(auc1), np.average(auc2), np.average(auc3))
    
'''

'''
# One entailment
# Pearson correlation analysis between co-existence and transferability

# ents = ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7']
# ents = E_MAPPING.keys()
ents = ['e%d' % i for i in range(41, 42)]
for e in ents:
    auc_v = []
    co_ex_v = []
    f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
    reader = csv.DictReader(f)
    for row in reader:
        auc = float(row['AUC-FI'])
        # auc = float(row['ST-AUC-SI'])
        F_id = row['S-T']
        co_ex = co_existence_quaternary(ent=e, tra=F_id)
        if co_ex == 1:
            co_ex_v.append(0)
            auc_v.append(auc)
        if co_ex == 3:
            co_ex_v.append(1)
            auc_v.append(auc)
    f.close()
    corr, p_val = stats.pearsonr(co_ex_v, auc_v)
    print 'entailment: %s, %s' % (e, E_MAPPING[e])
    print 'correlation: %f, p-value: %f \n' % (corr, p_val)
'''

'''
# Two entailments
# Pearson correlation analysis between co-existence and transferability
header = ['ent1', 'ent2', 'coefficient', 'p-value']
lines = [header]
ents = ['e%d' % i for i in range(1, 42)]
for e1 in ents:
    for e2 in ents:
        if e1 == e2:
            continue
        auc_v = []
        co_ex_v = []
        f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
        reader = csv.DictReader(f)
        for row in reader:
            auc = float(row['AUC-FI'])
            # auc = float(row['ST-AUC-SI'])
            F_id = row['S-T']
            co_ex1 = co_existence_quaternary(ent=e1, tra=F_id)
            co_ex2 = co_existence_quaternary(ent=e2, tra=F_id)
            if co_ex1 == 1 and co_ex2 == 1:
                co_ex_v.append(0)
                auc_v.append(auc)
            if co_ex1 == 3 and co_ex2 == 3:
                co_ex_v.append(1)
                auc_v.append(auc)
        f.close()
        if 0 < len(co_ex_v) == len(auc_v):
            corr, p_val = stats.pearsonr(co_ex_v, auc_v)
            if abs(corr) >= 0.1:
                line = '%s:%s,%s:%s,%f,%f' % (e1, E_MAPPING[e1].replace(',', ''), e2, E_MAPPING[e2].replace(',', ''), corr, p_val)
                print line
                lines.append(line.split(','))
write_csv(lines, os.path.join(COR_DIR, 'narrator_2ent.csv'))
'''

'''
# Three entailments
# Pearson correlation analysis between co-existence and transferability
header = ['ent1', 'ent2', 'ent3', 'coefficient', 'p-value']
lines = [header]
ents = ['e%d' % i for i in range(1, 42)]
f_2ent = open(os.path.join(COR_DIR, 'narrator_2ents.csv'), 'r')
reader_2ent = csv.DictReader(f_2ent)
for r in reader_2ent:
    ent1, ent2, coe, p_val = r['ent1'], r['ent2'], float(r['coefficient']), float(r['p-value'])
    if abs(coe) >= 0.12 and p_val < 0.05:
        e1 = ent1.split(':')[0]
        e2 = ent2.split(':')[0]
        for e3 in ents:
            if e3 == e1 or e3 == e2:
                continue
            auc_v = []
            co_ex_v = []
            f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
            reader = csv.DictReader(f)
            for row in reader:
                auc = float(row['AUC-FI'])
                F_id = row['S-T']
                co_ex1 = co_existence_quaternary(ent=e1, tra=F_id)
                co_ex2 = co_existence_quaternary(ent=e2, tra=F_id)
                co_ex3 = co_existence_quaternary(ent=e3, tra=F_id)
                if co_ex1 == 1 and co_ex2 == 1 and co_ex3 == 1:
                    co_ex_v.append(0)
                    auc_v.append(auc)
                if co_ex1 == 3 and co_ex2 == 3 and co_ex3 == 3:
                    co_ex_v.append(1)
                    auc_v.append(auc)
            f.close()
            if 0 < len(co_ex_v) == len(auc_v):
                corr, p_val = stats.pearsonr(co_ex_v, auc_v)
                if abs(corr) >= 0.1 and p_val < 0.05:
                    line = '%s:%s,%s:%s,%s:%s,%f,%f' % (
                        e1, E_MAPPING[e1].replace(',', ''), e2, E_MAPPING[e2].replace(',', ''), e3,
                        E_MAPPING[e3].replace(',', ''), corr, p_val)
                    print line
                    lines.append(line.split(','))
write_csv(lines, os.path.join(COR_DIR, 'narrator_3ents.csv'))
'''


'''
# Four entailments
# Pearson correlation analysis between co-existence and transferability
'''
header = ['ent1', 'ent2', 'ent3', 'ent4', 'coefficient', 'p-value']
lines = [header]
ents = ['e%d' % i for i in range(1, 42)]
f_3ent = open(os.path.join(COR_DIR, 'narrator_3ents.csv'), 'r')
reader_3ent = csv.DictReader(f_3ent)
for r in reader_3ent:
    ent1, ent2, ent3, coe, p_val = r['ent1'], r['ent2'], r['ent3'], float(r['coefficient']), float(r['p-value'])
    if abs(coe) >= 0.23 and p_val < 0.03:
        e1 = ent1.split(':')[0]
        e2 = ent2.split(':')[0]
        e3 = ent3.split(':')[0]
        for e4 in ents:
            if e4 == e1 or e4 == e2 or e4 == e3:
                continue
            auc_v = []
            co_ex_v = []
            f = open(os.path.join(COR_DIR, 'tra.csv'), 'r')
            reader = csv.DictReader(f)
            for row in reader:
                auc = float(row['AUC-FI'])
                F_id = row['S-T']
                co_ex1 = co_existence_quaternary(ent=e1, tra=F_id)
                co_ex2 = co_existence_quaternary(ent=e2, tra=F_id)
                co_ex3 = co_existence_quaternary(ent=e3, tra=F_id)
                co_ex4 = co_existence_quaternary(ent=e4, tra=F_id)
                if co_ex1 == 1 and co_ex2 == 1 and co_ex3 == 1 and co_ex4 == 1:
                    co_ex_v.append(0)
                    auc_v.append(auc)
                if co_ex1 == 3 and co_ex2 == 3 and co_ex3 == 3 and co_ex4 == 3:
                    co_ex_v.append(1)
                    auc_v.append(auc)
            f.close()
            if 0 < len(co_ex_v) == len(auc_v):
                corr, p_val = stats.pearsonr(co_ex_v, auc_v)
                if abs(corr) >= 0.1:
                    line = '%s:%s,%s:%s,%s:%s,%s:%s,%f,%f' % (
                        e1, E_MAPPING[e1].replace(',', ''), e2, E_MAPPING[e2].replace(',', ''), e3,
                        E_MAPPING[e3].replace(',', ''), e4, E_MAPPING[e4].replace(',', ''), corr, p_val)
                    print line
                    lines.append(line.split(','))
write_csv(lines, os.path.join(COR_DIR, 'narrator_4ents.csv'))
