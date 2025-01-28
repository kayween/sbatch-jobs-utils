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

## TODOs
[ ] Improve random ordering
[ ] Fix the bug that the ordering section cannot be empty