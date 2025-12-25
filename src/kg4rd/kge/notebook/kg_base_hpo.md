## 在未补全的知识图谱上进行超参数搜索

### 数据集

```
data/train2id_base.txt
data/valid2id_base.txt
data/test2id_base.txt
```

### Wandb

http://10.4.3.159:8080

### 训练配置

| 模型 | 训练脚本 | 配置文件 | 设备 | Wandb | 状态 |
| ---- | -------- | ---- | ---- | ---- | --- |
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_base_hpo_20251028.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | 3ennbbwl | 已完成 |
| TransE | src/scripts/TransE/TransE_hpo.py | config/TransE/TransE_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 | yzpfpb2e | 已完成 | 
| TransH | src/scripts/TransH/TransH_hpo.py | config/TransH/TransH_base_hpo_20251025.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:0 | h6a1sujn | 已完成 | 
| ANALOGY | src/scripts/ANALOGY/ANALOGY_hpo.py | config/ANALOGY/ANALOGY_base_hpo_20251028.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:1 | 388xxe2t | 已完成 | 

### 最优结果

- DistMult (ym3uhkwc)

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

- TransE (74wykuey)
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

- TransH (h6a1sujn)
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

- ANALOGY (q0slgvut)
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
opt_method: adam
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 10
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```