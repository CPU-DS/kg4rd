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
| DistMult | src/scripts/DistMult/DistMult_hpo.py | config/DistMult/DistMult_base_hpo_20251028.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | 3ennbbwl |
| TransE | src/scripts/TransE/TransE_hpo.py | config/TransE/TransE_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 | yzpfpb2e |
| TransD | src/scripts/TransD/TransD_hpo.py | config/TransD/TransD_base_hpo_20251025.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:1 | p3rmmbf6 |
| TransH | src/scripts/TransH/TransH_hpo.py | config/TransH/TransH_base_hpo_20251025.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:0 | h6a1sujn |
| RESCAL | src/scripts/RESCAL/RESCAL_hpo.py | config/RESCAL/RESCAL_base_hpo_20251027.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:0 | 6t4m20g7 |
| ANALOGY | src/scripts/ANALOGY/ANALOGY_hpo.py | config/ANALOGY/ANALOGY_base_hpo_20251028.yaml | 10.4.3.155/cuda 12.2/1080 Ti/cuda:1 | 388xxe2t |
