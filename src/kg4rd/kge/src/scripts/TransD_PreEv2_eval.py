# -*- coding: utf-8 -*-
# Create Date: 2025/10/23
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: TransD_PreEv2_eval.py
# Description: 评估 TransD_PreEv2

from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester
from unike.utils import WandbLogger
from model.TransD_PreEv2 import TransD_PreEv2

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
	valid_file=config['valid_file'],
	test_file=config['test_file'],
	batch_size = config['batch_size'],
	neg_ent = config['neg_ent'],
	test = True,
	test_batch_size = config['test_batch_size'],
	num_workers = config['num_workers'],
	train_sampler = BernSampler,
	test_sampler = TradTestSampler
)

transd = TransD_PreEv2(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim_e = config['dim_e'],
    dim_r = config['dim_r'],
	p_norm = config['p_norm'], 
	norm_flag = config['norm_flag'],
	ent_embed_path = config['ent_embed_path']
)

model = NegativeSampling(
	model = transd, 
	loss = MarginLoss(margin = config['margin'], adv_temperature = config['adv_temperature']),
)

tester = Tester(
    model = transd, 
    data_loader = dataloader, 
    use_gpu = config['test_use_gpu'],
    device = config['device']
)

tester.set_hits(new_hits=config['test_hits'])

trainer = Trainer(
    model = model,
    opt_method = config['opt_method'],
    data_loader = dataloader.train_dataloader(),
	epochs = config['epochs'], 
    lr = config['lr'],
    test = True,
    tester = tester, 
    valid_interval = config['valid_interval'],
	log_interval = config['log_interval'],
    save_interval = config['save_interval'],
	save_path = config['save_path'], 
    delta = config['delta'],
	wandb_logger = wandb_logger,
    use_accelerator = config['use_accelerator'],
    use_early_stopping = config['use_early_stopping'],
)

if __name__ == '__main__':
	trainer.run()
	wandb_logger.finish()
