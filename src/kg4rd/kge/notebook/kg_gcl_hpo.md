## 使用 GCL 结果作为预嵌入并进行超参数搜索

### 数据集

```
data/train2id_base.txt
data/valid2id_base.txt
data/test2id_base.txt
```

### Wandb

http://10.4.3.159:8080

### GCL 预嵌入

```
src/kg4rd/gcl/embeddings/gcl_20251014/ent_embed.npz
```

### 训练配置

| 模型 | 训练脚本 | 配置文件 | 设备 |
| ---- | -------- | ---- | ---- | 
| TransE_PreEv2 | src/scripts/TransE/TransE_PreEv2_hpo.py | config/TransE/TransE_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| TransD_PreEv2 | src/scripts/TransD/TransD_PreEv2_hpo.py | config/TransD/TransD_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |

- TransE
```
adv_temperature: 1
batch_size: 1,024
delta: 0.0001
dim: 200
epochs: 1000
l3_regul_rate: 0
loss: MarginLoss
lr: 0.569992214167705
margin: 6
neg_ent: 64
norm_flag: True
opt_method: sgd
p_norm: 1
patience: 2
regul_rate: 0
strategy: NegativeSampling
test_batch_size: 30
train_sampler: BernSampler
use_early_stopping: True
valid_interval: 50
```

- TransD
```
adv_temperature: 1
batch_size: 2,048
delta: 0.0001
dim_e: 256
dim_r: 256
epochs: 1000
l3_regul_rate: 0
loss: MarginLoss
lr: 0.39679280518417975
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