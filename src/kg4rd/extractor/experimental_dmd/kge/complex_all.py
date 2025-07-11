# -*- coding: utf-8 -*-
# Create Date: 2025/07/11
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: complex.py
# Description: kg4rd ComplEx experimental dmd 在整个图谱上训练

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, BernSampler
from unike.module.model import ComplEx
from unike.module.loss import SoftplusLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer

wandb_logger = WandbLogger(
	project="kg4rd",
	name="kg4rd-ComplEx-dmdexp-all",
	config=dict(
		in_path = 'src/kg4rd/extractor/experimental_dmd/kge/data/',
		train_file = 'all2id.txt',
		batch_size = 1024,
		neg_ent = 25,
		test = False,
		num_workers = 16,
		dim = 200,
		regul_rate = 1.0,
        use_tqdm = True,
		use_gpu = True,
		device = 'cuda:2',
		epochs = 200,
		lr = 0.5,
		opt_method = 'adagrad',
		log_interval = 1,
		save_interval = 50,
		save_path = 'src/kg4rd/extractor/experimental_dmd/kge/checkpoints/complex/all/complex.pth',
	),
	use='swanlab'
)

config = wandb_logger.config


dataloader = KGEDataLoader(
	in_path = config.in_path,
    train_file=config.train_file,
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = config.test,
	num_workers = config.num_workers,
	train_sampler = BernSampler
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


trainer = Trainer(
    model = model, 
    data_loader = dataloader.train_dataloader(), 
    epochs = config.epochs,
	lr = config.lr, 
    opt_method = config.opt_method, 
    use_gpu = config.use_gpu, 
    device = config.device,
    test = config.test, 
    log_interval = config.log_interval, 
    save_interval = config.save_interval,
    save_path = config.save_path, 
    use_wandb = True
)

if __name__ == "__main__":
    trainer.run()
    wandb_logger.finish()