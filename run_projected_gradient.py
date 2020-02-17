import torch
import numpy as np
import matplotlib.pyplot as plt

from generate_scripts import get_img_output_path
from generate_scripts import get_info_output_path
from generate_scripts import get_std_output_path

from collections import OrderedDict

from script_utils import get_script_root
from script_utils import get_code_root
from script_utils import get_output_root
from script_utils import get_sbatch_args

from script_utils import Exp
from script_utils import TYPE
from script_utils import lst_dataset, lst_checkpoint, lst_batch_size, lst_num_batch, lst_eps, lst_lr_dualproj as lst_lr, lst_nb_iter, lst_postprocess

exp_name = "projected_gradient"

cmd = "projected_gradient.py"

code_root = get_code_root()
sbatch_args = get_sbatch_args()

script_root = get_script_root(exp_name)
output_root = get_output_root(exp_name)

cmd_args = OrderedDict(dataset=lst_dataset,
                       checkpoint=lst_checkpoint,
                       batch_size=lst_batch_size,
                       num_batch=lst_num_batch,
                       eps=lst_eps,
                       kernel_size=[5],
                       lr=lst_lr,
                       nb_iter=lst_nb_iter,
                       dual_max_iter=[25],
                       grad_tol=[1e-4],
                       int_tol=[1e-4],
                       seed=[0],
                       debug=[1],
                       benchmark=[0],
                       postprocess=lst_postprocess,
                       )

noabbr = [
    "dataset",
    # "checkpoint",
    # "batch_size",
    # "num_batch",
    # "eps",
    # "kernel_size",
    # "lr",
    # "nb_iter",
    "dual_max_iter",
    "grad_tol",
    "int_tol",
    "seed",
    "debug",
    "benchmark",
    # "postprocess",
]

"""
python projected_gradient.py --dataset cifar \
                             --checkpoint cifar_vanilla \
                             --batch_size 50 \
                             --num_batch 1 \
                             --eps 0.01 \
                             --kernel_size None \
                             --lr 0.1 \
                             --nb_iter 100 \
                             --dual_max_iter 25 \
                             --grad_tol 1e-4 \
                             --int_tol 1e-4 \
                             --save_img_loc ./adversarial_examples/projected_gradient.pt \
                             --seed 0 \
                             --debug 0 \
                             --benchmark 0
"""


def collect_results(output_root, print_func):
    pattern = "projected_gradient_checkpoint-{}_batch_size-{}_num_batch-{}_eps-{}_kernel_size-5_lr-{}_nb_iter-{}_postprocess-{}".format(lst_checkpoint[0],
                                                                                                                                        lst_batch_size[0],
                                                                                                                                        lst_num_batch[0],
                                                                                                                                        "{}",
                                                                                                                                        lst_lr[0],
                                                                                                                                        lst_nb_iter[0],
                                                                                                                                        "{}")
    for postprocess in lst_postprocess:
        print("& ", end="")
        for eps in lst_eps:
            script_name = pattern.format(eps, postprocess)

            info_output_path = get_info_output_path(output_root, script_name)
            try:
                acc, run_time, num_iter, func_calls, overflow, converge, lst_acc = torch.load(info_output_path)
            except:
                acc, run_time, num_iter, func_calls, overflow, converge, lst_loss, lst_acc = torch.load(info_output_path)
            # acc, run_time, num_iter, func_calls, overflow, converge, lst_acc = torch.load(info_output_path)

            if lst_eps.index(eps) == 0 and postprocess == 1:
                print("PGD + Dual Proj.                       ", end="")

            if lst_eps.index(eps) == 0 and postprocess == 0:
                print("PGD + Dual Proj. (w/o post-processing) ", end="")

            print_func(acc, num_iter / func_calls, run_time / num_iter)

        print(" \\\\")


def collect_results_converge(output_root, plot_func, plot_acc=True, simple=False):
    pattern = "projected_gradient_checkpoint-{}_batch_size-{}_num_batch-{}_eps-{}_kernel_size-5_lr-{}_nb_iter-{}_postprocess-{}".format(lst_checkpoint[0],
                                                                                                                                        lst_batch_size[0],
                                                                                                                                        lst_num_batch[0],
                                                                                                                                        lst_eps[0],
                                                                                                                                        "{}",
                                                                                                                                        lst_nb_iter[0],
                                                                                                                                        lst_postprocess[0])
    lst_lines = []
    lst_labels = []

    for lr in lst_lr:
        if simple and lr != 0.01:
            continue

        script_name = pattern.format(lr)
        info_output_path = get_info_output_path(output_root, script_name)
        try:
            acc, run_time, num_iter, func_calls, overflow, converge, lst_acc = torch.load(info_output_path)
        except:
            acc, run_time, num_iter, func_calls, overflow, converge, lst_loss, lst_acc = torch.load(info_output_path)

        if TYPE is Exp.IMAGENET_CONVERGE:
            lst_acc = np.array(lst_acc).reshape(2, 300).sum(axis=0)
            lst_loss = np.array(lst_loss).reshape(2, 300).sum(axis=0)

        label = r"dual proj $\eta={}$".format(lr)

        if plot_acc:
            lines = plot_func(lst_acc, label=label, linestyle='-', linewidth=2)
        else:
            lines = plot_func(lst_loss, label=label, linestyle='-', linewidth=2)

        lst_lines += lines
        lst_labels.append(label)

        print(script_name)
        # print(lst_acc)

    return lst_lines, lst_labels
