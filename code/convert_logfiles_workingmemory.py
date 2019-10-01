import os.path as op
import pandas as pd
import numpy as np
from glob import glob
import numpy as np
import matplotlib.pyplot as plt

p_logs = sorted(glob('../../logs/workingmemory/raw/sub*.log'))
con_mapper = {0: 'null', 1: 'active_nochange', 2: 'active_change', 3: 'passive'}
resp_mapper = {'active_nochange': 2, 'active_change': 1}
resp_rev_mapper = {'active_nochange': 1, 'active_change': 2}

bids_dir = '..'

corrs = []
corrsm = []
for p_log in p_logs:
    sub_id = op.basename(p_log).split('-piopwm')[0]
    if int(sub_id.split('-')[1]) > 105:  # super ugly, but there was an error logging responses from sub-105 and lower
        this_mapper = resp_rev_mapper
    else:
        this_mapper = resp_mapper

    df = pd.read_csv(p_log, skiprows=3, sep='\t')
    pulse_idx = df.loc[df.loc[:, 'Event Type'] == 'Pulse'].index[0]
    df = df.iloc[pulse_idx:, :]
    df = df.loc[:, ['Event Type', 'Code', 'Time']]
    df = df.rename({'Event Type': 'trial_type', 'Time': 'onset'}, axis=1)
    start_task = df.iloc[0, :].loc['onset']
    df.loc[:, 'onset'] = df.loc[:, 'onset'] - start_task
    df = df.loc[df.Code.isin(['1', '2', '3']), :]
    df.onset /= 10000
    df.index = range(df.shape[0])
    
    for i, row in df.iterrows():
        if row['trial_type'] == 'Response':
            tt = 'response'
        else:
            tt = con_mapper[int(row['Code'])]
        df.loc[i, 'trial_type'] = tt

    correct = []
    rt = []
    hand = []
    for i, row in df.iterrows():
        if row['trial_type'] != 'response':
            if i+1 == df.shape[0]:
                rt.append('n/a')
                correct.append('miss')
                hand.append('n/a')
                continue

            nextrow = df.loc[i+1, :]
            hand.append('left' if nextrow['Code'] == '1' else 'right')
            if nextrow['trial_type'] != 'response':
                rt.append('n/a')
                correct.append('miss')
            else:
                rt.append(nextrow['onset'] - row['onset'])
                if row['trial_type'] == 'passive':
                    correct.append('n/a')
                elif int(nextrow['Code']) == this_mapper[row['trial_type']]:
                    correct.append('correct')
                else:
                    correct.append('incorrect')

    df = df.drop(['Code'], axis=1).query("trial_type != 'response'")
    df['response_accuracy'] = correct
    df['response_time'] = rt
    df['response_hand'] = hand
    df['duration'] = 6
    df = df.loc[:, ['onset', 'duration', 'trial_type', 'response_accuracy', 'response_time', 'response_hand']]

    df_np = df.query("trial_type != 'passive'")
    n_corr = (df_np['response_accuracy'] == 'correct').sum()
    n_incorr = (df_np['response_accuracy'] == 'incorrect').sum()
    n_miss = (df_np['response_accuracy'] == 'miss').sum()
    n_tot = df_np.shape[0]

    print(f"prop all = {n_corr / n_tot}, prop non-missed = {n_corr / (n_corr + n_incorr)}")
    corrs.append(n_corr / n_tot)
    corrsm.append(n_corr / (n_corr + n_incorr))
    f_out = f'../../logs/workingmemory/clean/{sub_id}_task-workingmemory_acq-seq_events.tsv'
    df.to_csv(f_out, sep='\t')
    f_out = f'{bids_dir}/{sub_id}/func/{sub_id}_task-workingmemory_acq-seq_events.tsv'
    if op.isdir(op.dirname(f_out)):
        df.to_csv(f_out, sep='\t', index=False)

print(np.mean(corrs))
print(np.nanmean(corrsm))
