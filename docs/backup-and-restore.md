# 备份与恢复说明

## 目标

本文档用于固化 `lobster-farm` 当前生产基线，便于后续：

- 回滚
- 迁移
- 排障
- 继续开发

当前阶段为：

`可长期运行的人工审核内容中台`

## 需要备份的内容

请优先备份以下内容：

### 1. 项目代码目录

- `src/`
- `services/`
- `scripts/`
- `docs/`
- `config/`
- `tests/`

### 2. 运行配置

- `.env`
- `.env.example`

说明：

- `.env` 中包含真实密钥
- 备份时请放入受控位置
- 不要将 `.env` 提交到仓库

### 3. 运行数据

- `exports/`
- `data/`
- `logs/`

### 4. systemd unit 文件

虚拟机内需要备份：

- `/etc/systemd/system/lobster-farm-run-dev.timer`
- `/etc/systemd/system/lobster-farm-run-dev-once.service`
- `/etc/systemd/system/lobster-farm-run-dev.service`

## 备份方法

### Windows 宿主机项目目录备份

可将项目目录整体打包：

```powershell
tar.exe -a -c -f lobster-farm-backup.zip lobster-farm
```

### 虚拟机内配置与数据备份

建议打包以下目录：

```bash
cd /opt
tar -czf lobster-farm-runtime-backup.tar.gz lobster-farm
```

### systemd unit 文件备份

```bash
sudo tar -czf lobster-farm-systemd-backup.tar.gz /etc/systemd/system/lobster-farm-run-dev.timer /etc/systemd/system/lobster-farm-run-dev-once.service /etc/systemd/system/lobster-farm-run-dev.service
```

## 恢复方法

### 1. 恢复项目目录

将项目目录恢复到：

```bash
/opt/lobster-farm
```

例如：

```bash
cd /opt
sudo tar -xzf lobster-farm-runtime-backup.tar.gz
sudo chown -R "$USER":"$USER" /opt/lobster-farm
```

### 2. 恢复 .env

将备份中的 `.env` 放回：

```bash
/opt/lobster-farm/.env
```

注意：

- 不要把真实密钥写入仓库
- 恢复后检查文件权限

### 3. 恢复 systemd timer / service

```bash
sudo tar -xzf lobster-farm-systemd-backup.tar.gz -C /
sudo systemctl daemon-reload
sudo systemctl enable --now lobster-farm-run-dev.timer
```

### 4. 重新执行 verify.sh

```bash
cd /opt/lobster-farm
source .venv/bin/activate
bash ./scripts/verify.sh
```

### 5. 恢复后检查

建议至少检查：

- `systemctl status lobster-farm-run-dev.timer --no-pager -l`
- `journalctl -u lobster-farm-run-dev-once.service -n 50 --no-pager`
- `cat /opt/lobster-farm/data/runtime/run-dev/status.env`

## 回滚建议

如果升级后出现问题，建议按以下顺序回滚：

1. 停止 timer
2. 恢复项目目录
3. 恢复 `.env`
4. 恢复 systemd unit
5. 重载 systemd
6. 执行 `verify.sh`

示例：

```bash
sudo systemctl disable --now lobster-farm-run-dev.timer
sudo systemctl daemon-reload
```
