#! /usr/bin/python
import os

ENT_DIR = 'your_home_dir/Onto/Entailments'
sigma, kappa, tau = 0.99, 1.0, 0.8

doms = []
for f in os.listdir(ENT_DIR):
    if f[0:20] not in doms:
        doms.append(f[0:20])

for i, dom in enumerate(doms):
    print '\n i: %d,  domain: %s \n' % (i, dom)
    all_c_g, all_r_g, filter_c_g, filter_r_g = [], [], [], []
    all_ind, filter_ind = [], []

    IMP_F = os.path.join(ENT_DIR, '%s_imp.csv' % dom)
    EFF_F = os.path.join(ENT_DIR, '%s_eff.csv' % dom)
    CLS_ENT_F = os.path.join(ENT_DIR, '%s_class_ents.csv' % dom)
    ROL_ENT_F = os.path.join(ENT_DIR, '%s_role_ents.csv' % dom)
    ROOT_IND_F = os.path.join(ENT_DIR, '%s_root_ind.csv' % dom)

    '''
        # read important entailments
    '''
    imp_f = open(IMP_F, 'r')
    imp = {}
    for line in imp_f.readlines():
        tmp = line.strip().split(':')
        imp[tmp[0]] = float(tmp[1])
    imp_f.close()
    for i, g in enumerate(imp.keys()):
        if len(g.split(',')) == 2:
            if g not in all_c_g:
                all_c_g.append(g)
            if imp[g] >= sigma and g not in filter_c_g:
                filter_c_g.append(g)
        if len(g.split(',')) == 3:
            if g not in all_r_g:
                all_r_g.append(g)
            if imp[g] >= sigma and g not in filter_r_g:
                filter_r_g.append(g)

    '''
        # read effective entailments
    '''
    eff_f = open(EFF_F, 'r')
    eff = {}
    for line in eff_f.readlines():
        tmp = line.strip().split(':')
        tmp2 = tmp[1].split(',')
        eff[tmp[0]] = float(tmp2[1])
    eff_f.close()
    for i, g in enumerate(eff.keys()):
        if len(g.split(',')) == 2:
            if g not in all_c_g:
                all_c_g.append(g)
            if eff[g] >= tau and g not in filter_c_g:
                filter_c_g.append(g)
        if len(g.split(',')) == 3:
            if g not in all_r_g:
                all_r_g.append(g)
            if eff[g] >= tau and g not in filter_r_g:
                filter_r_g.append(g)

    '''
        # extract individuals 
    '''
    for g in filter_c_g:
        i = g.split(',')[1]
        if i not in filter_ind:
            filter_ind.append(i)
    for g in filter_r_g:
        tmp = g.split(',')
        i, j = tmp[0], tmp[2]
        if i not in filter_ind:
            filter_ind.append(i)
        if j not in filter_ind:
            filter_ind.append(j)
    for g in all_c_g:
        i = g.split(',')[1]
        if i not in all_ind:
            all_ind.append(i)
    for g in all_r_g:
        tmp = g.split(',')
        i, j = tmp[0], tmp[2]
        if i not in all_ind:
            all_ind.append(i)
        if j not in all_ind:
            all_ind.append(j)

    '''
        # output importance/effectiveness of each entailment
    for g in filter_c_g:
        print '%s, %f, %f' % (g, imp[g] if g in imp else -1.0, eff[g] if g in eff else -1.0)
    print '%d, %d' % (len(filter_c_g), len(all_c_g))
    print '\n\n'
    for g in filter_r_g:
        print '%s, %f, %f' % (g, imp[g] if g in imp else -1.0, eff[g] if g in eff else -1.0)
    '''


    '''
        # write root individuals to file
    '''
    root_ind_f = open(ROOT_IND_F, 'w')
    for i in filter_ind:
        root_ind_f.write(i + '\n')
    root_ind_f.close()

    print 'class ass. ent.: %d, %d' % (len(filter_c_g), len(all_c_g))
    print 'role ent.: %d, %d' % (len(filter_r_g), len(all_r_g))
    print 'individual: %d, %d' % (len(filter_ind), len(all_ind))
