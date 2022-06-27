#!/bin/bash
##############################
#        Yaprak Yigit        #
#        Assignment3         #
##############################

#SBATCH --partition=assemblix

#SBATCH --job-name=minimap2
#SBATCH --mail-type=ALL
#SBATCH --mail-user=y.yigit@st.hanze.nl
#SBATCH --account=yyigit

#SBATCH --nodes=1
# Run the job for max 4 hours
#SBATCH --time=0-04:00:00
# For minimap 2 N+1 threads
#SBATCH --cpus-per-task=17
#SBATCH --mem-per-cpu=4500MB

# Source conda so minimap2 is loaded into the environment
source /commons/conda/conda_load.sh

# Data I tested on
index=../Data/reference.fa
data=../Data/sequence.fa

# Actual file locations
#index=/data/dataprocessing/MinIONData/all_bacteria.fna
#data=/data/dataprocessing/MinIONData/all.fq

# For loop to generate time for each CPU
# -t is the amount of CPU's 
# -a will map the reference and sequence to SAM format
for ((n = 1; n <= 16; n++)); do
    /usr/bin/time -o timings.txt --append -f "${n}\t%e" minimap2 -t $n+1 -a $index $data > "/dev/null" 2> log.txt
done
