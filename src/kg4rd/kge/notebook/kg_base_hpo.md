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
| TransE | src/scripts/TransE_hpo.py | config/TransE_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 | ttzl0rst |
| TransD | src/scripts/TransD_hpo.py | config/TransD_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 | 56u3w0mp |
| TransH | src/scripts/TransH_hpo.py | config/TransH_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 | 0vn7nu69 |
| TransR | src/scripts/TransR_hpo.py | config/TransR_base_hpo_20251025.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 | wdb9p7to |