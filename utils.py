import os

root = "/h/kaiwen/tml2/fast-wasserstein-adversarial/"
# root = "/home/k77wu/vaughan/fast-wasserstein-adversarial/"

sbatch_args = """#!/bin/bash\n
#SBATCH -p p100
#SBATCH --mem=10G
#SBATCH --gres=gpu:1
"""

def get_script_root(exp_name):
    return os.path.join(root, "script", exp_name)


def get_code_root():
    return root


def get_output_root(exp_name):
    return os.path.join(root, "output", exp_name)


def get_sbatch_args():
    return sbatch_args
