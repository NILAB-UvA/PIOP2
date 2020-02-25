import numpy as np 
import nibabel as nib
import json

N_SLICES = 36
TR = 2
slicetimes = np.linspace(0, TR - TR / N_SLICES, N_SLICES).round(4).tolist()

wfs_hz =  434.214
wfs_ppm = 12
sense_acc = 2
npe = 80

ees = wfs_ppm / (wfs_hz * (npe / sense_acc))
trt = ees * (npe / sense_acc - 1)

info = dict(
    EffectiveEchoSpacing=ees,
    TotalReadoutTime=trt,
    SliceTiming=slicetimes
)

for task in ['stopsignal', 'workingmemory', 'emorecognition', 'restingstate']:
    f_out = f'../task-{task}_acq-seq_bold.json'
    with open(f_out, 'w') as f:
        json.dump(info, f, indent=4)


# dwi stuff
npe = 112
wfs_ppm = 18.927
ees = wfs_ppm / (wfs_hz * (npe / sense_acc))
trt = ees * (npe / sense_acc - 1)

info = dict(
    EffectiveEchoSpacing=ees,
    TotalReadoutTime=trt
)

f_out = f'../acq-32b1000_dwi.json'
with open(f_out, 'w') as f:
    json.dump(info, f, indent=4)

#ees_spi = (wfs_ppm / (wfs_hz * npe)) / acc
# 1/(BandwidthPerPixelPhaseEncode * MatrixSizePhase)
#print(1 / (37.8 * 40))
