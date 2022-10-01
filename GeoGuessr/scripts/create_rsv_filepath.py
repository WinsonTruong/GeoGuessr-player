#create_rsv_filepath.py

import os
import json
import pandas as pd 

FOLDER_NAME = 'rsv'
for k in ['indv', 'pano']:
    os.mkdir(f'../data/{FOLDER_NAME}_{k}')
    os.mkdir(f'../data/{FOLDER_NAME}_{k}/train')
    os.mkdir(f'../data/{FOLDER_NAME}_{k}/unlabeled')
