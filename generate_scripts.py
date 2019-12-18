import datetime
import os
import shutil
import importlib
import itertools
from pathlib import Path


def extract_args(module_name):
    """Parse the arguments in a given file
    script_root: the location where the generated scripts are stored
    code_root: the code location
    """
    assert module_name.endswith(".py")

    module = importlib.import_module(module_name[:-3])

    return (module.script_root,
            module.code_root,
            module.output_root,
            module.sbatch_args,
            module.cmd,
            module.cmd_args,
            module.noabbr,
            module.collect_results,
            )


def get_time_stamp():
    dt_str = str(datetime.datetime.now())
    ret = dt_str.split()[0] + '-' + dt_str.split()[1].split('.')[0]
    return ret


def create_latest_symlink(batch_job_folder, folder):
    symlink = Path(os.path.join(batch_job_folder, "latest"))
    if symlink.exists():
        assert symlink.is_symlink()
        symlink.unlink()
    symlink.symlink_to(os.path.join(batch_job_folder, folder))


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


def get_script_name(cmd, names, vals, noabbr):
    ret = cmd[:-3]
    for name, val in zip(names, vals):
        if name in noabbr:
            continue
        ret += "_{}-{}".format(name, val)
    return ret


def get_output_folder(output_root, script_name):
    return os.path.join(output_root, script_name)


def get_img_output_path(output_root, script_name):
    output_folder = get_output_folder(output_root, script_name)
    return os.path.join(output_folder, "adversarial.pt")


def get_info_output_path(output_root, script_name):
    output_folder = get_output_folder(output_root, script_name)
    return os.path.join(output_folder, "record.pt")


def get_std_output_path(output_root, script_name):
    output_folder = get_output_folder(output_root, script_name)
    return os.path.join(output_folder, "std.output")


def get_sbatch_args_with_slurm_output_path(sbatch_args):
    return sbatch_args + "#SBATCH -o ../slurm/slurm-%A.out"


def generate_script(module_name, overwrite, verbose):
    script_root, code_root, output_root, sbatch_args, cmd, cmd_args, noabbr, collect_results = extract_args(module_name)

    script_folder = "{}/{}".format(script_root, get_time_stamp())
    os.mkdir(script_folder)

    names = list(cmd_args.keys())
    lsts = [cmd_args[key] for key in cmd_args]

    for vals in itertools.product(*lsts):
        script_name = get_script_name(cmd, names, vals, noabbr)

        script_path = "{}/{}.sh".format(script_folder, script_name)

        output_folder = get_output_folder(output_root, script_name)

        if os.path.exists(output_folder):
            if overwrite:
                """CAUTION: existing files in the output folder will be deleted"""
                shutil.rmtree(output_folder)
            else:
                raise Exception("WARNING: existing files may be deleted; consider using --overwrite option")

        os.mkdir(output_folder)

        img_output_path = get_img_output_path(output_root, script_name)
        info_output_path = get_info_output_path(output_root, script_name)
        std_output_path = get_std_output_path(output_root, script_name)

        str_cmd_args = get_str_cmd_args(names, vals)
        str_cmd_args = "{} --save_img_loc {} --save_info_loc {} --{}".format(str_cmd_args,
                                                                             img_output_path,
                                                                             info_output_path,
                                                                             std_output_path)

        py_cmd = "{} {}".format(cmd, str_cmd_args)

        content = (
            "{}\n\n".format(get_sbatch_args_with_slurm_output_path(sbatch_args)) +
            "cd {}\n\n".format(code_root) +
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
    from str2bool import str2bool

    parser = argparse.ArgumentParser()

    parser.add_argument('module_name', type=str)
    parser.add_argument('--overwrite', type=str2bool, default=False)
    parser.add_argument('--verbose', type=str2bool, default=False)

    args = parser.parse_args()

    generate_script(args.module_name,
                    args.overwrite,
                    args.verbose)
