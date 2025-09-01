# -*- coding: utf-8 -*-
# Create Date: 2025/07/15
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: accelerator_rotate_all.py
# Description: kg4rd RotatE experimental dmd 在整个图谱上训练

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, UniSampler
from unike.module.model import RotatE
from unike.module.loss import SigmoidLoss
from unike.module.strategy import NegativeSampling
from unike.config import Trainer

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-RotatE-dmdexp-all-multi",
	config=dict(
        in_path = 'src/kg4rd/extract/experimental_dmd/kge/data/',
		train_file = 'all2id.txt',
		batch_size = 512,
		neg_ent = 25,
		test = False,
  		num_workers = 16,
		dim = 512,
		margin = 6.0,
		epsilon = 2.0,
		adv_temperature = 2,
		regul_rate = 0.0,
        use_tqdm = True,
		epochs = 500,
		lr = 2e-5,
		opt_method = 'adam',
		log_interval = 1,
		save_interval = 50,
		save_path = "src/kg4rd/extract/experimental_dmd/kge/checkpoints/rotate/all/multi/rotate.pth"
    )
)

config = wandb_logger.config

dataloader = KGEDataLoader(
	in_path = config.in_path,
	train_file = config.train_file,
	batch_size = config.batch_size,
	neg_ent = config.neg_ent,
	test = config.test,
	num_workers = config.num_workers,
	train_sampler = UniSampler
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

trainer = Trainer(
    model = model, 
    data_loader = dataloader.train_dataloader(), 
    epochs = config.epochs,
    use_accelerator = True,
	lr = config.lr, 
    opt_method = config.opt_method, 
    test = config.test, 
	log_interval = config.log_interval, 
    save_interval = config.save_interval,
	save_path = config.save_path, 
    wandb_logger = wandb_logger
)

if __name__ == "__main__":
    trainer.run()
    wandb_logger.finish()
