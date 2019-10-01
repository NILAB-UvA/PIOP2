import pandas as pd
import os.path as op
from glob import glob
import numpy as np

PULSECODE = 255
base_dir = '../'
logdir = '../../logs/stopsignal/raw'
logs = sorted(glob(op.join(logdir, 'sub*.log')))
txts = sorted(glob(op.join(logdir, 'sub*.txt')))

for log, txt in zip(logs, txts):
    sub_id = op.basename(log)[:8]
    #print(sub_id)
    
    log = pd.read_csv(log, sep='\t', skiprows=3, skip_blank_lines=True)
    log['Code'] = log['Code'].astype(str)
    log['Code'] = [np.float(x) if x.isdigit() else x for x in log['Code']]
    sequence = log['Code'][log['Code'].isin(['vlmr', 'vrml'])].iloc[0]

    if sequence == 'vlmr':
        corr_resp = {'female': 2, 'male': 1}
    else:
        corr_resp = {'female': 1, 'male': 2}

    pulse_idx = np.where(log['Code'] == PULSECODE)[0]

    if len(pulse_idx) > 1:  # take first pulse if mult pulses are logged
        pulse_idx = int(pulse_idx[0])

    pulse_t = log['Time'][log['Code'] == PULSECODE].iloc[0]
    log['Time'] = (log['Time'] - float(pulse_t)) / 10000.0
    log['Duration'] /= 10000.0
    trial_idx = log['Code'].apply(lambda x: x[:2] if isinstance(x, str) else x) == 'D:'
    log_clean = log[trial_idx]
    log_clean = log_clean.drop(['Trial', 'Uncertainty.1', 'TTime', 'Event Type',
                                'Subject', 'Uncertainty',
                                'ReqTime', 'ReqDur', 'Stim Type',
                                'Pair Index'], axis=1)
    log_clean.index = ['Trial_%i' % (i+1) for i in range(log_clean.shape[0])]
    assert(log_clean.shape[0] == 100)

    behav = pd.read_csv(txt, sep='\t', skiprows=1)
    behav.index = ['Trial_%i' % i for i in behav['Trial']]
    behav = behav.drop(['Time', 'Trial', 'miss1', 'P1', 'S_R1', 'ResT'], axis=1)
    merged = pd.concat((log_clean, behav), axis=1)
    assert(merged.shape[0] == log_clean.shape[0] == behav.shape[0])

    bids_file = pd.DataFrame({'onset': merged['Time'],
                              'duration': merged['Duration'],
                              'response_time': merged['RT'] / 1000,
                              'stop_signal_delay': [x / 1000 if x != 99 else 'n/a' for x in merged['SSD1']]},
                             index=merged.index)
    conditions = []
    correct_or_not = []
    gender = [x.split('\\')[-1][0] if isinstance(x, str) else x
              for x in merged['Code']]
    gender = ['female' if s == 'V' else 'male' for s in gender]
    bids_file['gender'] = gender
    bids_file['response_hand'] = ['left' if x == 1 else 'right' for x in merged['Res']]
    for idx in range(merged.shape[0]):

        this_gender = gender[idx]
        this_stop = merged['GoStop'].iloc[idx]
        this_resp = merged['Res'].iloc[idx]

        if this_stop == 0:
            conditions.append('go')
            if this_resp == 0:
                correct_or_not.append('miss')
            elif this_resp == corr_resp[this_gender]:
                correct_or_not.append('correct')
            else:
                correct_or_not.append('incorrect')
        elif this_stop == 1 and this_resp > 0:
            conditions.append('unsuccesful_stop')    
            correct_or_not.append('correct' if corr_resp[this_gender] == this_resp else 'incorrect')
        else:
            conditions.append('succesful_stop')
            correct_or_not.append('n/a')

    bids_file['response_time'] = [rt if rt != 0 else 'n/a' for rt in bids_file['response_time']]
    bids_file['trial_type'] = conditions
    bids_file['response_accuracy'] = correct_or_not
    bids_file = bids_file.loc[:, ['onset', 'duration', 'trial_type', 'stop_signal_delay', 'response_time', 'response_accuracy', 'response_hand', 'gender']]
    succ_stops = np.sum(bids_file['trial_type'] == 'succesful_stop') / np.sum(['stop' in x for x in bids_file['trial_type']])
    
    #fn = op.join('/home/lsnoek1/PIOP2/raw/bids_converted_fieldmap', op.basename(sub), 'func',
    #             op.basename(sub) + '_task-stop_events.tsv')
    #bids_file.to_csv(fn, sep='\t', index=False)

    #mSSD = bids_file['SSD'][bids_file['SSD'] > 0].mean()
    #goRT = bids_file['response_time'][(bids_file['trial_type'] == 'go') & (bids_file['correct_response'] == 1)]
    #goRT = sorted(np.array(goRT.tolist()))
    #p_stop_error = 1 - succ_stops
    #QRT = np.percentile(goRT, p_stop_error*100)
    #SSRT = QRT - mSSD
    fn = f'../../logs/stopsignal/clean/{sub_id}_task-stopsignal_acq-seq_events.tsv'
    bids_file.to_csv(fn, sep='\t', index=False)
    print(f"{sub_id}: {bids_file.shape}")
    if op.isdir(f'../{sub_id}/func'):
        fn = f'../{sub_id}/func/{sub_id}_task-stopsignal_acq-seq_events.tsv'
        bids_file.to_csv(fn, sep='\t', index=False)
