# -*- coding: utf-8 -*-
# Create Date: 2026/02/28
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: RESCAL_entire.py
# Description: 训练 RESCAL

from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.model import RESCAL
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester
from unike.utils import WandbLogger

import yaml
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str)
args = parser.parse_args()

with open(args.config, 'r') as f:
	config = yaml.load(f, Loader=yaml.FullLoader)
 
wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project=config['project'],
	name=config['name'],
	config=config
)

dataloader = KGEDataLoader(
	in_path = config['in_path'],
	train_file=config['train_file'],
	batch_size = config['batch_size'],
	neg_ent = config['neg_ent'],
	test = False,
	num_workers = config['num_workers'],
	train_sampler = BernSampler,
)

rescal = RESCAL(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config['dim']
)

model = NegativeSampling(
	model = rescal, 
	loss = MarginLoss(margin = config['margin'], adv_temperature = config['adv_temperature']),
)

trainer = Trainer(
    model = model,
    opt_method = config['opt_method'],
    data_loader = dataloader.train_dataloader(),
	epochs = config['epochs'], 
    lr = config['lr'],
    test = False,
	log_interval = config['log_interval'],
    save_interval = config['save_interval'],
	save_path = config['save_path'], 
    delta = config['delta'],
	wandb_logger = wandb_logger,
	use_gpu = config['trainer_use_gpu'],
    use_accelerator = config['use_accelerator'],
	device = config['trainer_device']
)

if __name__ == '__main__':
	trainer.run()
	wandb_logger.finish()

