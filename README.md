# Zipf's law 

## Installation

```pip install -r requirements.txt```

```pip install -e .```

## Data
1. LUNA: download http://zil.ipipan.waw.pl/LUNA?action=AttachFile&do=view&target=LUNA.PL.zip and extract `LUNA.PL` from the archive. This path is later referred to as `path/to/luna/dataset`.

2. MultiWOZ: clone https://github.com/budzianowski/multiwoz and extract `multiwoz/data/MultiWOZ_2.2` from the repository. This path is later referred to as `path/to/multiwoz/dataset`.

## Experiments

```python -m zipfs_law.cli.run_experiments --luna-dataset-dir path/to/luna/dataset --multiwoz-dataset-dir path/to/multiwoz/dataset```