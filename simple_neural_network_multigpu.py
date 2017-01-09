#Simple Multilayer Neural Network to seperate pycbc injections from noise triggers
#Author: Hunter Gabbard
#Max Planck Insitute for Gravitational Physics

import argparse
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np
import h5py
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import sys
from math import exp, log
import tensorflow as tf
from keras.callbacks import EarlyStopping

#construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="path to input dataset")
args = vars(ap.parse_args())

#load CBC/noise triggers and identify labels
h1 = h5py.File(args['dataset'], 'r')
marg_l = np.asarray(h1['H1/marg_l'][:]).reshape((h1['H1/marg_l'].shape[0],1))
count = np.asarray(h1['H1/count'][:]).reshape((h1['H1/count'].shape[0],1))
maxnewsnr = np.asarray(h1['H1/maxnewsnr'][:]).reshape((h1['H1/maxnewsnr'].shape[0],1))
maxsnr = np.asarray(h1['H1/maxsnr'][:]).reshape((h1['H1/maxsnr'].shape[0],1))
time = np.asarray(h1['H1/time'][:]).reshape((h1['H1/time'].shape[0],1))
ratio_chirp = np.asarray(h1['H1/ratio_chirp'][:]).reshape((h1['H1/ratio_chirp'].shape[0],1))
delT = np.asarray(h1['H1/delT'][:]).reshape((h1['H1/delT'].shape[0],1))
delta_chirp = np.asarray(h1['H1/delta_chirp'][:]).reshape((h1['H1/delta_chirp'].shape[0],1))


marg_l_inj = np.asarray(h1['H1/marg_l_inj'][:]).reshape((h1['H1/marg_l_inj'].shape[0],1))
count_inj = np.asarray(h1['H1/count_inj'][:]).reshape((h1['H1/count_inj'].shape[0],1))
maxnewsnr_inj = np.asarray(h1['H1/maxnewsnr_inj'][:]).reshape((h1['H1/maxnewsnr_inj'].shape[0],1))
maxsnr_inj = np.asarray(h1['H1/maxsnr_inj'][:]).reshape((h1['H1/maxsnr_inj'].shape[0],1))
time_inj = np.asarray(h1['H1/time_inj'][:]).reshape((h1['H1/time_inj'].shape[0],1))
ratio_chirp_inj = np.asarray(h1['H1/ratio_chirp_inj'][:]).reshape((h1['H1/ratio_chirp_inj'].shape[0],1))
delT_inj = np.asarray(h1['H1/delT_inj'][:]).reshape((h1['H1/delT_inj'].shape[0],1))
delta_chirp_inj = np.asarray(h1['H1/delta_chirp_inj'][:]).reshape((h1['H1/delta_chirp_inj'].shape[0],1))
eff_dist_inj = np.asarray(h1['H1/eff_dist_inj'][:]).reshape((h1['H1/eff_dist_inj'].shape[0],1))


#Applying weights to injections
marg_l_inj_w = []
count_inj_w = []
maxnewsnr_inj_w = []
maxsnr_inj_w = []
time_inj_w = []
eff_dist_inj_w = []
ratio_chirp_inj_w = []
delT_inj_w = []
delta_chirp_inj_w = []

#Need to make a definition out of the below code...
#weight_input = [marg_l_inj, count_inj, maxnewsnr_inj, maxsnr_inj, time_inj, eff_dist_inj]
#weight_name = ['marg_l_inj', 'count_inj', 'maxnewsnr_inj', 'maxsnr_inj', 'time_inj', 'eff_dist_inj']
#weight_output = [marg_l_inj_w, count_inj_w, maxnewsnr_inj_w, maxsnr_inj_w, time_inj_w, eff_dist_inj_w]
#def weight_applier(weight_input, weight_name, weight_output):
#    for stat in enumerate(weight_input):
#        stat_name = weight_name[stat[0]]
#        for idx in enumerate(stat[1]):
#            idx = idx[0]
#            print weight_output[stat[0]][0]
#            weight_output[stat[0]].append(weight_input[idx][0]*((eff_dist_inj[idx][0]**2)/eff_dist_inj.mean()))
#        weight_output[stat[0]] = np.asarray(weight_output[stat[0]]).reshape((h1['H1/%s' % stat_name].shape[0],1))

