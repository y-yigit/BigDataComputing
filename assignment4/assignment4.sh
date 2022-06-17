#!/bin/bash

# Find the multiple input files first

data_dir=/data/dataprocessing/rnaseq_data/Brazil_Brain/
files= find $data_dir -name '*.fastq' -o -name '*.fastq' 

# assignment4.py returns stdout.write(string)
# find a way to save this output
echo $files | parallel -j 2 --sshloginfile hosts.txt --results outdir "python3 assignment4.py {}" 
