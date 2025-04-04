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

    def dump(self, path: str):
        """
        Dump the entire configuration.

        Args:
            path: The path to dump configuration.
        """
        with open(path, 'w') as f:
            f.write(tomlkit.dumps(self.config_dict))

    @property
    def root(self):
        return self.config_dict['root'] if "root" in self.config_dict else None

    @property
    def prologue(self):
        return self.config_dict['prologue']

    @property
    def epilogue(self):
        return self.config_dict['epilogue']

    @property
    def cmd(self):
        """The command to run."""
        return self.config_dict['cmd']

    @property
    def git_repo_hash(self):
        raise NotImplementedError

    @property
    def git_repo_commit_msg(self):
        raise NotImplementedError

    @cached_property
    def lst_grouped_args_dicts(self):
        return self.config_dict['grouped_arguments'] if 'grouped_arguments' in self.config_dict else []

    @cached_property
    def shared_args_dict(self):
        return self.config_dict['arguments']

    @cached_property
    def lst_args_dicts(self):
        """
        Parse the config file and return a list of dictionaries. Each dictionary contains arguments for each run.
        """
        if not self.lst_grouped_args_dicts:
            # If there are no grouped arguments, then we only need to enumerate all combinations of the shared arguments
            return cartesian_product(self.shared_args_dict)

        else:
            # Otherwise, combine grouped arguments and shared arguments and then do a Cartesian product
            # Nested comprehension makes it unreadable. But it looks cooler than itertools.chain.
            return [
                args_dict
                for grouped_args_dict in self.lst_grouped_args_dicts
                for args_dict in cartesian_product(dict(**grouped_args_dict, **self.shared_args_dict))
            ]

    @property
    def fmt(self):
        return self.config_dict['io']['format']

    @property
    def named_args(self):
        return self.config_dict['io']['named_args']

    @property
    def ordering(self):
        return self.config_dict['ordering'] if 'ordering' in self.config_dict else None


class ScriptGenerator:
    def __init__(self, config_path: str, num_scripts: int):
        # Do parsing first---the program terminates immediately if parsing fails
        self.parser = ConfigFileParser(config_path)
        self.num_scripts = num_scripts

        self.time_stamp = get_time_stamp()

    @property
    def root_folder(self):
        """The root folder to dump everything."""
        if self.parser.root is not None:
            return os.path.join(self.parser.root, self.time_stamp)
        else:
            current_folder = os.path.dirname(os.path.realpath(__file__))
            return os.path.join(current_folder, "experiments", self.time_stamp)

    @property
    def scripts_folder(self):
        """The folder to dump all scripts."""
        return os.path.join(self.root_folder, "scripts")

    @property
    def outputs_folder(self):
        """The folder to dump all runs."""
        return os.path.join(self.root_folder, "outputs")

    def write(self):
        lst_runs = self.make_runs()
        lst_scripts = self.make_scripts(lst_runs)

        os.mkdir(self.root_folder)
        self.parser.dump(os.path.join(self.root_folder, "config.toml"))

        os.mkdir(self.scripts_folder)
        for i, script in enumerate(lst_scripts):
            script.write(os.path.join(self.scripts_folder,  "{:d}.sh".format(i)))

        os.mkdir(self.outputs_folder)
        for run in lst_runs:
            os.makedirs(run.output_path)

    def make_runs(self):
        lst_runs = [
            Run(self.parser.cmd, args_dict, self.outputs_folder, self.parser.fmt, self.parser.named_args)
            for args_dict in self.parser.lst_args_dicts
        ]

        if self.parser.ordering is None:
            return lst_runs
        else:
            # TODO:
            # 1. Check the validaty of the config file before writing scripts.
            # 2. It's not safe to rely on the dictionary ordering in toml files.
            def value2index(value, lst):
                return value if not lst else lst.index(value)

            return sorted(
                lst_runs,
                key=lambda x: [value2index(x.args_dict[key], lst) for key, lst in self.parser.ordering.items()],
            )

    def make_scripts(self, lst_runs):
        return [
            Script(
                self.parser.prologue,
                self.parser.epilogue,
                [run for j, run in enumerate(lst_runs) if j % self.num_scripts == i],
            ) for i in range(self.num_scripts)
        ]

    def make_symlink(self):
        """
        TODO: Handle the symlink robustly, e.g., when the latest folder is deleted.
        """
        create_latest_symlink(self.root_folder)


def main(config_path: str, num_scripts: int = 1, symlink: bool = True):
    """
    Args:
        config_path: Path to the config file.
        num_scripts: Number of bash scripts to generate.
    """

    generator = ScriptGenerator(config_path, num_scripts)
    generator.write()

    # Create symlinks at the very end
    if symlink:
        generator.make_symlink()


if __name__ == "__main__":
    import fire
    fire.Fire(main)
