#!/bin/bash
#SBATCH --job-name=deepseek_test    # Job name
#SBATCH --output=dp%j.out    # Standard output file
#SBATCH --error=dp%j.err     # Error file
#SBATCH --partition=ice-gpu         # Partition name (check with 'sinfo' if needed)
#SBATCH -N1 --gres=gpu:1       # Request 1 GPU
#SBATCH --cpus-per-task=4           # Request 4 CPU cores
#SBATCH --mem=16G                   # Request 16GB RAM
#SBATCH --time=01:00:00             # Max job runtime (hh:mm:ss)
#SBATCH --mail-type=END,FAIL        # Email notification (optional)
#SBATCH --mail-user=ychauhan9@gatech.edu  # Replace with your email

# Load necessary modules (modify as per your HPC environment)
module load anaconda3  # If Conda is available
source activate my_env  # Activate your Conda environment

export HUGGINGFACE_TOKEN=$(cat /home/hice1/ychauhan9/scratch/hgtoken.env)

# Run the DeepSeek Python script
python deepseek_test.py