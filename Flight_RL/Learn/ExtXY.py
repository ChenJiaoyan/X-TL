#! /usr/bin/python
import pymysql
import csv
import os
import numpy as np

# Usage: (1) extract original X and y series, (2) partition samples into training and testing sets

# Parameters:
#   types of X: N1, N2, N3, N4, N5
#   cutting_time between training and testing: c_time
#   forecasting time: f_period


'''
ori = 'JFK', ori_nebs = ['LGA', 'EWR', 'PHL']
ori = 'EWR', ori_i_nebs = ['LGA', 'JFK', 'PHL']
ori = 'ORD', ornebs = ['MDW', 'MKE', 'DTW']
ori = 'ATL', ori_nebs = ['CLT', 'SAV', 'BNA']
ori = 'LAX', ori_nebs = ['BUR', 'SNA', 'SAN']
ori = 'SFO', ori_nebs = ['OAK', 'SJC', 'SMF']
ori = 'DFW', ori_nebs = ['OKC', 'AUS', 'IAH']
ori = 'CLT', ori_nebs = ['ATL', 'RDU', 'CHS']
'''

car = 'DL'
ori = 'JFK'
des = 'LAX'
ori_nebs = ['LGA', 'EWR', 'PHL']

CRS_dep_t1 = '1500'
CRS_dep_t2 = '1759'
year1, year2 = 2010, 2017
# predict_t = '1500'
predict_t = CRS_dep_t1

N1, N2, N3, N4, N5 = 20, 5, 10, 5, 15

HOME_DIR = 'your_home_dir/Sample/'

#'''
## parameters settings, used in command line
import sys
car, ori, des = sys.argv[1], sys.argv[2], sys.argv[3]
ori_nebs = sys.argv[4:7]
CRS_dep_t1, CRS_dep_t2 = sys.argv[7], sys.argv[8]
HOME_DIR = sys.argv[9]
#'''

DIR = os.path.join(HOME_DIR, '%s_%s_%s_%s_%s' % (car, ori, des, CRS_dep_t1, CRS_dep_t2))
if not os.path.exists(DIR):
    os.mkdir(DIR)