#weight_applier(weight_input, weight_name, weight_output)


for idx in enumerate(count_inj):
    idx = idx[0]
    count_inj_w.append(count_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
count_inj_w = np.asarray(count_inj_w).reshape((h1['H1/count_inj'].shape[0],1))

for idx in enumerate(marg_l_inj):
    idx = idx[0]
    marg_l_inj_w.append(marg_l_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
marg_l_inj_w = np.asarray(marg_l_inj_w).reshape((h1['H1/marg_l_inj'].shape[0],1))

for idx in enumerate(maxnewsnr_inj):
    idx = idx[0]
    maxnewsnr_inj_w.append(maxnewsnr_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
maxnewsnr_inj_w = np.asarray(maxnewsnr_inj_w).reshape((h1['H1/maxnewsnr_inj'].shape[0],1))

for idx in enumerate(maxsnr_inj):
    idx = idx[0]
    maxsnr_inj_w.append(maxsnr_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
maxsnr_inj_w = np.asarray(maxsnr_inj_w).reshape((h1['H1/maxsnr_inj'].shape[0],1))

for idx in enumerate(ratio_chirp_inj):
    idx = idx[0]
    ratio_chirp_inj_w.append(ratio_chirp_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj[0]**2).mean()))
ratio_chirp_inj_w = np.asarray(ratio_chirp_inj_w).reshape((h1['H1/ratio_chirp_inj'].shape[0],1))

for idx in enumerate(delT_inj):
    idx = idx[0]
    delT_inj_w.append(delT_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
delT_inj_w = np.asarray(delT_inj_w).reshape((h1['H1/delT_inj'].shape[0],1))

inj_weights = []
np.asarray(inj_weights)
for idx in enumerate(delta_chirp_inj):
    idx = idx[0]
    delta_chirp_inj_w.append(delta_chirp_inj[idx][0]*((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
    inj_weights.append(((eff_dist_inj[idx][0]**2)/(eff_dist_inj**2).mean()))
delta_chirp_inj_w = np.asarray(delta_chirp_inj_w).reshape((h1['H1/delta_chirp_inj'].shape[0],1))
inj_weights = np.asarray(inj_weights).reshape((h1['H1/delta_chirp_inj'].shape[0],1))

#combining trigs and inj into one matrix
trig_comb = np.hstack((marg_l, count, maxnewsnr, maxsnr, ratio_chirp, delT))
inj_comb = np.hstack((marg_l_inj_w, count_inj_w, maxnewsnr_inj_w, maxsnr_inj_w, ratio_chirp_inj_w, delT_inj_w))
#inj_comb = np.hstack((marg_l_inj, count_inj, maxnewsnr_inj, maxsnr_inj, ratio_chirp_inj, delT_inj))


indices_trig = np.random.permutation(trig_comb.shape[0])

#The factor of 10 refers to ten times as much background.
trig_train_idx, trig_test_idx = indices_trig[:int(trig_comb.shape[0]*.8)], indices_trig[int(trig_comb.shape[0]*.8):int(trig_comb.shape[0])]
trig_train, trig_test = trig_comb[trig_train_idx,:], trig_comb[trig_test_idx,:]

indices_inj = np.random.permutation(inj_comb.shape[0])
inj_train_idx, inj_test_idx = indices_inj[:int(inj_comb.shape[0]*.8)], indices_inj[int(inj_comb.shape[0]*.8):]
inj_train_weight, inj_test_weight = inj_weights[inj_train_idx,:], inj_weights[inj_test_idx,:]
inj_train, inj_test = inj_comb[inj_train_idx,:], inj_comb[inj_test_idx,:]

comb_all = np.vstack((trig_comb, inj_comb))
train_data = np.vstack((trig_train, inj_train))
test_data = np.vstack((trig_test, inj_test))


#making labels
c_zero = np.zeros((trig_comb.shape[0],1))
c_z_train = c_zero[:int(trig_comb.shape[0]*.8)]
c_z_test = c_zero[int(trig_comb.shape[0]*.8):int(trig_comb.shape[0])]
c_ones = np.ones((int(inj_comb.shape[0]),1))
c_o_train = c_ones[:int(inj_comb.shape[0]*.8)]
c_o_test = c_ones[int(inj_comb.shape[0]*.8):int(inj_comb.shape[0])]
lab_train = np.vstack((c_z_train,c_o_train))
lab_test = np.vstack((c_z_test,c_o_test))
labels_all = np.vstack((c_zero,c_ones))

# define the architecture of the network (sigmoid)
for d in ['/gpu:0', '/gpu:1', '/gpu:2', '/gpu:3', '/gpu:4', '/gpu:5']:
    with tf.device(d):
        model0 = Sequential()
        early_stopping = EarlyStopping(monitor='val_loss', patience=2)
        model0.add(Dense(7, input_dim=trig_comb.shape[1],activation='sigmoid'))
        model0.add(Dense(4, activation='sigmoid'))
        model0.add(Dense(4, activation='sigmoid'))
        model0.add(Dense(4, activation='sigmoid'))
        model0.add(Dense(1, activation='sigmoid'))

    #train the model using SGD
        print("[INFO] compiling model...")
        sgd = SGD(lr=0.01)
        model0.compile(loss="binary_crossentropy", optimizer='rmsprop',
	        metrics=["accuracy"])
        model0.fit(train_data, lab_train, nb_epoch=5, batch_size=32, class_weight = {0: 1/((trig_comb.shape[0]*.8)/(inj_comb.shape[0]*.8)), 1: 1.}, shuffle=True)

# show the accuracy on the testing set
print("[INFO] evaluating on testing set...")
(loss, accuracy) = model0.evaluate(test_data, lab_test,
	batch_size=32, verbose=1)
print("[INFO] loss={:.4f}, accuracy: {:.4f}%".format(loss,
	accuracy * 100))
res_pre = model0.predict(test_data)

model0.summary()

#####################
#Computing ROC Curve#
#####################

n_noise = len(trig_test)
pred_prob = model0.predict_proba(test_data).T[0]
prob_sort_noise = pred_prob[pred_prob[0:n_noise].argsort()][::-1]
prob_sort_inj = pred_prob[pred_prob[n_noise+1:].argsort()][::-1]
prob_sort_injWeight = inj_test_weight.T[0][pred_prob[n_noise+1:].argsort()][::-1]
prob_sort_injNewsnr = inj_test[:,2][pred_prob[n_noise+1:].argsort()][::-1]
prob_sort_noiseNewsnr = trig_test[:,2][pred_prob[0:n_noise].argsort()][::-1]

pred_class = model0.predict_classes(test_data)
class_sort = pred_class[pred_prob[:].argsort()][::-1]

orig_test_labels = lab_test[pred_prob[:].argsort()][::-1]

FAP = []
ROC_w_sum = []
ROC_newsnr_sum = []
np.array(FAP)
np.array(ROC_w_sum)
np.array(ROC_newsnr_sum)

w_sum = 0
newsnr_sum = 0
#Calculating the yaxis and FAP of ROC curve
for idx in range(n_noise):
    #Calculate false alarm probability value
    FAP.append((float(idx+1))/n_noise)
    
    w_sum = prob_sort_injWeight[prob_sort_inj > prob_sort_noise[idx]].sum()
    newsnr_sum = prob_sort_injNewsnr[prob_sort_inj > prob_sort_noise[idx]].sum()
    ROC_w_sum.append(w_sum)
    ROC_newsnr_sum.append(newsnr_sum)


