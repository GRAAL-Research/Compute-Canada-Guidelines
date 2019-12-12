#!/bin/bash
#SBATCH --array=1-10                                          # Launch an array of 10 jobs
#SBATCH --account=def-someuser                                # Account with resources
#SBATCH --cpus-per-task=6                                     # Number of CPUs
#SBATCH --gres=gpu:1                                          # Number of GPUs (per node)
#SBATCH --mem=5G                                              # memory (per node)
#SBATCH --time=0-01:30                                        # time (DD-HH:MM)
#SBATCH --mail-user=user@domain                               # Where to email
#SBATCH --mail-type=FAIL                                      # Email when a job fails
#SBATCH --output=/scratch/username/some/folder/%A_%a.out      # Default write output on scratch, to jobID_arrayID.out file

module load python/3.7
virtualenv --no-download $SLURM_TMPDIR/env
source $SLURM_TMPDIR/env/bin/activate
pip install --no-index --upgrade pip

pip install --no-index -r requirements.txt

date
SECONDS=0

# You can access the array ID via $SLURM_ARRAY_TASK_ID

# The $@ transfers all args passed to this bash file to the Python script
# i.e. a call to 'sbatch $sbatch_args this_launcher.sh --arg1=0 --arg2=True'
# will call 'python my_script.py --arg1=0 --arg2=True'
python my_script.py $@

# Utility to show job duration in output file
diff=$SECONDS
echo "$(($diff / 60)) minutes and $(($diff % 60)) seconds elapsed."
date
