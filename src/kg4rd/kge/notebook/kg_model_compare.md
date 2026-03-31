## 在补全的知识图谱上进行评估

### 数据集

```
data/train2id.txt
data/valid2id.txt
data/test2id.txt
```

### 训练配置
| 模型 | 训练脚本 | 配置文件 | 设备 |
| ---- | -------- | ---- | ---- |
| DistMult | src/scripts/DistMult/DistMult_eval.py | config/DistMult/DistMult_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| TransE | src/scripts/TransE/TransE_eval.py | config/TransE/TransE_eval_Accel_20250910.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| TransH | src/scripts/TransH/TransH_eval.py | config/TransH/TransH_eval_Accel_20251004.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| TransD | src/scripts/TransD/TransD_eval.py | config/TransD/TransD_eval_Accel_20251004.yaml | 10.4.0.141/cuda 12.2/4090/cuda:3 |
| RESCAL | src/scripts/RESCAL/RESCAL_eval.py | config/RESCAL/RESCAL_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| ComplEx | src/scripts/ComplEx/ComplEx_eval.py | config/ComplEx/ComplEx_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| SimplE | src/scripts/SimplE/SimplE_eval.py | config/SimplE/SimplE_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:2 |
| RGCN | src/scripts/RGCN/RGCN_eval.py | config/RGCN/RGCN_eval_Accel_20260202.yaml | 172.20.72.100/cuda 12.4/H20/cuda:1 |
| CompGCN | src/scripts/CompGCN/CompGCN_eval.py | config/CompGCN/CompGCN_eval_Accel_20260203.yaml | 172.20.72.100/cuda 12.4/H20/cuda:7 |

| 模型 | MR | MRR | Hit@1 | Hit@3 | Hit@10 | Hit@30 | Hit@50 | duration |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| DistMult | 988.523 | 0.304 | 0.1 | 0.475 | 0.595 | 0.663 | 0.691 | 41554.2909 |
| TransE | 1559.734 | 0.257 | 0.004 | 0.471 | 0.608 | *0.714* | **0.75** | *21047.7633* |
| TransH | 1769.141 | 0.255 | 0.002 | 0.468 | 0.606 | 0.707 | 0.741 | 25013.6508 |
| TransD | 1665.199 | 0.258 | 0.004 | 0.471 | 0.607 | 0.712 | *0.748* | 32958.01477 |
| RESCAL | 1011.511 | 0.407 | **0.243** | 0.542 | *0.641* | 0.706 | 0.736 | **20079.6128** |
| ComplEx | 1380.405 | 0.152 | 0.034 | 0.227 | 0.332 | 0.444 | 0.501 | 38579.1861 |
| SimplE | 1764.566 | 0.121 | 0.068 | 0.144 | 0.201 | 0.278 | 0.329 |39542.04899|
| RGCN | *952.317* | *0.413* | 0.238 | *0.548* | **0.647** | 0.709 | 0.746 | 56823.4176 |
| CompGCN | **941.856** | **0.418** | *0.24* | **0.552** | 0.638 | **0.716** | 0.747 | 73284.9213 |

| 模型 | MR(type) | MRR(type) | Hit@1(type) | Hit@3(type) | Hit@10(type) | Hit@30(type) | Hit@50(type) |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| DistMult | 553.21 | 0.306 | 0.101 | 0.477 | 0.598 | 0.666 | 0.695 |
| TransE | 522.345 | 0.267 | 0.016 | 0.479 | 0.613 | 0.718 | **0.754** |
| TransH | 587.288 | 0.264 | 0.015 | 0.473 | 0.61 | 0.71 | 0.744 |
| TransD | 557.97 | 0.266 | 0.016 | 0.477 | 0.611 | 0.715 | *0.751* |
| RESCAL | 426.431 | 0.408 | *0.243* | 0.543 | **0.6742** | 0.707 | 0.738 |
| ComplEx | 754.329 | 0.156 | 0.036 | 0.231 | 0.337 | 0.452 | 0.51 |
| SimplE | 1082.309 | 0.124 | 0.071 | 0.147 | 0.205 | 0.282 | 0.333 |
| RGCN | *412.583* | *0.414* | 0.24 | *0.551* | *0.652* | *0.72* | *0.751* |
| CompGCN | **401.726** | **0.42** | **0.252** | **0.556** | 0.646 | **0.721** | 0.748 |