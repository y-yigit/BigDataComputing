#!/bin/bash
##############################
#        Yaprak Yigit        #
#        Assignment3         #
##############################

# Job name
#SBATCH --job-name=minimap2

# Allow all notifications about the job
#SBATCH --mail-type=ALL
#SBATCH --mail-user=y.yigit@st.hanze.nl
#SBATCH --account=yyigit

# The partition on which the job shall run
#SBATCH --partition=assemblix

# N+1 Threads for Minimap2
#SBATCH --nodes=1
# From 1 to 16
#SBATCH --array=1-16
# --Memory per node 
#SBATCH --mem-per-cpu=1500MB

# How long the job is allowed to run in real time, 
# formatted as d-hh:mm:ss
#SBATCH --time=0-02:00:00

# Source conda so minimap2 is loaded into the environment
source /commons/conda/conda_load.sh

# File locations
index=$( realpath "$0"  ) && /data/dataprocessing/MinIONData/all_bacteria.fna "$index"
data=$( realpath "$0"  ) && /data/dataprocessing/MinIONData/all.fq "$data"

# The output goes to /dev/null
/usr/bin/time -o timings.txt --append -f "${n}\t%e" minimap2 -N "$n"+1 -a $index $data > "/dev/null" 2> log.txt

