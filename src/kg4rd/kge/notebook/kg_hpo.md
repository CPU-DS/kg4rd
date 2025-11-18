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
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_hpo_20251118.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | jl1cmf61 |  |