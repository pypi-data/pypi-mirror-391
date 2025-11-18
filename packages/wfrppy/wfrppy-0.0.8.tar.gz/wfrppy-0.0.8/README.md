# wfrppy 使用指南

wfrppy 提供一组 Windows 命令行工具，用于部署和管理 FRP（Fast Reverse Proxy）的 `frpc` / `frps`。通过封装计划任务导入、配置编辑与清理操作，可在 Windows 上获得接近 systemd 的守护体验。

---

## 安装

```powershell
pip install wfrppy
```

或在仓库根目录打包：

```powershell
python pipups/wfrppy/pipup.py
```

---

## 命令概览

| 命令 | 作用 | 常用子命令 |
|------|------|------------|
| frpc | 管理 frpc 部署 | `deploy`、`cleanup`、`list`、`addtask`、`rmtask`、`edit` |
| frps | 管理 frps 部署 | `deploy`、`cleanup`、`list`、`addtask`、`rmtask`、`edit` |

查看帮助：

```powershell
frpc --help
frps --help
frpc <子命令> --help
frps <子命令> --help
```

---

## 快速部署

```powershell
frpc deploy                 # 默认部署到 ~/frp/frpc
frps deploy                 # 默认部署到 ~/frp/frps
```

部署完成后会生成：

- `main.toml`：默认配置模板
- `frpc_example.toml`：额外的 frpc 示例配置（若提供）
- `logs/`：日志目录
- `readme.txt`：离线说明

首次执行 `frpc addtask main` 或 `frps addtask main` 时，如未检测到计划任务会自动创建；该步骤需要管理员权限。

---

## 常用操作

```powershell
frpc list            # 查看配置及计划任务状态
frpc edit main       # 使用记事本编辑 main.toml
frpc show main       # 查看配置内容
frpc addtask main    # 基于模板导入计划任务
frpc rmtask main     # 删除对应计划任务
frpc cleanup         # 清理部署目录与计划任务

frps list            # 查看 frps 配置及计划任务状态
frps edit main       # 使用记事本编辑 main.toml
frps addtask main    # 导入 frps 计划任务
frps rmtask main     # 删除 frps 计划任务
frps cleanup         # 清理部署目录与计划任务
```

两套命令均遵循 `\frp\frp[c|s]-<名称>` 的计划任务命名，与 `<名称>.toml` 配置一一对应。

---

## 注意事项

- 计划任务操作需在管理员 PowerShell 或 CMD 中执行，避免因权限不足导致导入失败。
- 若计划任务导入失败，可在管理员环境下再次执行 `frpc addtask <名称>` 或 `frps addtask <名称>` 查看详细日志。
- 部署目录默认位于 `~/frp/<组件>`，可通过 `deploy` 命令自定义路径。
- `cleanup --keep-dir` 可保留部署目录；`cleanup --keep-service` 可保留已创建的计划任务（命令名称保持向后兼容）。

---

祝在 Windows 平台顺利运行 FRP！
