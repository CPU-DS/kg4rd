## 在未补全的知识图谱上进行评估

### 数据集

```
data/train2id_base.txt
data/valid2id_base.txt
data/test2id_base.txt
```

### Swanlab

http://10.4.0.141:8000

### 训练配置

| 模型 | 训练脚本 | 配置文件 | 设备 | Wandb | 状态 |
| ---- | -------- | ---- | ---- | ---- | --- |
| DistMult | src/scripts/DistMult/DistMult_eval.py | config/DistMult/DistMult_base_eval_Accel_20251118.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | rtrg844vrbiku8791m8cp | 已完成 |
| TransE | src/scripts/TransE/TransE_eval.py | config/TransE/TransE_base_eval_Accel_20251120.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | 6fnnf8lz6zjh6mv33fynj | 已完成 |