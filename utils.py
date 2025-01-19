import os
import datetime
from pathlib import Path

from itertools import product


def unsqueeze_values(d: dict):
    """
    Returns:
        A dictionary. Turn all values of the input dictionary into lists.
    """
    return {
        key: value if isinstance(value, list) else [value]
        for key, value in d.items()
    }


def cartesian_product(d: dict):
    d = unsqueeze_values(d)
    return [dict(zip(d.keys(), c)) for c in product(*d.values())]


def get_time_stamp():
    dt_str = str(datetime.datetime.now())
    ret = dt_str.split()[0] + '-' + dt_str.split()[1].split('.')[0]
    return ret


def create_latest_symlink(target: str):
    """
    Args:
        target: The target foler to link.
    """
    parent = os.path.join(target, os.pardir)

    symlink = Path(os.path.join(parent, "latest"))

    if symlink.exists():
        assert symlink.is_symlink()
        symlink.unlink()

    symlink.symlink_to(os.path.join(parent, target))


def get_str_cmd_args(names, vals):
    model_args = ""
    for name, val in zip(names, vals):
        model_args += "--{} {} ".format(name, val)
    return model_args


def get_aligned_str(str_cmd_args, is_echo):
    ret = ""

    lst = str_cmd_args.split('--')
    assert len(lst) > 3

    ret += "{}--{}\\\n".format(lst[0], lst[1])

    for i in range(2, len(lst) - 1):
        ret += " " * (len(lst[0])) + "--{}\\\n".format(lst[i])

    if is_echo is True:
        ret += "\n"
    else:
        ret += " " * (len(lst[0])) + "> {}".format(lst[-1])

    return ret


def get_script_name(cmd, args, vals, named_args):
    ret = cmd[:-3]
    for arg, val in zip(args, vals):
        if arg in named_args:
            ret += "_{}-{}".format(arg, val)
    return ret


def get_output_folder(output_root, script_name):
    return os.path.join(output_root, script_name)


def get_std_output_path(output_root, script_name):
    output_folder = get_output_folder(output_root, script_name)
    return os.path.join(output_folder, "std.output")


def get_sbatch_args_with_slurm_output_path(sbatch_args):
    return sbatch_args + "#SBATCH -o ../slurm/slurm-%A.out"
