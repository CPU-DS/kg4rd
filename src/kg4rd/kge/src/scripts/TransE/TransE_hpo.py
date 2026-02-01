# -*- coding: utf-8 -*-
# Create Date: 2025/10/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransE_hpo.py
# Description: TransE 超参数搜索

from unike.data import get_kge_data_loader_hpo_config
from unike.module.model import get_transe_hpo_config
from unike.module.loss import get_margin_loss_hpo_config
from unike.module.strategy import get_negative_sampling_hpo_config
from unike.config import get_tester_hpo_config
from unike.config import get_trainer_hpo_config
from unike.config import set_hpo_config, start_hpo_train, set_hpo_hits

import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str)
parser.add_argument('--resume_sweep_id', type=str, required=False, default=None)
args = parser.parse_args()

with open(args.config, 'r') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)
 
data_loader_config = get_kge_data_loader_hpo_config()
data_loader_config.update({
    'in_path': {
        'value': config['in_path']
    },
    'train_file': {
        'value': config['train_file']
    },
    'valid_file': {
        'value': config['valid_file']
    },
    'test_file': {
        'value': config['test_file']
    },
    'test_batch_size': {
        'value': config['test_batch_size']
    }
})

kge_config = get_transe_hpo_config()

loss_config = get_margin_loss_hpo_config()

strategy_config = get_negative_sampling_hpo_config()

tester_config = get_tester_hpo_config()
tester_config.update({
    'device': {
        'value': config['tester_device']
    },
    'use_tqdm': {
        'value': True
    }
})

trainer_config = get_trainer_hpo_config()
trainer_config.update({
    'device': {
        'value': config['trainer_device']
    },
    'log_interval': {
        'value': config['log_interval']
    },
    'valid_interval': {
        'value': config['valid_interval']
    },
    'save_path': {
        'value': config['save_path']
    },
    'epochs': {
        'value': config['epochs']
    },
})

sweep_config = set_hpo_config(
    sweep_name = config['sweep_name'],
    data_loader_config = data_loader_config,
    kge_config = kge_config,
    loss_config = loss_config,
    strategy_config = strategy_config,
    tester_config = tester_config,
    trainer_config = trainer_config
)

set_hpo_hits(config['hpo_hits'])

start_hpo_train(project=config['project'], config=sweep_config, count=0, resume_sweep_id=args.resume_sweep_id, 
                prior_runs=['mmliwpw3', 'b4ecxke8', 'q8efo8qa', '1ye1t2i6', 'iteenzpi', '83b95cts', 'qn6mrlus', 'vr58agym', 'adrk6lpt', '74wykuey', 'geca7fbf', 'tjph46o8', 'xr0n1yfg', 'pvdj4z4a', 'qb5lvmdd', 'vkv6ef1m', 'mxq9oj9x', 'rehfmwr2', 'id0fti16', 'dc6mripw'])