# -*- coding: utf-8 -*-
# Create Date: 2025/09/10
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: transe.py
# Description: 训练 TransE

from unike.data import KGEDataLoader, BernSampler
from unike.module.model import TransE
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer
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
	config=config,
)

dataloader = KGEDataLoader(
	in_path = config['in_path'],
	train_file=config['train_file'],
	batch_size = config['batch_size'],
	neg_ent = config['neg_ent'],
	test = False,
	num_workers = config['num_workers'],
	train_sampler = BernSampler
)

transe = TransE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config['dim'], 
	p_norm = config['p_norm'], 
	norm_flag = config['norm_flag']
)

model = NegativeSampling(
	model = transe, 
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
    use_accelerator = config['use_accelerator']
)

if __name__ == '__main__':
	trainer.run()
	wandb_logger.finish()
