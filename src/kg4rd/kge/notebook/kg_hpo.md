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

| 模型 | 训练脚本 | 配置文件 | 设备 | Wandb | 状态 |
| ---- | -------- | ---- | ---- | ---- | ---- |
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_hpo_20251118.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | jl1cmf61 | 已完成 |

- DistMult (nl7gmedp)

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