# -*- coding: utf-8 -*-
# Create Date: 2025/07/10
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: rotate.py
# Description: kg4rd RotatE experimental dmd 模型测试

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, UniSampler, TradTestSampler
from unike.module.model import RotatE
from unike.module.loss import SigmoidLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-RotatE-dmdexp",
	config=dict(
        in_path = 'src/kg4rd/extractor/experimental_dmd/kge_origin/data/',
		batch_size = 512,
		neg_ent = 10,
		test = True,
		test_batch_size = 10,
  		num_workers = 16,
		dim = 256,
		margin = 6.0,
		epsilon = 2.0,
		adv_temperature = 2,
		regul_rate = 0.0,
        use_tqdm = True,
		use_gpu = True,
		device = 'cuda:0',
		epochs = 500,
		lr = 2e-5,
		opt_method = 'adam',
  		valid_interval = 50,
		log_interval = 1,
		save_interval = 50,
		save_path = "src/kg4rd/extractor/experimental_dmd/kge_origin/checkpoints/rotate/rotate.pth",
        use_early_stopping=True
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
	train_sampler = UniSampler,
	test_sampler = TradTestSampler
)

rotate = RotatE(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim,
	margin = config.margin,
	epsilon = config.epsilon,
)

model = NegativeSampling(
	model = rotate, 
	loss = SigmoidLoss(adv_temperature = config.adv_temperature),
	regul_rate = config.regul_rate
)

tester = Tester(
    model = rotate, 
    data_loader = dataloader, 
    use_tqdm = config.use_tqdm,
    use_gpu = config.use_gpu, 
    device = config.device
)

tester.set_hits(new_hits=[1, 3, 10, 30, 50])

trainer = Trainer(
    model = model, 
    data_loader = dataloader.train_dataloader(), 
    epochs = config.epochs,
	lr = config.lr, 
    opt_method = config.opt_method, 
    use_gpu = config.use_gpu, 
    device = config.device,
	tester = tester, 
    test = config.test, 
    valid_interval = config.valid_interval,
	log_interval = config.log_interval, 
    save_interval = config.save_interval,
	save_path = config.save_path, 
wandb_logger = wandb_logger
)

if __name__ == "__main__":
    trainer.run()
    wandb_logger.finish()
