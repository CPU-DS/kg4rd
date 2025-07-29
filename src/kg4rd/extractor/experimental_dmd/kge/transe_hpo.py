# -*- coding: utf-8 -*-
# Create Date: 2025/07/29
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: transe_hpo.py
# Description: transe hpo

import pprint
import os
from unike.data import get_kge_data_loader_hpo_config
from unike.module.model import get_transe_hpo_config
from unike.module.loss import get_margin_loss_hpo_config
from unike.module.strategy import get_negative_sampling_hpo_config
from unike.config import get_tester_hpo_config
from unike.config import get_trainer_hpo_config
from unike.config import set_hpo_config, start_hpo_train

os.environ["WANDB_MODE"] = "offline"
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

data_loader_config = get_kge_data_loader_hpo_config()
data_loader_config.update({
    'in_path': {
        'value': os.path.join('src/kg4rd/extractor/experimental_dmd/kge/data/')
    },
    'test_batch_size': {
        'value': 10
    },
    'batch_size': {
        'values': [128, 256, 512, 1024, 2048, 4096]
    }
})
print("data_loader_config:")
pprint.pprint(data_loader_config)
print()

kge_config = get_transe_hpo_config()
print("kge_config:")
pprint.pprint(kge_config)
print()

loss_config = get_margin_loss_hpo_config()
print("loss_config:")
pprint.pprint(loss_config)
print()

strategy_config = get_negative_sampling_hpo_config()
print("strategy_config:")
pprint.pprint(strategy_config)
print()

tester_config = get_tester_hpo_config()
tester_config.update({
    'device': {
        'value': 'cuda:1'
    }
})
print("tester_config:")
pprint.pprint(tester_config)
print()

trainer_config = get_trainer_hpo_config()
trainer_config.update({
    'log_interval': {
        'value': 1
    },
    'valid_interval': {
        'value': 50
    },
    'save_path': {
        'value': 'src/kg4rd/extractor/experimental_dmd/kge/checkpoints/transe/hpo/transe.pth'
    }
})
print("trainer_config:")
pprint.pprint(trainer_config)
print()

sweep_config = set_hpo_config(
    sweep_name = "kg4rd-TransE-hpo",
    data_loader_config = data_loader_config,
    kge_config = kge_config,
    loss_config = loss_config,
    strategy_config = strategy_config,
    tester_config = tester_config,
    trainer_config = trainer_config)
print("sweep_config:")
pprint.pprint(sweep_config)
print()

start_hpo_train(project="kg4rd",config=sweep_config, count=3)