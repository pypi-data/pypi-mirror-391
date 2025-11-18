# lfrppy 使用指南

lfrppy 提供一套轻量、可扩展的命令行工具，帮助你在 Linux 环境下部署与维护 FRP（Fast Reverse Proxy）客户端 `frpc` 和服务端 `frps`。命令通过内置注册中心管理，后续扩展新的功能时无需修改打包脚本。

---

## 安装

```bash
pip install lfrppy
```

若从源码构建，可在仓库根目录执行：

```bash
python pipups/lfrppy/pipup.py
```

---

## 命令总览

| 命令  | 说明             | 常用子命令                |
|-------|------------------|---------------------------|
| frpc  | 管理 FRP 客户端  | `deploy`、`cleanup`、`cd`、`start`、`stop`、`status`、`enable` |
| frps  | 管理 FRP 服务端  | `deploy`、`cleanup` |

查看帮助：

```bash
frpc --help
frpc <子命令> --help
frps --help
frps <子命令> --help
```

---

## frpc 部署与管理

### 快速部署

```bash
frpc deploy frpc \
  --service-user $(whoami) \
  --systemd-dir /etc/systemd/system
```

执行后会生成：

- `main.toml` 与 `frpc_full_example.toml`
- `logs/` 日志目录（默认空目录，可存放运行日志）
- `systemd/frpc@.service` 模板（ExecStart 指向包内二进制）
- `readme.txt` 使用说明

> frpc 可执行文件位于包内 `lfrppy/bin/frpc`，部署时不会复制到安装目录。

若进程具有写入 `/etc/systemd/system` 的权限，会自动复制模板并执行 `systemctl daemon-reload`。

### 进入部署目录

```bash
frpc cd          # 输出部署目录并提示手动执行 cd
frpc cd --print  # 仅打印部署路径
```

### 管理实例（底层调用 systemctl）

```bash
frpc start example    # ≈ sudo systemctl start frpc@example
frpc enable example   # ≈ sudo systemctl enable frpc@example
frpc status example   # ≈ sudo systemctl status frpc@example
frpc restart example  # ≈ sudo systemctl restart frpc@example
frpc stop example     # ≈ sudo systemctl stop frpc@example
```

> 以上命令实质调用 systemctl，必要时请配合 sudo 使用。

### 清理部署

```bash
frpc cleanup \
  --install-dir ~/frp/frpc \
  --systemd-dir /etc/systemd/system \
  --remove-default-config
```

常用参数：

- `--keep-dir`：保留安装目录，仅停止服务
- `--keep-service`：保留 systemd 模板和状态
- `--instance NAME`：停止/禁用 `frpc@NAME`（可重复）
- `--config PATH`：删除额外配置文件（可重复）
- `--remove-default-config`：删除 `/etc/frp/frpc.ini`

---

## frps 部署与清理

部署命令：

```bash
frps deploy frps \
  --systemd-dir /etc/systemd/system
```

生成内容包括 `main.toml`、`frps_full_example.toml`、`logs/` 目录及 `readme.txt`；`frps` 可执行文件位于包内 `lfrppy/bin/frps`，若具备权限也会自动写入 systemd 模板。

清理命令：

```bash
frps cleanup \
  --install-dir ~/frp/frps \
  --systemd-dir /etc/systemd/system \
  --remove-default-config
```

参数与客户端类似（无需指定实例）。

---

## 常用选项

- `<install-dir>`：部署目录位置（默认 `~/frp/frpc` 或 `~/frp/frps`，可在 deploy 命令中直接作为第一个参数传入）
- `--service-user USER`：systemd 运行账号（默认当前用户）
- `--systemd-dir PATH`：systemd 模板目标路径（默认 `/etc/systemd/system`）
- `--overwrite`：允许覆盖已有文件
- `--no-service`：仅生成模板，不写入 systemd 目录

如需手动处理模板，可执行：

```bash
sudo cp ~/frp/frpc/systemd/frpc@.service /etc/systemd/system/
sudo systemctl daemon-reload
```

---

## 扩展 lfrppy

1. 在 `lfrppy/<module>/__init__.py` 中实现业务逻辑和 CLI 入口。
2. 使用 `register_command(...)` 注册命令，补充 `usage`、`examples`、`notes` 等信息。
3. 发布前运行 `pipups/lfrppy/pipup.py`，重新生成 console_scripts。

---

## 常见问题

**需要 sudo 吗？** 在写入 `/etc/systemd/system` 或启停服务时通常需要 sudo。可以使用 `--no-service` 跳过自动安装，再自行处理。\
**如何完全卸载 FRP？** 执行对应的 `cleanup` 命令删除目录与模板，然后运行 `sudo systemctl daemon-reload`。\
**能否替换内置二进制？** 可以。将 `lfrppy/bin/` 下的 `frpc` 或 `frps` 替换为自定义版本后重新打包即可。

---

祝使用顺利！

