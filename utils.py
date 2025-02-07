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
