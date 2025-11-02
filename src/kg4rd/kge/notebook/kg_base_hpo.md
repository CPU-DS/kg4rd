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

| 模型 | 训练脚本 | 配置文件 | 设备 | Wandb |
| ---- | -------- | ---- | ---- | ---- | 
| TransE | src/scripts/TransE_hpo.py | config/TransE_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 | 58jxmf1s |
| TransD | src/scripts/TransD_hpo.py | config/TransD_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | cjj2pds7 |
| TransH | src/scripts/TransH_hpo.py | config/TransH_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 | f7ar4chd |
| DistMult | src/scripts/DistMult_hpo.py | config/DistMult_base_hpo_20251028.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 | al8l5x3s |
