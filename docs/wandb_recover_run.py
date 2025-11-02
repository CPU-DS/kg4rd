# -*- coding: utf-8 -*-
# Create Date: 2025/11/02
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: wandb_runs_recover.py
# Description: wandb runs 恢复

import wandb
import subprocess
import os
import re

WANDB_LOCAL_PATH = './wandb'
ENTITY = 'wangtao'
PROJCRT = 'kg4rd'


def recover_run(run_id: str):
    wandb.init(
        id=run_id,
        project=PROJCRT,
        entity=ENTITY,
        resume="allow"
    )
    wandb.finish()
    pattern = re.compile(r'run-\d+_\d+-' + run_id)
    for d in os.listdir(WANDB_LOCAL_PATH):
        if pattern.search(d):
            subprocess.run(f"wandb sync {os.path.join(WANDB_LOCAL_PATH, d)}", shell=True)
            break

def recover_sweep_runs(sweep_id: str):
    runs = []
    for d in os.listdir(os.path.join(WANDB_LOCAL_PATH, f'sweep-{sweep_id}')):
        run_id = d.split('-')[-1].split('.')[0]
        recover_run(run_id)
        runs.append(run_id)
    return runs
