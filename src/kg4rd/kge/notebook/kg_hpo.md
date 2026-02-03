## 在补全后的知识图谱上进行超参数搜索

### 数据集

```
data/train2id.txt
data/valid2id.txt
data/test2id.txt
```

### Wandb

http://10.4.3.159:8080

### 训练配置

| 模型 | 训练脚本 | 配置文件 | 设备 |
| ---- | -------- | ---- | ---- |
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_hpo_20251118.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| TransE | src/scripts/TransE/TransE_hpo.py | config/TransE/TransE_hpo_20251126.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | g2h6m14o |
| TransD | src/scripts/TransD/TranD_hpo.py | config/TransD/TransD_hpo_20251225.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 | 2atq85ex |
| TransH | src/scripts/TransH/TranH_hpo.py | config/TransH/TransH_hpo_20251225.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | x1wr21lm |
| ComplEx | src/scripts/ComplEx/ComplEx_hpo.py | config/ComplEx/ComplEx_hpo_20260105.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| ANALOGY | src/scripts/ANALOGY/ANALOGY_hpo.py | config/ANALOGY/ANALOGY_hpo_20260105.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| RESCAL | src/scripts/RESCAL/RESCAL_hpo.py | config/ANALOGY/RESCAL_hpo_20260105.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 |
| SimplE | src/scripts/SimplE/SimplE_hpo.py | config/SimplE/SimplE_hpo_20260112.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 |
| RGCN | src/scripts/RGCN/RGCN_hpo.py | config/RGCN/RGCN_hpo_20260130.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| CompGCN | src/scripts/CompGCN/CompGCN_hpo.py | config/CompGCN_hpo_20260130.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |

- DistMult

```
adv_temperature: 6
batch_size: 1024
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: SigmoidLoss
lr: 0.3282426851422243
neg_ent: 64
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- TransE
```
adv_temperature: 6
batch_size: 4,096
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: MarginLoss
lr: 0.05079633914318759
margin: 1
neg_ent: 64
norm_flag: True
opt_method: adam
p_norm: 1
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- TransH
```
adv_temperature: 6
batch_size: 1,024
delta: 0.0001
dim: 200
epochs: 1,000
l3_regul_rate: 0
lr: 0.022296944339356858
margin: 1
neg_ent: 64
norm_flag: True
opt_method: adagrad
p_norm: 1
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- RESCAL
```
adv_temperature: 6
batch_size: 2,048
delta: 0.0001
dim: 50
epochs: 1000
l3_regul_rate: 0
loss: MarginLoss
lr: 0.7485010381006322
margin: 6
neg_ent: 16
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 5
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- ANALOGY
```
adv_temperature: 6
batch_size: 512
delta: 0.0001
dim: 50
epochs: 1,000
l3_regul_rate: 0
lr: 0.5233303153398249
neg_ent: 16
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 5
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- TransD
```
adv_temperature: 6
batch_size: 512
delta: 0.0001
dim_e: 200
dim_r: 200
epochs: 1,000
l3_regul_rate: 0
lr: 0.01793454374096748
neg_ent: 64
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- ComplEx
```
adv_temperature: 6
batch_size: 512
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: SoftplusLoss
lr: 0.7621625391244857
neg_ent: 4
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- SimplE
```
adv_temperature: 6
batch_size: 512
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: NegativeSampling
lr: 0.5679825984232756
neg_ent: 64
opt_method: sgd
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- RGCN
```
adv_temperature: 1
batch_size: 3000
delta: 0.0001
dim: 200
l3_regul_rate: 0
loss: RGCNLoss
lr: 0.7857815410979511
neg_ent: 16
opt_method: adagrad
patience: 2
regul_rate: 0
strategy: RGCNSampling
train_sampler: BernSampler
use_early_stopping: True
```

- CompGCN
```
adv_temperature: 3
batch_size: 256
delta: 0.0001
dim: 100
epochs: 1000
l3_regul_rate: 0
loss: CompGCNLoss
lr: 0.3451281510901301
neg_ent: 16
opt_method: adagrad
patience: 2
regul_rate: 0
strategy: CompGCNSampling
test_batch_size: 5
train_sampler: Sampler
use_early_stopping: True
valid_interval: 50
```