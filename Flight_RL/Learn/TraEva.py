#! /usr/bin/python

import tensorflow as tf
import numpy as np
import os
import time
import sys

from sklearn import metrics


'''
hard transfer (ht): 
    in TD: 
        1. load CNN from SD (CNN_SD)
        2. calculate representations (Tr_R_X, Te_R_X) with CNN_SD (3rd conv layer)
        3. fine tune the FC layers with (Tr_R_X, Tr_D_Y)
        4. test with (Te_R_X, Te_D_Y), get Performance_HT
        5. performance_gain: Performance_HT - Performance_Local
'''


def hard_transfer():
    print 'Step 1: load SD CNN'
    saver = tf.train.import_meta_graph(os.path.join(os.path.join(DIR, SD), 'CNN.ckpt.meta'))
    X_ = tf.get_collection("X_")[0]
    h_pool3_reshape = tf.get_collection("h_pool3_reshape")[0]
    keep_prob = tf.get_collection("keep_prob")[0]

    print 'Step 2: calculate representations'
    with tf.Session(config=tf.ConfigProto(intra_op_parallelism_threads=THREAD_NUM)) as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        saver.restore(sess, os.path.join(os.path.join(DIR, SD), 'CNN.ckpt'))
        Tr_R_X = sess.run(h_pool3_reshape,
                          feed_dict={X_: Tr_D_X.reshape(Tr_D_X.shape + (1, 1)), keep_prob: DROPOUT_PROB})
        Te_R_X = sess.run(h_pool3_reshape,
                          feed_dict={X_: Te_D_X.reshape(Te_D_X.shape + (1, 1)), keep_prob: DROPOUT_PROB})

    print 'Step 3 & Step 4: fine tune the FC layer and test'
    R_n = Tr_R_X.shape[1]
    R_X_ = tf.placeholder("float", [None, R_n])
    R_Y_ = tf.placeholder("float", [None, CLASS])

    ## FC4: fully connected, dropout
    R_W_fc4 = tf.Variable(tf.truncated_normal([R_n, 128], stddev=0.1))
    R_b_fc4 = tf.Variable(tf.constant(0.1, shape=[128]))
    R_h_fc4 = tf.matmul(R_X_, R_W_fc4) + R_b_fc4
    R_keep_prob = tf.placeholder(tf.float32)
    R_h_fc4_drop = tf.nn.dropout(R_h_fc4, R_keep_prob)

    ## FC5: readout layer
    R_W_fc4 = tf.Variable(tf.truncated_normal([128, CLASS], stddev=0.1))
    R_b_fc4 = tf.Variable(tf.constant(0.1, shape=[CLASS]))
    R_y_conv = tf.nn.xw_plus_b(R_h_fc4_drop, R_W_fc4, R_b_fc4)

    ## loss
    R_cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=R_Y_, logits=R_y_conv))
    R_train_step = tf.train.AdamOptimizer(1e-4).minimize(R_cross_entropy)

    test_results = []
    start_time = time.time()
    with tf.Session(config=tf.ConfigProto(intra_op_parallelism_threads=THREAD_NUM)) as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        for e in range(EPOCH_NUM):
            ran = get_batch(Tr_R_X.shape[0], e)
            R_train_step.run(session=sess, feed_dict={R_X_: Tr_R_X[ran], R_Y_: Tr_D_Y[ran], R_keep_prob: DROPOUT_PROB})
            if e % 100 == 0 or e == EPOCH_NUM - 1:
                tr_label_p, tr_score_p = sess.run([tf.argmax(R_y_conv, 1), tf.nn.softmax(R_y_conv)[:, 1]],
                                                  feed_dict={R_X_: Tr_R_X, R_keep_prob: DROPOUT_PROB})
                tr_label = np.argmax(Tr_D_Y, 1)
                tr_acc, tr_auc = metrics.accuracy_score(tr_label, tr_label_p), metrics.roc_auc_score(tr_label,
                                                                                                     tr_score_p)
                print 'epoch %d, training accuracy: %f, AUC: %f' % (e, tr_acc, tr_auc)

                te_label_p, te_score_p = sess.run([tf.argmax(R_y_conv, 1), tf.nn.softmax(R_y_conv)[:, 1]],
                                                  feed_dict={R_X_: Te_R_X, R_keep_prob: DROPOUT_PROB})
                te_label = np.argmax(Te_D_Y, 1)
                te_acc, te_auc = metrics.accuracy_score(te_label, te_label_p), metrics.roc_auc_score(te_label,
                                                                                                     te_score_p)
                print 'epoch %d, testing accuracy: %f, AUC: %f \n' % (e, te_acc, te_auc)
                test_results.append([te_acc, te_auc])
    print "time spent: %s seconds\n" % (time.time() - start_time)

    print 'Step 5: compare testing performance'
    test_res = np.array(test_results)
    auc_order_index = np.argsort(-test_res[:, 1], axis=0)
    ht_test_res = test_res[auc_order_index][0:TOP_K]
    np.save(os.path.join(HT_DIR, '%s-%s' % (SD, TD)), ht_test_res)
    ht_gap = np.average(ht_test_res, axis=0) - np.average(local_test_res, axis=0)
    print 'testing accuracy gap: %f, AUC gap: %f' % (ht_gap[0], ht_gap[1])
    np.save(os.path.join(HT_DIR, '%s-%s-gap' % (SD, TD)), ht_gap)


'''
soft transfer (st): 
    in TD: 
        1. load CNN from SD (CNN_SD)
        2. fine tune all the layers of CNN_SD with TD_Tr
        3. test with TD test data (TD_Te), get Performance_ST
        4. performance_gain: Performance_ST - Performance_Local
'''


