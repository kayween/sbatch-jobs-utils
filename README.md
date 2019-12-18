# sbatch jobs utils

## folder structure
```
.
+-- exps
|   +-- generate_script.py
|   +-- job-type-1.py # python script that contains arguments for experiments and collect_results function
|   +-- job-type-2.py
+-- script
|   +-- job-type-1 # folder containing slurm scripts generated
|   +-- job-type-2
+-- output
|   +-- job-type-1 # folder containing outputs of experiments e.g. std output 
|   +-- job-type-2
+-- slurm
|   +-- job-type-1 # folder containing slurm outputs
|   +-- job-type-2
+-- code1.py
+-- code2.py
```