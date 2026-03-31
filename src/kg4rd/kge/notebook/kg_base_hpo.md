## 在未补全的知识图谱上进行超参数搜索

### 数据集

```
data/train2id_base.txt
data/valid2id_base.txt
data/test2id_base.txt
```

### 训练配置

| 模型 | 训练脚本 | 配置文件 | 设备 |
| ---- | -------- | ---- | ---- |
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_base_hpo_20251028.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| TransE | src/scripts/TransE/TransE_hpo.py | config/TransE/TransE_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| TransH | src/scripts/TransH/TransH_hpo.py | config/TransH/TransH_base_hpo_20251025.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:0 |
| ANALOGY | src/scripts/ANALOGY/ANALOGY_hpo.py | config/ANALOGY/ANALOGY_base_hpo_20251028.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:1 |
| TransD | src/scripts/TransD/TranD_hpo.py | config/TransD/TransD_base_hpo_20251025.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:0 |
| ComplEx | src/scripts/ComplEx/ComplEx_hpo.py | config/ComplEx/ComplEx_base_hpo_20251027.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:1 |
| SimplE | src/scripts/SimplE/SimplE_hpo.py | config/SimplE/SimplE_base_hpo_20251028.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| RESCAL | src/scripts/RESCAL/RESCAL_hpo.py | config/RESCAL/RESCAL_base_hpo_20251027.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |

### 最优结果

- DistMult

```
adv_temperature: 3
batch_size: 512
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: SigmoidLoss
lr: 0.5943847642116686
neg_ent: 16
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
lr: 0.07236990606544978
margin: 1
neg_ent: 64
norm_flag: True
opt_method: sgd
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
batch_size: 4,096
delta: 0.0001
dim: 200
epochs: 1,000
l3_regul_rate: 0
lr: 0.02483607260093485
margin: 1
neg_ent: 16
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

- ANALOGY
```
adv_temperature: 6
batch_size: 4,096
delta: 0.0001
dim: 200
epochs: 1,000
l3_regul_rate: 0
lr: 0.02483607260093485
neg_ent: 16
opt_method: adam
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
dim: 50
epochs: 1000
l3_regul_rate: 0
loss: NegativeSampling
lr: 0.8753348749023981
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

- RESCAL
```
adv_temperature: 3
batch_size: 4,096
delta: 0.0001
dim: 50
epochs: 1000
l3_regul_rate: 0
loss: MarginLoss
lr: 0.54787191581426
margin: 6
neg_ent: 64
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
dim_e: 100
dim_r: 100
epochs: 1,000
l3_regul_rate: 0
lr: 0.19029603128223693
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
adv_temperature: 1
batch_size: 512
delta: 0.0001
dim: 50
epochs: 1000
l3_regul_rate: 0
loss: SoftplusLoss
lr: 0.8371733105997534
neg_ent: 16
opt_method: adagrad
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 5
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```