# -*- coding: utf-8 -*-
# Create Date: 2025/06/25
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: transe.py
# Description: kg4rd TransE experimental dmd 模型测试

from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.model import TransE
from unike.module.loss import MarginLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester
from unike.utils import WandbLogger

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-TransE-dmdexp",
	config=dict(
		in_path = 'src/kg4rd/extractor/experimental_dmd/kge/data/',
		batch_size = 256,
		neg_ent = 25,
		test = True,
		test_batch_size = 10,
		num_workers = 16,
		dim = 100,
		p_norm = 1,
		norm_flag = True,
		margin = 1.0,
		use_gpu = True,
		device = "cuda:0",
		epochs = 500,
		lr = 0.01,
		valid_interval = 50,
		log_interval = 1,
		save_interval = 50,
		save_path = "src/kg4rd/extractor/experimental_dmd/kge/checkpoints/transe/transe.pth",
		delta = 0.01,
		use_early_stopping = True
	)
)

config = wandb_logger.config


dataloader = KGEDataLoader(
	in_path = config.in_path, 
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = config.test,
	test_batch_size = config.test_batch_size,
	num_workers = config.num_workers,
	train_sampler = BernSampler,
	test_sampler = TradTestSampler
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

tester = Tester(
    model = transe, 
    data_loader = dataloader, 
    use_gpu = config.use_gpu,
    device = config.device
)

tester.set_hits(new_hits=[1, 3, 10, 30, 50])

trainer = Trainer(
    model = model, 
    data_loader = dataloader.train_dataloader(),
	epochs = config.epochs, 
    lr = config.lr, 
    use_gpu = config.use_gpu, 
    device = config.device,
	tester = tester, 
    test = config.test, 
    valid_interval = config.valid_interval,
	log_interval = config.log_interval,
    save_interval = config.save_interval,
	save_path = config.save_path, 
    delta = config.delta,
	wandb_logger = wandb_logger,
    use_early_stopping=config.use_early_stopping,
)

if __name__ == '__main__':
	trainer.run()
	wandb_logger.finish()