def soft_transfer():
    print 'Step 1: load SD CNN'
    saver = tf.train.import_meta_graph(os.path.join(os.path.join(DIR, SD), 'CNN.ckpt.meta'))
    X_ = tf.get_collection("X_")[0]
    Y_ = tf.get_collection("Y_")[0]
    y_conv = tf.get_collection("y_conv")[0]
    train_step = tf.get_collection("train_step")[0]
    keep_prob = tf.get_collection("keep_prob")[0]

    print 'Step 2 & Step 3: fine tune CNN with (Tr_D_X, Tr_D_Y), test CNN'
    test_results = []
    start_time = time.time()
    with tf.Session(config=tf.ConfigProto(intra_op_parallelism_threads=THREAD_NUM)) as sess:
        saver.restore(sess, os.path.join(os.path.join(DIR, SD), 'CNN.ckpt'))
        for e in range(EPOCH_NUM):
            ran = get_batch(Tr_D_X.shape[0], e)
            train_step.run(session=sess,
                           feed_dict={X_: Tr_D_X[ran].reshape(Tr_D_X[ran].shape + (1, 1)), Y_: Tr_D_Y[ran],
                                      keep_prob: DROPOUT_PROB})
            if e % 100 == 0 or e == EPOCH_NUM - 1:
                tr_label_p, tr_score_p = sess.run([tf.argmax(y_conv, 1), tf.nn.softmax(y_conv)[:, 1]],
                                                  feed_dict={X_: Tr_D_X.reshape(Tr_D_X.shape + (1, 1)), Y_: Tr_D_Y,
                                                             keep_prob: DROPOUT_PROB})
                tr_label = np.argmax(Tr_D_Y, 1)
                tr_acc, tr_auc = metrics.accuracy_score(tr_label, tr_label_p), metrics.roc_auc_score(tr_label,
                                                                                                     tr_score_p)
                print 'epoch %d, training accuracy: %f, AUC: %f' % (e, tr_acc, tr_auc)

                te_label_p, te_score_p = sess.run([tf.argmax(y_conv, 1), tf.nn.softmax(y_conv)[:, 1]],
                                                  feed_dict={X_: Te_D_X.reshape(Te_D_X.shape + (1, 1)), Y_: Te_D_Y,
                                                             keep_prob: DROPOUT_PROB})
                te_label = np.argmax(Te_D_Y, 1)
                te_acc, te_auc = metrics.accuracy_score(te_label, te_label_p), metrics.roc_auc_score(te_label,
                                                                                                     te_score_p)
                print 'epoch %d, testing accuracy: %f, AUC: %f \n' % (e, te_acc, te_auc)
                test_results.append([te_acc, te_auc])
    print "time spent: %s seconds\n" % (time.time() - start_time)

    print 'Step 4: compare testing performance'
    test_res = np.array(test_results)
    auc_order_index = np.argsort(-test_res[:, 1], axis=0)
    st_test_res = test_res[auc_order_index][0:TOP_K]
    np.save(os.path.join(ST_DIR, '%s-%s' % (SD, TD)), st_test_res)
    st_gap = np.average(st_test_res, axis=0) - np.average(local_test_res, axis=0)
    print 'testing accuracy gap: %f, AUC gap: %f' % (st_gap[0], st_gap[1])
    np.save(os.path.join(ST_DIR, '%s-%s-gap' % (SD, TD)), st_gap)


def get_batch(size, e):
    if size % BATCH_SIZE == 0:
        m = size / BATCH_SIZE
        bottom, top = e % m * BATCH_SIZE, e % m * BATCH_SIZE + BATCH_SIZE
    else:
        m = size / BATCH_SIZE + 1
        bottom = e % m * BATCH_SIZE
        if bottom + BATCH_SIZE > size:
            top = size
        else:
            top = bottom + BATCH_SIZE
    return range(bottom, top)


CLASS = 2
TOP_K = 7
DROPOUT_PROB = 0.8

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_DEVICE_ORDER'] = 'PCI_BUS_ID'
os.environ['CUDA_VISIBLE_DEVICES'] = '0'

'''
## run one domain transfer for debug in IDE 
SD = 'AA_JFK_LAX_1500_1759'
TD = 'DL_JFK_LAX_1500_1759'
DIR = 'your_home_dir/Sample'

THREAD_NUM = 2
EPOCH_NUM = 1500
BATCH_SIZE = 100
# '''


# '''
## parameters settings, used in command line
EPOCH_NUM, BATCH_SIZE, THREAD_NUM = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
DIR, SD, TD = sys.argv[4], sys.argv[5], sys.argv[6]
OPTION = sys.argv[7]
# '''

data_dir = os.path.join(DIR, TD)
Tr_D_X = np.load(os.path.join(data_dir, 'Tr_D_X.npy'))
Tr_D_Y = np.load(os.path.join(data_dir, 'Tr_D_Y.npy'))
Te_D_X = np.load(os.path.join(data_dir, 'Te_D_X.npy'))
Te_D_Y = np.load(os.path.join(data_dir, 'Te_D_Y.npy'))
local_test_res = np.load(os.path.join(data_dir, 'local_test_res.npy'))

if OPTION == 'H':
    print '\n\n##### HARD TRANSFER:  %s  to  %s ####\n\n' % (SD, TD)
    print 'hard transfer ...'
    HT_DIR = os.path.join(DIR, '../HT_Result')
    if not os.path.exists(HT_DIR):
        os.mkdir(HT_DIR)
    hard_transfer()
elif OPTION == 'S':
    print '\n\n##### SOFT TRANSFER:  %s  to  %s ####\n\n' % (SD, TD)
    ST_DIR = os.path.join(DIR, '../ST_Result')
    if not os.path.exists(ST_DIR):
        os.mkdir(ST_DIR)
    soft_transfer()



