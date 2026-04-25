# run-dev 常驻服务说明

## 目标

本文档说明 `lobster-farm` 在虚拟机内以 `systemd` 常驻运行时的推荐方案、日志位置、状态查看方式和回滚方式。

## 推荐方案

推荐使用 `systemd timer`：

- `lobster-farm-run-dev-once.service`
- `lobster-farm-run-dev.timer`

原因：

- 调度由 `systemd` 负责，结构更清晰。
- 每轮执行是独立的一次任务，便于排错和观察。
- 结合 `Persistent=true`，虚拟机重启后可补跑错过的周期。
- 配合脚本内 `flock`，可避免重入。

## 兼容方案

保留 `lobster-farm-run-dev.service`：

- 基于 `while + sleep`
- 适合快速试运行
- 不作为长期运行首选

## 环境变量加载

常驻执行统一从项目根目录 `.env` 显式加载：

- `scripts/vm/prepare-systemd-env.sh` 会先把 `.env` 清洗成 `data/runtime/run-dev/systemd.env`
- `systemd unit` 通过 `EnvironmentFile=-/opt/lobster-farm/data/runtime/run-dev/systemd.env` 显式加载
- `scripts/vm/run-dev-managed.sh` 也会再次加载清洗后的环境文件

这样可以保证：

- 手工执行与常驻执行环境更一致
- 切换 `RUN_MODE`、飞书配置、视频配置时不需要改 unit 文件
- `.env` 即使来自 Windows，带有 BOM 或 CRLF，也不会导致 systemd 加载失败

## 防重入机制

`run-dev-managed.sh` 使用以下锁文件：

- `data/runtime/run-dev/run-dev.lock`

实现方式：

- 使用 `flock -n`
- 若上一次任务尚未结束，则本轮直接跳过并写日志

## 运行记录

运行记录位于：

- `data/runtime/run-dev/status.env`
- `data/runtime/run-dev/last_success.log`
- `data/runtime/run-dev/last_failure.log`
- `data/runtime/run-dev/systemd.env`

关键字段：

- `LAST_RUN_AT`
- `LAST_RUN_STATUS`
- `LAST_EXIT_CODE`
- `FAILURE_COUNT`

## 失败告警预留

当前失败告警脚本：

- `scripts/vm/notify-failure.sh`

当前行为：

- 在连续失败达到阈值后输出明确日志
- 预留后续飞书告警接入点
- 默认不主动发送外部告警

## 查看状态命令

查看 timer：

```bash
sudo systemctl status lobster-farm-run-dev.timer --no-pager -l
```

查看单次 service：

```bash
sudo systemctl status lobster-farm-run-dev-once.service --no-pager -l
```

查看兼容 loop service：

```bash
sudo systemctl status lobster-farm-run-dev.service --no-pager -l
```

查看 timer 日志：

```bash
sudo journalctl -u lobster-farm-run-dev.timer -n 50 --no-pager
```

查看执行日志：

```bash
sudo journalctl -u lobster-farm-run-dev-once.service -n 100 --no-pager
```

查看最近失败日志：

```bash
cat /opt/lobster-farm/data/runtime/run-dev/last_failure.log
```

## 推荐启用方式

启用 timer：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lobster-farm-run-dev.timer
```

如需停用旧 loop service：

```bash
sudo systemctl disable --now lobster-farm-run-dev.service
```

## 回滚方式

停用 timer 并恢复旧 service：

```bash
sudo systemctl disable --now lobster-farm-run-dev.timer
sudo systemctl enable --now lobster-farm-run-dev.service
```
