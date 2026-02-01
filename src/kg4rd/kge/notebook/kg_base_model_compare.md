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

| 模型 | 训练脚本 | 配置文件 | 设备 |
| ---- | -------- | ---- | ---- |
| DistMult | src/scripts/DistMult/DistMult_eval.py | config/DistMult/DistMult_base_eval_Accel_20251118.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| TransE | src/scripts/TransE/TransE_eval.py | config/TransE/TransE_base_eval_Accel_20251120.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| TransH | src/scripts/TransH/TransH_eval.py | config/TransH/TransH_base_eval_Accel_20251216.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| TransD | src/scripts/TransD/TransD_eval.py | config/TransD/TransD_base_eval_Accel_20260130.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| ANALOGY | src/scripts/ANALOGY/ANALOGY_eval.py | config/ANALOGY/ANALOGY_base_eval_Accel_20260130.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| RESCAL | src/scripts/RESCAL/RESCAL_eval.py | config/RESCAL/RESCAL_base_eval_Accel_20260130.yaml | 10.4.0.141/cuda 12.2/4090/cuda:1 |
| ComplEx | src/scripts/ComplEx/ComplEx_eval.py | config/ComplEx/ComplEx_base_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |
| SimplE | src/scripts/SimplE/SimplE_eval.py | config/SimplE/SimplE_base_eval_Accel_20260131.yaml | 10.4.0.141/cuda 12.2/4090/cuda:0 |

| 模型 | MR | MRR | Hit@1 | Hit@3 | Hit@10 | Hit@30 | Hit@50 | duration |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| DistMult | 2779.742 | 0.455 | 0.288 | 0.612 | 0.659 | 0.696 | 0.718 | 32898.08468 |
| TransE | 1561.333 | 0.252 | 0.004 | 0.459 | 0.599 | 0.706 | 0.743 | 8742.7453 |
| TransH | 1630.578 | 0.25 | 0.002 | 0.456 | 0.596 | 0.698 | 0.737 | 15577.3326 |
| TransD | 1464.361 | 0.253 | 0.014 | 0.448 | 0.588 | 0.697 | 0.744 | 42292.1321 |
| RESCAL | 997.805 | 0.428 | 0.277 | 0.551 | 0.648 | 0.713 | 0.744 | 19065.5256 |
| ComplEx | 1969.156 | 0.459 | 0.306 | 0.599 | 0.659 | 0.694 | 0.714 | 14873.1312 |
| SimplE | 1225.994 | 0.176 | 0.094 | 0.219 | 0.307 | 0.41 | 0.469 | 38734.8969 |

| 模型 | MR(type) | MRR(type) | Hit@1(type) | Hit@3(type) | Hit@10(type) | Hit@30(type) | Hit@50(type) |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| DistMult | 587.641 | 0.457 | 0.289 | 0.615 | 0.663 | 0.7 | 0.722 |
| TransE | 549.013 | 0.261 | 0.016 | 0.465 | 0.602 | 0.709 | 0.746 |
| TransH | 586.918 | 0.259 | 0.016 | 0.461 | 0.599 | 0.7 | 0.739 |
| TransD | 535.106 | 0.256 | 0.017 | 0.451 | 0.589 | 0.699 | 0.746 |
| RESCAL | 414.066 | 0.429 | 0.277 | 0.552 | 0.649 | 0.715 | 0.745 |
| ComplEx | 601.485 | 0.463 | 0.31 | 0.602 | 0.663 | 0.7 | 0.721 |
| SimpIE | 870.839 | 0.177 | 0.095 | 0.22 | 0.309 | 0.413 | 0.472 |
