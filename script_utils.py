import os

root = "/h/kaiwen/tml2/fast-wasserstein-adversarial/"
root_local = "/home/k77wu/Desktop/fast-wasserstein-adversarial/"


sbatch_args = """#!/bin/bash\n
#SBATCH -p p100
#SBATCH --mem=10G
#SBATCH --gres=gpu:1
"""

from enum import Enum


class Exp(Enum):
    MNIST_ATTACK = 1
    CIFAR_ATTACK = 2
    IMAGENET_ATTACK = 3

    CIFAR_CONVERGE = 4
    IMAGENET_CONVERGE = 5

enum2str = {
    Exp.MNIST_ATTACK: "MNIST",
    Exp.CIFAR_ATTACK: "CIFAR",
    Exp.IMAGENET_ATTACK: "ImageNet",
}

TYPE = Exp(1)

if TYPE is Exp.MNIST_ATTACK:
    lst_dataset = ["mnist"]
    # lst_checkpoint = ["mnist_vanilla"]
    lst_checkpoint = ["mnist_robust"]

    lst_batch_size = [100]
    lst_num_batch = [100]
    lst_eps = [0.1, 0.2, 0.3, 0.4, 0.5]

    lst_lr_sinkhorn = [1e-1]
    lst_lr_dualproj = [1e-1]

    lst_nb_iter = [300]
    lst_lam = [1000, 1500, 2000]

    lst_entrp_gamma = [1e-3]

    lst_postprocess = [0, 1]

elif TYPE is Exp.CIFAR_ATTACK:
    lst_dataset = ["cifar"]
    # lst_checkpoint = ["cifar_vanilla"]
    lst_checkpoint = ["cifar_adv_training"]

    lst_batch_size = [100]
    lst_num_batch = [100]
    lst_eps = [0.001, 0.002, 0.003, 0.004, 0.005]

    lst_lr_sinkhorn = [1e-1]
    # lst_lr_dualproj = [1e-2]
    lst_lr_dualproj = [2e-2]

    # lst_nb_iter = [300]
    lst_nb_iter = [500]
    # lst_lam = [3000, 10000, 20000, 50000, 100000]
    lst_lam = [3000, 10000, 20000, 100000]

    lst_entrp_gamma = [1e-3]

    lst_postprocess = [0, 1]

elif TYPE is Exp.IMAGENET_ATTACK:
    lst_dataset = ["imagenet"]
    lst_checkpoint = ["imagenet_resnet50"]

    lst_batch_size = [50]
    lst_num_batch = [2]
    # lst_eps = [0.001, 0.002, 0.003, 0.004, 0.005]
    lst_eps = [0.001]
    # lst_eps = [0.003]
    # lst_eps = [0.004]

    lst_lr_sinkhorn = [1e-1]
    lst_lr_dualproj = [1e-2]

    lst_nb_iter = [300]
    # lst_lam = [100000, 200000, 1000000]
    lst_lam = [200000]
    # lst_lam = [100000]
    lst_entrp_gamma = [1e-3]

    lst_postprocess = [0, 1]
    # lst_postprocess = [0]

elif TYPE is Exp.CIFAR_CONVERGE:
    lst_dataset = ["cifar"]
    lst_checkpoint = ["cifar_vanilla"]

    lst_batch_size = [100]
    lst_num_batch = [1]
    lst_eps = [0.005]

    lst_lr_sinkhorn = [1., 1e-1, 1e-2, 1e-3, 5e-4]
    lst_lr_dualproj = [1., 1e-1, 1e-2, 1e-3, 5e-4]

    lst_nb_iter = [300]
    lst_lam = [20000]
    lst_entrp_gamma = [1e-3]

    lst_postprocess = [0]


elif TYPE is Exp.IMAGENET_CONVERGE:
    lst_dataset = ["imagenet"]
    lst_checkpoint = ["imagenet_resnet50"]

    lst_batch_size = [50]
    lst_num_batch = [2]
    lst_eps = [0.005]

    lst_lr_sinkhorn = [1., 1e-1, 1e-2, 1e-3, 5e-4]
    lst_lr_dualproj = [1., 1e-1, 1e-2, 1e-3, 5e-4]

    lst_nb_iter = [300]
    lst_lam = [200000]
    lst_entrp_gamma = [1e-3]

    lst_postprocess = [0]


def get_script_root(exp_name):
    return os.path.join(root, "script", exp_name)


def get_code_root():
    return root


def get_output_root(exp_name):
    return os.path.join(root, "output", exp_name)


def get_sbatch_args():
    return sbatch_args
