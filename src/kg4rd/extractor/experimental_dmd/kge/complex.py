# -*- coding: utf-8 -*-
# Create Date: 2025/07/10
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: complex.py
# Description: kg4rd ComplEx experimental dmd 模型测试

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, BernSampler, TradTestSampler
from unike.module.model import ComplEx
from unike.module.loss import SoftplusLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer, Tester

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-ComplEx-dmdexp",
	config=dict(
		in_path = 'src/kg4rd/extractor/experimental_dmd/kge_origin/data/',
		batch_size = 1024,
		neg_ent = 25,
		test = True,
		test_batch_size = 10,
		num_workers = 16,
		dim = 200,
		regul_rate = 1.0,
        use_tqdm = True,
		use_gpu = True,
		device = 'cuda:1',
		epochs = 500,
		lr = 0.5,
		opt_method = 'adagrad',
		valid_interval = 50,
		log_interval = 1,
		save_interval = 50,
		save_path = 'src/kg4rd/extractor/experimental_dmd/kge_origin/checkpoints/complex/complex.pth',
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

complEx = ComplEx(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim
)

model = NegativeSampling(
	model = complEx, 
	loss = SoftplusLoss(), 
	regul_rate = config.regul_rate
)

tester = Tester(
    model = complEx, 
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
	wandb_logger = wandb_logger,
    use_early_stopping = config.use_early_stopping
)

if __name__ == "__main__":
    trainer.run()
    wandb_logger.finish()