#create_rsv_filepath.py

import os
import json
import pandas as pd 

from pathlib import Path

parent_dir = Path(__file__).parent.parent
folder_names = ['rsv', 'rsv2']

for folder_name in folder_names:
    for k in ['indv', 'pano']:
        Path.mkdir(parent_dir / 'data' / f'{folder_name}_{k}', exist_ok=True)
        Path.mkdir(parent_dir / 'data' / f'{folder_name}_{k}' / 'train', exist_ok=True)
        Path.mkdir(parent_dir / 'data' / f'{folder_name}_{k}' / 'unlabeled', exist_ok=True)
