# 运维手册

## 当前阶段

当前系统定位为：

`可长期运行的人工审核内容中台`

当前不具备：

- 抖音自动发布
- 视频号自动发布
- 任意平台自动发稿

## 常用命令

### 查看 timer 状态

```bash
sudo systemctl status lobster-farm-run-dev.timer --no-pager -l
```

### 查看最近执行日志

```bash
sudo journalctl -u lobster-farm-run-dev-once.service -n 100 --no-pager
```

### 查看待审核任务

```bash
python ./services/orchestrator/src/list_review_tasks.py --review-status pending_review
```

### 写回审核结果

```bash
python ./services/orchestrator/src/review.py --task-id "task_xxx" --review-status approved --reviewed-by "alice" --review-note "通过"
```

### 查看待发布队列

```bash
cat /opt/lobster-farm/data/state/publish_queue.json
```

### 停止常驻任务

```bash
sudo systemctl stop lobster-farm-run-dev.timer
```

### 重启常驻任务

```bash
sudo systemctl restart lobster-farm-run-dev.timer
```

## 常见故障

### 飞书发送失败

排查顺序：

1. 检查 `.env`
2. 检查 `RUN_MODE` 与 `FEISHU_ADAPTER`
3. 检查 `journalctl -u lobster-farm-run-dev-once.service`
4. 检查任务目录下的 `review_message.json`

### .env 读取失败

常见原因：

- 文件不存在
- Windows CRLF/BOM 导致解析异常

排查：

```bash
cat /opt/lobster-farm/data/runtime/run-dev/systemd.env
```

### 任务未生成

排查：

```bash
cat /opt/lobster-farm/data/state/workflow_state.json
ls -la /opt/lobster-farm/exports/pending_review
```

### timer 未触发

排查：

```bash
sudo systemctl status lobster-farm-run-dev.timer --no-pager -l
systemctl list-timers --all --no-pager | grep 'lobster-farm-run-dev'
```

### 磁盘空间不足

排查：

```bash
df -h
du -sh /opt/lobster-farm/exports
du -sh /opt/lobster-farm/data
```

### Python 虚拟环境损坏

处理步骤：

```bash
cd /opt/lobster-farm
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 建议巡检项

建议每天至少检查：

- timer 是否 active
- 最近一次运行是否 success
- 待审核任务数量是否异常堆积
- `publish_queue.json` 是否持续增长
