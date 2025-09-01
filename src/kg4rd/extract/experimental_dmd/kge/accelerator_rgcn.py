# -*- coding: utf-8 -*-
# Create Date: 2025/07/17
# Author: wangtao <wangtao.cpu@gmail.com>
# File Name: rgcn.py
# Description: kg4rd RGCN experimental dmd 模型测试

from unike.utils import WandbLogger
from unike.data import KGEDataLoader, RGCNSampler, RGCNTestSampler
from unike.module.model import RGCN
from unike.module.loss import RGCNLoss
from unike.module.strategy import RGCNSampling
from unike.config import Trainer, Tester

wandb_logger = WandbLogger(endpoint='swanlab').set_config(
	project="kg4rd",
	name="kg4rd-RGCN-dmdexp",
	config=dict(
        in_path = 'src/kg4rd/extract/experimental_dmd/kge_origin/data/',
        batch_size = 128,
        neg_ent = 10,
        test = True,
        test_batch_size = 100,
        num_workers = 16,
        dim = 500,
        num_layers = 2,
        regularization = 1e-5,
        use_tqdm = False,
        use_gpu = True,
        device = 'cuda:2',
        epochs = 10000,
        lr = 0.0001,
        valid_interval = 50,
        log_interval = 1,
        save_interval = 100,
        save_path = 'src/kg4rd/extract/experimental_dmd/kge/checkpoint/kge_origin/rgcn.pth',
        use_early_stopping=True,
        use_accelerator=True
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
    train_sampler = RGCNSampler,
    test_sampler = RGCNTestSampler
)

rgcn = RGCN(
	ent_tol = dataloader.get_ent_tol(),
	rel_tol = dataloader.get_rel_tol(),
	dim = config.dim,
	num_layers = config.num_layers
)

model = RGCNSampling(
	model = rgcn,
	loss = RGCNLoss(model = rgcn, regularization = config.regularization)
)

tester = Tester(
    model = rgcn, 
    data_loader = dataloader, 
    use_tqdm = config.use_tqdm,
    use_gpu = config.use_gpu, 
    device = config.device,
)

trainer = Trainer(model = model, 
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
    wandb_logger = wandb_logger,
    use_early_stopping=config.use_early_stopping,
    metric='hits@10',
    use_accelerator=config.use_accelerator
)
trainer.run()