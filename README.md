# sbatch jobs utils

## folder structure
```
.
+-- exps
|   +-- generate_script.py
|   +-- job-type-1.py # python script containing arguments for experiments and collect_results()
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

## work flow

generate scripts
```
python generate_scripts.py job-type-1.py 
```

collect results
```
python collect_results.py job-type-1.py 
```