def exe_sel_sql(sql):
    connection = pymysql.connect(host='116.62.18.214', user='jiaoyan', passwd='123456',
                                 db='flight', cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    return data


def write_csv(lines, f_name):
    f = open(os.path.join(DIR, f_name), 'wb')
    writer = csv.writer(f)
    writer.writerows(lines)
    f.close()


#################### y DepDelay time-series begin######################
header = ['Carrier', 'FlightNum', 'FlightDate', 'CRSDepTime', 'DepDelay']
rows = [header]
for y in range(year1, year2 + 1):
    sql_y = "select Carrier,FlightNum,FlightDate,CRSDepTime,DepDelay " \
            "from flight.flight_%d where Carrier='%s'  and Origin='%s' and Dest='%s' " \
            "and CRSDepTime >= '%s' and CRSDepTime <= '%s' order by FlightDate,CRSDepTime" \
            % (y, car, ori, des, CRS_dep_t1, CRS_dep_t2)
    print 'query y for %d ...' % y
    records_y = exe_sel_sql(sql_y)
    for rec in records_y:
        row = [rec['Carrier'], rec['FlightNum'], rec['FlightDate'], rec['CRSDepTime'], rec['DepDelay']]
        rows.append(row)
write_csv(rows, 'y.csv')
print 'y saved'
#################### end ######################

f = open(os.path.join(DIR, 'y.csv'), 'r')
reader = csv.DictReader(f)
ids = [[row['FlightNum'], row['FlightDate']] for row in reader]
f.close()

################# X1: Mete at origin start ################
met_atts = ['temperature', 'dewPoint', 'visibility', 'humidity', 'cloudCover', 'pressure', 'windSpeed', 'windBearing']
header = ['FlightNum', 'FlightDate'] + met_atts
rows = [header]
sql_X1 = "select * from flight.mete where airport = '%s' and hour like '____-__-__T%s' order by hour" % (
    ori, predict_t[0:2])
print 'query X1 ...'
records_x1 = exe_sel_sql(sql_X1)
d_met = {}
for rec in records_x1:
    d = rec['hour'][0:10]
    met = []
    for h in met_atts:
        met.append(rec[h])
    d_met[d] = met
for i in ids:
    col_num = len(met_atts)
    cols = d_met[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X1.csv')
print 'X1 saved'
################# end ################

################# X2: DepDelay of latest N1 flights at origin start #######################
header = ['FlightNum', 'FlightDate'] + ['Origin_Del' + str(i + 1) for i in range(N1)]
rows = [header]
d_del = {}
for y in range(year1, year2 + 1):
    sql_X2 = "select FlightDate,CRSDepTime,DepDelay,Cancelled from flight.flight_%d " \
             "where Origin='%s' and CRSDepTime<='%s' and CRSDepTime > '%.2d00' " \
             "order by FlightDate,CRSDepTime desc" % (y, ori, predict_t, int(predict_t[0:2]) - 5)
    print 'query X2 for %d ...' % y
    records_X2 = exe_sel_sql(sql_X2)
    for rec in records_X2:
        d = rec['FlightDate']
        delay = rec['DepDelay'] if float(rec['Cancelled']) == 0 else '1440'
        if d in d_del:
            if len(d_del[d]) < N1:
                d_del[d].append(delay)
        else:
            d_del[d] = [delay]
for i in ids:
    col_num = N1
    cols = d_del[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X2.csv')
print 'X2 saved'
################# end ################

################# X3: DepDelay of latest N2 flights of the carrier at origin start #######################
header = ['FlightNum', 'FlightDate'] + ['Carrier_Origin_Del' + str(i + 1) for i in range(N2)]
rows = [header]
d_del = {}
for y in range(year1, year2 + 1):
    sql_X3 = "select Carrier,FlightNum,Origin,Dest,FlightDate,CRSDepTime,DepDelay,Cancelled from flight.flight_%d " \
             "where Origin='%s' and Carrier='%s' and CRSDepTime<='%s' order by FlightDate,CRSDepTime desc" \
             % (y, ori, car, predict_t)
    print 'query X3 for %d ...' % y
    records_X3 = exe_sel_sql(sql_X3)
    for rec in records_X3:
        d = rec['FlightDate']
        delay = rec['DepDelay'] if float(rec['Cancelled']) == 0 else '1440'
        if d in d_del:
            if len(d_del[d]) < N2:
                d_del[d].append(delay)
        else:
            d_del[d] = [delay]
for i in ids:
    col_num = N2
    cols = d_del[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X3.csv')
print 'X3 saved'
################# end ################

################# X4: DepDelay of latest N3 flights of the carrier start #######################
header = ['FlightNum', 'FlightDate'] + ['Carrier_Del' + str(i + 1) for i in range(N3)]
rows = [header]
d_del = {}
for y in range(year1, year2 + 1):
    sql_X4 = "select Carrier,FlightNum,Origin,Dest,FlightDate,CRSDepTime,DepDelay,Cancelled from flight.flight_%d " \
             "where Carrier='%s' and CRSDepTime<='%s' and CRSDepTime > '%.2d00' order by FlightDate,CRSDepTime desc" \
             % (y, car, predict_t, int(predict_t[0:2]) - 4)
    print 'query X4 for %d ...' % y
    records_X4 = exe_sel_sql(sql_X4)
    for rec in records_X4:
        d = rec['FlightDate']
        delay = rec['DepDelay'] if float(rec['Cancelled']) == 0 else '1440'
        if d in d_del:
            if len(d_del[d]) < N3:
                d_del[d].append(delay)
        else:
            d_del[d] = [delay]
for i in ids:
    col_num = N3
    cols = d_del[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X4.csv')
print 'X4 saved'
################# end ################

################# X5: DepDelay of latest N4 flights at each of origin's neighbouring airports start ################
header = ['FlightNum', 'FlightDate']
for neb in ori_nebs:
    header += ['Origin_' + neb + '_Del' + str(i + 1) for i in range(N4)]
rows = [header]
d_del = {}
for y in range(year1, year2 + 1):
    for i, neb in enumerate(ori_nebs):
        sql_X5 = "select FlightDate,CRSDepTime,DepDelay,Cancelled from flight.flight_%d " \
                 "where Origin='%s' and CRSDepTime<='%s' and CRSDepTime > '%.2d00' " \
                 "order by FlightDate,CRSDepTime desc" % (y, neb, predict_t, int(predict_t[0:2]) - 5)
        print 'query X5 for %d and %s ...' % (y, neb)
        records_X5 = exe_sel_sql(sql_X5)
        for rec in records_X5:
            d = rec['FlightDate']
            delay = rec['DepDelay'] if float(rec['Cancelled']) == 0 else '1440'
            if d in d_del:
                if len(d_del[d]) < (i + 1) * N4:
                    d_del[d].append(delay)
            else:
                d_del[d] = [delay]
for i in ids:
    col_num = N4 * len(ori_nebs)
    cols = d_del[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X5.csv')
################# end ################

################# X6: ArrDelay of latest N5 flights at destination start #####################
header = ['FlightNum', 'FlightDate'] + ['Dest_Del' + str(i + 1) for i in range(N5)]
rows = [header]
d_del = {}
for y in range(year1, year2 + 1):
    sql_X6 = "select FlightDate,CRSArrTime,ArrDelay,Cancelled from flight.flight_%d " \
             "where Dest='%s' and CRSArrTime<='%s' and CRSArrTime > '%.2d00' " \
             "order by FlightDate,CRSArrTime desc" % (y, des, predict_t, int(predict_t[0:2]) - 4)
    print 'query X6 for %d ...' % y
    records_X6 = exe_sel_sql(sql_X6)
    for rec in records_X6:
        d = rec['FlightDate']
        delay = rec['ArrDelay'] if float(rec['Cancelled']) == 0 else '1440'
        if d in d_del:
            if len(d_del[d]) < N5:
                d_del[d].append(delay)
        else:
            d_del[d] = [delay]
for i in ids:
    col_num = N5
    cols = d_del[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X6.csv')
################# end ################


################# X7: Mete at destination start ################
met_atts = ['temperature', 'dewPoint', 'visibility', 'humidity', 'cloudCover', 'pressure', 'windSpeed', 'windBearing']
header = ['FlightNum', 'FlightDate'] + met_atts
rows = [header]
sql_X7 = "select * from flight.mete where airport = '%s' and hour like '____-__-__T%s' order by hour" % (
    des, predict_t[0:2])
print 'query X7 ...'
records_x7 = exe_sel_sql(sql_X7)
d_met = {}
for rec in records_x7:
    d = rec['hour'][0:10]
    met = []
    for h in met_atts:
        met.append(rec[h])
    d_met[d] = met
for i in ids:
    col_num = len(met_atts)
    cols = d_met[i[1]]
    if len(cols) < col_num:
        cols += [''] * (col_num - len(cols))
    row = i + cols
    rows.append(row)
write_csv(rows, 'X7.csv')
print 'X7 saved'
################# end ################

################ Merge Samples Start ########################
X_fs = ['X1.csv', 'X2.csv', 'X3.csv', 'X4.csv', 'X5.csv', 'X6.csv', 'X7.csv']
y_f = 'y.csv'
f = open(os.path.join(DIR, y_f), 'rb')
r = csv.DictReader(f)
delay_label = [float('NaN') if row['DepDelay'] == '' else float(row['DepDelay']) > 0 for row in r]
y = np.array(delay_label, dtype=float)
f.close()

D = y.reshape((y.shape[0], 1))
for X_f in X_fs:
    f = open(os.path.join(DIR, X_f), 'rb')
    r = csv.reader(f)
    next(r)
    X_floats = []
    for i, row in enumerate(r):
        X_floats.append([float('NaN') if item == '' else float(item) for item in row[2:]])
    X_arr = np.array(X_floats, dtype=float)
    D = np.concatenate((D, X_arr), axis=1)
    f.close()

D_nan = np.isnan(D)
D_not_nan_i = np.where(D_nan[:, 0] == False)
D = D[D_not_nan_i]
np.save(os.path.join(DIR, 'D'), D)
print 'D.npy saved'
################ end ########################
