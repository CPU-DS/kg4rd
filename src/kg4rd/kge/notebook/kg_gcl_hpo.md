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

| 模型 | 训练脚本 | 配置文件 | 设备 | Wandb |
| ---- | -------- | ---- | ---- | ---- | 
| TransE_PreEv2 | src/scripts/TransE/TransE_PreEv2_hpo.py | config/TransE/TransE_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |  |
| TransD_PreEv2 | src/scripts/TransD/TransD_PreEv2_hpo.py | config/TransD/TransD_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |  |
| TransH_PreEv2 | src/scripts/TransH/TransH_PreEv2_hpo.py | config/TransH/TransH_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |  |
| DistMult_PreEv2 | src/scripts/DistMult/DistMult_PreEv2_hpo.py | config/DistMult/DistMult_PreEv2_hpo_20251102.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 |  |