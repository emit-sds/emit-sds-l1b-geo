#!/bin/bash
#
# Simple handler for running a single job out of a list
echo "hi"
echo $(sed "${SLURM_ARRAY_TASK_ID}q;d" $1)
$(sed "${SLURM_ARRAY_TASK_ID}q;d" $1)



