import os
import shutil
import itertools

from utils import get_time_stamp
from utils import create_latest_symlink
from utils import get_str_cmd_args
from utils import get_aligned_str
from utils import get_script_name
from utils import get_output_folder
from utils import get_std_output_path
from utils import get_sbatch_args_with_slurm_output_path

root = None
script_root = None
output_root = None

sbatch_args = None

cmd = None
cmd_args = None
named_args = None
other_args = None


def generate_script(overwrite, verbose):
    script_folder = "{}/{}".format(script_root, get_time_stamp())
    os.mkdir(script_folder)

    args = list(cmd_args.keys())
    lsts = [cmd_args[key] for key in cmd_args]

    for vals in itertools.product(*lsts):
        script_name = get_script_name(cmd, args, vals, named_args)

        script_path = "{}/{}.sh".format(script_folder, script_name)

        output_folder = get_output_folder(output_root, script_name)

        if os.path.exists(output_folder):
            if overwrite:
                """CAUTION: existing files in the output folder will be deleted"""
                shutil.rmtree(output_folder)
            else:
                raise Exception("WARNING: existing files in the output folder may be deleted; consider using --overwrite option\nconflict folder: {}".format(output_folder))

        os.mkdir(output_folder)

        std_output_path = get_std_output_path(output_root, script_name)

        str_cmd_args = get_str_cmd_args(args, vals)

        py_cmd = "{} {}".format(cmd, str_cmd_args)
        print(py_cmd)

        for func in other_args:
            str_cmd_args += func(output_folder)

        str_cmd_args = "{} --{}".format(str_cmd_args, std_output_path)

        py_cmd = "{} {}".format(cmd, str_cmd_args)

        content = (
            "{}\n\n".format(get_sbatch_args_with_slurm_output_path(sbatch_args)) +
            "touch %A\n\n" +
            "cd {}\n\n".format(root) +
            get_aligned_str("echo {}\n\n".format(py_cmd), is_echo=True) +
            get_aligned_str("python {}\n\n".format(py_cmd), is_echo=False) +
            "echo 'Job Done!'\n"
        )

        with open(script_path, "w") as f:
            if verbose:
                print(script_name)
            f.write(content)

        create_latest_symlink(script_root, script_folder)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('module_name', type=str)
    parser.add_argument('--overwrite', type=int, default=0)
    parser.add_argument('--verbose', type=int, default=0)

    args = parser.parse_args()

    exec("from {} import *".format(args.module_name[:-3]))

    generate_script(args.overwrite, args.verbose)
