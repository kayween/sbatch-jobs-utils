
remote_root = "/h/kaiwen/tml2/fast-wasserstein-adversarial/"
local_root = "/home/k77wu/Desktop/fast-wasserstein-adversarial/"
# local_root = "/home/k77wu/fast-wasserstein-adversarial/"
# local_root = "/h/kaiwen/tml2/fast-wasserstein-adversarial/"

sbatch_args = """#!/bin/bash\n
#SBATCH -p p100
#SBATCH --mem=10G
#SBATCH --gres=gpu:1
"""
