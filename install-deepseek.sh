#!/bin/bash -l
#SBATCH --job-name=install-deepsk
#SBATCH --output=./p2-output/install-deepsk.%j.out
#SBATCH --error=./p2-output/install-deepsk.%j.err
#SBATCH --partition=ice-gpu       # or an ‘ice-cpu’ partition with large RAM
#SBATCH -N1                        # 1 node
#SBATCH --gres=gpu:1               # request 1 GPU (if you want GPU conversion)
#SBATCH --mem=200G                 # request 200 GB RAM
#SBATCH --time=02:00:00            # up to 2 hours

module load anaconda3
# source activate my_env

# # Option 1: ← initialize conda for non-interactive shells
# # Prepend *your* conda bin to PATH
# export PATH="/storage/ice1/7/1/mong31/scratch/conda3/bin:$PATH"
# eval "$(conda shell.bash hook)"

# Option 2: ← point to the conda.sh file
# ← source the real conda.sh from the conda base
. /storage/ice1/7/1/mong31/conda3/etc/profile.d/conda.sh

# ← now this will succeed
conda activate my_env

# ensure HF token is set if you need to pull from the Hub
export HUGGINGFACE_TOKEN=$(cat ~/scratch/hf-token.env)

# now run your installer
python install-deepseek.py
