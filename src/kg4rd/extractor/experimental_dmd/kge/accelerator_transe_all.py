# -*- coding: utf-8 -*-
# Create Date: 2025/07/29
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: accelerator_transe_all.py
# Description: kg4rd TransE experimental dmd 在整个图谱上训练

from unike.data import KGEDataLoader, BernSampler
from unike.module.model import TransE
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester
from unike.utils import WandbLogger

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-TransE-dmdexp-all-multi",
	config=dict(
		in_path = 'src/kg4rd/extractor/experimental_dmd/kge/data/',
		train_file = 'all2id.txt',
		batch_size = 256,
		neg_ent = 25,
		num_workers = 16,
		dim = 100,
		p_norm = 1,
		norm_flag = True,
		margin = 1.0,
		epochs = 500,
		lr = 0.01,
		valid_interval = 50,
		log_interval = 1,
		save_interval = 50,
		save_path = "src/kg4rd/extractor/experimental_dmd/kge/checkpoints/transe/all/multi/transe.pth",
		delta = 0.01
	)
)

config = wandb_logger.config


dataloader = KGEDataLoader(
	in_path = config.in_path, 
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = False,
	num_workers = config.num_workers,
	train_sampler = BernSampler
)

transe = TransE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim, 
	p_norm = config.p_norm, 
	norm_flag = config.norm_flag
)

model = NegativeSampling(
	model = transe, 
	loss = MarginLoss(margin = config.margin),
)

trainer = Trainer(
    model = model, 
    data_loader = dataloader.train_dataloader(),
	epochs = config.epochs, 
    lr = config.lr,
    test = False, 
    valid_interval = config.valid_interval,
	log_interval = config.log_interval,
    save_interval = config.save_interval,
	save_path = config.save_path, 
    delta = config.delta,
	wandb_logger = wandb_logger,
    use_accelerator=True
)

if __name__ == '__main__':
	trainer.run()
	wandb_logger.finish()
