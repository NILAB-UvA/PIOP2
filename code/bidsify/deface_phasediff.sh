set -e
fmaps=$(ls ../sub*/fmap/*phasediff.nii.gz)
for fmap in $fmaps; do 
    echo "Working on $fmap"
    cp $fmap ../../fmap_backup/
    pydeface $fmap --outfile $fmap --force
done
