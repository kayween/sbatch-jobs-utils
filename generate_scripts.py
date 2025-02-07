import os
from typing import List
from functools import cached_property

import tomlkit

from utils import (
    get_time_stamp,
    create_latest_symlink,
    cartesian_product,
)


class Run(object):
    """
    A single run of experiment.
    """
    def __init__(
        self,
        cmd: str,
        args_dict: dict,
        output_root_folder: str,
        fmt: str,
        named_args: List,
    ):
        """
        Args:
            cmd: The python command to execute.
            args_dict: The argument dictionary that will be passed to the python command.
            output_root_folder: A string that determines the output path.
            fmt: The format string that determines the output path.
            named_args: A subset of arguments that are used to create folder names.

        """
        self.cmd = cmd
        self.args_dict = args_dict

        self.output_root_folder = output_root_folder
        self.fmt = fmt
        self.named_args = named_args

    @property
    def output_path(self):
        return os.path.join(
            self.output_root_folder,
            self.fmt.format(*[self.args_dict[key] for key in self.named_args]),
        )

    def to_str(self, use_line_break=True):
        separator = " \\\n    " if use_line_break else " "
        return separator.join(
            [self.cmd] +
            ["--{}={}".format(key, value) for key, value in self.args_dict.items()] +
            ["--output_path={}".format(self.output_path)] +
            ["             >{} 2>&1".format(os.path.join(self.output_path, "std.out"))]
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
            self.prologue +
            "\n\n" +
            "\n\n".join(
                [
                    "echo {}\n{}".format(run.to_str(use_line_break=False), run.to_str(use_line_break=True))
                    for run in self.runs
                ]
            ) +
            "\n\n" +
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
    def cmd(self):
        """
        The python command.
        """
        return self.config_dict['cmd']

    @cached_property
    def lst_grouped_args_dicts(self):
        return self.config_dict['grouped_arguments'] if hasattr(self.config_dict, 'grouped_arguments') else []

    @cached_property
    def shared_args_dict(self):
        return self.config_dict['arguments']

    @cached_property
    def lst_args_dicts(self):
        """
        Parse the config file and return a list of dictionaries. Each dictionary contains arguments for each run.
        """
        if not self.lst_grouped_args_dicts:
            return cartesian_product(self.shared_args_dict)

        lst = []

        for grouped_args_dict in self.lst_grouped_args_dicts:
            # Combine grouped arguments and shared arguments and then do a Cartesian product
            combined_args_dict = dict(**grouped_args_dict, **self.shared_args_dict)

            lst += cartesian_product(combined_args_dict)

        return lst

    @property
    def fmt(self):
        return self.config_dict['io']['format']

    @property
    def named_args(self):
        return self.config_dict['io']['named_args']

    @property
    def ordering(self):
        return self.config_dict['ordering']


def main(config_path: str, num_scripts: int = 1, symlink: bool = True):
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
    scripts_root_folder = os.path.join(current_folder, "scripts", time_stamp)
    os.mkdir(scripts_root_folder)

    # Dumping experimental results to ./experiments
    output_root_folder = os.path.join(current_folder, "experiments", time_stamp)
    os.mkdir(output_root_folder)

    # Generate runs
    lst_runs = [
        Run(parser.cmd, args_dict, output_root_folder, parser.fmt, parser.named_args)
        for args_dict in parser.lst_args_dicts
    ]

    lst_scripts = [
        Script(parser.prologue, parser.epilogue, [])
        for i in range(num_scripts)
    ]

    # TODO:
    # 1. Check the validaty of the config file before writing scripts.
    # 2. It's not safe to rely on the dictionary ordering in toml files.
    def value2index(value, lst):
        return value if not lst else lst.index(value)

    lst_runs_sorted = sorted(
        lst_runs,
        key=lambda x: [value2index(x.args_dict[key], lst) for key, lst in parser.ordering.items()],
    )

    for i, run in enumerate(lst_runs_sorted):
        lst_scripts[i % num_scripts].add_run(run)
        os.makedirs(run.output_path)

    for i, script in enumerate(lst_scripts):
        script.write(os.path.join(scripts_root_folder, "{:d}.sh".format(i)))

    # create symlinks at the very end
    if symlink:
        create_latest_symlink(scripts_root_folder)
        create_latest_symlink(output_root_folder)


if __name__ == "__main__":
    import fire
    fire.Fire(main)
