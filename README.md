# A Light Weight Repo for Experiment Management

## Folder Structure
```
sbatch-jobs-utils/ # This repository
├── configs
├── experiments
├── scripts
├── submit
├── README.md
├── generate_scripts.py
└── utils.py
```

## Usage

generate scripts
```
python generate_scripts.py ./configs/CONFIGURATION.toml
```

run scripts
```
bash ./submit/bash.sh ./scripts/latest/
```

**Special Argument**
```
python main.py --arg1=value1 --arg2=value2 ... --output_path=/path/to/output/folder/
```
Note that `--output_path` is a special argument added to the command.
The script, e.g., `main.py`, has to support this argument.

## TODOs
[ ] Improve random ordering
[ ] Fix the bug that the ordering section cannot be empty
