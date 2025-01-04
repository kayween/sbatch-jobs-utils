import os
import shutil

from functools import cached_property

import itertools
from itertools import product

from typing import List

import tomlkit

from utils import get_time_stamp
from utils import create_latest_symlink
from utils import get_str_cmd_args
from utils import get_aligned_str
from utils import get_script_name
from utils import get_output_folder
from utils import get_std_output_path
from utils import get_sbatch_args_with_slurm_output_path

from utils import (
    unsqueeze_values,
    cartesian_product,
)


class Run(object):
    """
    A single run of experiment.
    """
    def __init__(self, py_file: str, args_dict: dict, named_args: List, output_folder: str):
        """
        Args:
            py_file: The python file that executes the run.
            args_dict: The argument dictionary that will be passed to py_file.
            named_args: A subset of arguments that are used to create folder names.
        """
        self.py_file = py_file
        self.args_dict = args_dict

        self.named_args = named_args
        self.output_folder = output_folder

    @property
    def save_loc(self):
        return os.path.join(
            self.output_folder,
            # Expand the seed to three digits so that the display is prettier.
            *[
                self.args_dict[key] if key != "seed" else "{:03d}".format(self.args_dict[key])
                for key in self.named_args
            ],
        )

    def to_str(self):
        return " ".join(
            ["python -u {}".format(self.py_file)] +
            ["--{}={}".format(key, value) for key, value in self.args_dict.items()] +
            ["--save_loc={}".format(self.save_loc)] +
            ["> {} 2>&1".format(os.path.join(self.save_loc, "std.out"))]
        )


class Script(object):
    def __init__(self, prologue: str, epilogue: str, runs: List):
        self.prologue = prologue
        self.epilogue = epilogue
        self.runs = runs 

    def add_run(self, run: Run):
        self.runs.append(run)

    def to_str(self):
        return (
            self.prologue + "\n" +
            "\n".join([run.to_str() for run in self.runs]) + "\n" +
            self.epilogue + "\n"
        )

    def write(self, path):
        with open(path, "w") as f:
            f.write(self.to_str())


class ConfigFileParser(object):
    def __init__(self, config_path):
        with open(config_path, 'rb') as f:
            self.config_dict = tomlkit.load(f)

    @property
    def prologue(self):
        return self.config_dict['prologue']

    @property
    def epilogue(self):
        return self.config_dict['epilogue']

    @property
    def py_file(self):
        """
        The python file that 
        """
        return self.config_dict['python']['file']

    @cached_property
    def lst_grouped_args_dicts(self):
        return [
            unsqueeze_values(value) for key, value in self.config_dict['arguments'].items()
            if key.startswith("group")
        ]

    @cached_property
    def shared_args_dict(self):
        if 'shared' in self.config_dict['arguments']:
            # If there is an explicit 'shared' key, then we've found shared arguments
            shared_args_dict = self.config_dict['arguments']['shared']

        else:
            # Otherwise, we collect all arguments that are not grouped arguments
            shared_args_dict = {
                key: value for key, value in self.config_dict['arguments'].items()
                if not key.startswith("group")
            }

        return unsqueeze_values(shared_args_dict)

    @cached_property
    def lst_args_dicts(self):
        """
        Parse the config file and return a list of dictionaries. Each dictionary contains arguments for each run.
        """
        if not self.lst_grouped_args_dicts:
            cartesian_product(self.shared_args_dict)

        lst = []

        for grouped_args_dict in self.lst_grouped_args_dicts:
            # Combine grouped arguments and shared arguments and then do a Cartesian product
            combined_args_dict = dict(**grouped_args_dict, **self.shared_args_dict)

            lst += cartesian_product(combined_args_dict)

        return lst

    @property
    def named_args(self):
        return self.config_dict['io']['named_args']


def main(config_path: str, num_scripts: int = 0):
    """
    Args:
        config_path: Path to the config file.
        num_scripts: Number of bash scripts to generate.
    """
    # Do parsing first---the program terminates immediately if parsing fails
    parser = ConfigFileParser(config_path)
    _ = parser.lst_args_dicts

    time_stamp = get_time_stamp()
    current_folder = os.path.dirname(os.path.realpath(__file__))

    # Dumping scripts to ./scripts
    scripts_folder = os.path.join(current_folder, "scripts", time_stamp)
    os.mkdir(scripts_folder)
    create_latest_symlink(scripts_folder)

    # Dumping experimental results to ./experiments
    output_folder = os.path.join(current_folder, "experiments", time_stamp)
    os.mkdir(output_folder)
    create_latest_symlink(output_folder)

    lst_runs = [
        Run(parser.py_file, args_dict, parser.named_args, output_folder)
        for args_dict in parser.lst_args_dicts
    ]

    lst_scripts = [
        Script(parser.prologue, parser.epilogue, [])
        for i in range(num_scripts)
    ]

    for run in lst_runs:
        # TODO: Make it less awkward
        idx = run.args_dict['seed'] % num_scripts
        lst_scripts[idx].add_run(run)

        os.makedirs(run.save_loc)

    for i, script in enumerate(lst_scripts):
        script.write(os.path.join(scripts_folder, "{:d}.sh".format(i)))


def generate_scripts(cmd, args):
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
    import fire
    fire.Fire(main)
