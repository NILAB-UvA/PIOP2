The PIOP2 dataset is part of the Amsterdam Open MRI Collection (AOMIC), a collection of multimodal (3T) MRI datasets including structural (T1-weighted), diffusion-weighted, and (resting-state and task-based) functional BOLD MRI data, as well as detailed demographics and psychometric variables from a large set of healthy participants.
This dataset contains both raw and preprocessed data (and other "derivatives"), which is available on [Openneuro](https://openneuro.org/datasets/ds002790).
At present, only the raw data is available; we're in the process of uploading the derivatives.

The data is described in detail in [this preprint](ADD LINK TO PREPRINT WHEN AVAILABLE).
In short, raw MRI data is available in `sub-???` directories and the behavioral/psychometric/demographic data can be found in the `participant.tsv` file.
The `participants.json` file contains more information about the variables (columns) in the `participants.tsv` file.

### How to download the data?
The entire dataset, including all derivatives, is very large (~53GB raw data + ~355GB derivatives), so we recommend against downloading everything at once (unless you actually want to use all data, of course).
Instead, you can use the [awscli](https://aws.amazon.com/cli/) tool to programmatically download the relevant files. 
The `awscli` tool can be installed using `pip` (i.e., `pip install awscli`). Now, if you're only interested in the raw T1-weighted scans, you can download *only* those files using the following command:

```
aws s3 sync --no-sign-request s3://openneuro.org/ds002790 /your/ouput/dir --exclude "*" --include "sub-*/anat/*T1w.nii.gz"
```

The `--exclude "*"` part makes sure that all files are ignored except those matching the `--include` filter. 
Similarly, if you'd only want to download the Fmriprep-preprocessed resting-state files in "MNI152NLin2009cAsym" space only, you can use the following command:

```
aws s3 sync --no-sign-request s3://openneuro.org/ds002790 /your/ouput/dir --exclude "*" --include "derivatives/fmriprep/sub-*/func/*task-restingstate*space-MNI*desc-preproc_bold.nii.gz"
```

You can, of course, also download a single file, e.g., the `participants.tsv` file:

```
aws s3 sync --no-sign-request s3://openneuro.org/ds002790 /your/ouput/dir --exclude "*" --include "participants.tsv"
```
