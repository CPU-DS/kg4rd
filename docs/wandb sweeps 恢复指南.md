# wandb sweeps 恢复指南

### Q1: 预知服务器将在接下来的某一段时间关闭

1. 使用 sweeps > controls 中的 stop 关闭当前 sweep, sweep 将在当前 runs 结束后不再产生新的 run;

2. 服务器重启后使用 sweeps > controls 中的 unpause 将 sweep 的状态变为 running;

3. 使用 `start_hpo_train` 函数时传入 `resume_sweep_id` 参数, 即当前的 `sweep_id`, sweep 会接着运行;

### Q2: 服务器意外关闭

1. 服务器意外关闭不会更改当前 sweep 的状态, 直接执行上述 step 3 即可；

2. 服务器意外关闭导致导致当前 run 中断 (适用于 Q2 或 Q1 中服务器当前 run 还没有结束的情况), 继续当前 run: 待补充;

### Q3: wandb 网页中数据被清空, 但本地 `wandb` 文件夹数据还存在

1. 运行 `wandb_recover_run.py` 中的 `recover_sweep_runs` 函数, 传入之前的 `sweep_id`, 会将之前该 sweep 中的 run 数据全部恢复, 但不会恢复 sweep;

2. 重新执行 `start_hpo_train` 函数时传入 `prior_runs` 参数将之前的 runs 和当前新的 sweep 关联起来;

3. 如果是使用 docker 部署的本地 wandb, 一定要加上 `--restart=always` 参数, 不然服务器重启后 wandb 容器有可能会消失;