#!/bin/bash
data='test.fa'

parallel --sshloginfile hosts.txt --results outdir python3 assignment4.py $data ::: 1 2 3 4 5 
