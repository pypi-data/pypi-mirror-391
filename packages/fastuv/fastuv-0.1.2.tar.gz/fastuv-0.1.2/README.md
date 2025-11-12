# fastuv: 快速 uv 安装器

[![PyPI version](https://badge.fury.io/py/fastuv.svg)](https://badge.fury.io/py/fastuv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

fastuv 是一个通过 PyPI 分发的 **uv** 安装器，专为国内用户优化。它自动配置国内镜像源，实现用户级别的快速安装。

## ✨ 特性

- [开始] **一键安装**：`pip install fastuv && fastuv install`
- 🇨🇳 **国内优化**：自动配置清华源等国内镜像，大幅提升下载速度
- 👤 **用户级别**：无需 sudo 权限，安装到用户目录
- 🔄 **自动配置**：自动设置 PATH 和 conda 环境联动
- [清理] **完整卸载**：支持 `fastuv uninstall` 完全清理

## [开始] 快速开始

### 安装 fastuv

```bash
pip install fastuv
```

### 安装 uv

```bash
fastuv install
```

安装完成后，uv 将自动配置国内镜像源，你可以直接使用：

```bash
# 重启终端或 source 配置文件
source ~/.bashrc  # 或 source ~/.zshrc

# 现在可以使用 uv 了
uv --version
uv pip install requests
```

## [配置] 高级用法

### 自定义安装选项

```bash
# 指定版本
fastuv install --version 0.5.0

# 指定下载代理
fastuv install --proxy https://ghproxy.com

# 指定 PyPI 镜像源
fastuv install --mirror https://mirrors.aliyun.com/pypi/simple/

# 不安装 conda 环境联动
fastuv install --no-hooks
```

### 完全卸载

```bash
# 只卸载 uv
fastuv uninstall

# 卸载并清理所有配置和缓存
fastuv uninstall --all
```

## [安装包] 安装过程中做了什么

`fastuv install` 会自动完成以下步骤：

1. **下载官方 uv 安装脚本**
2. **注入国内镜像配置**
   - PyPI 镜像：`https://pypi.tuna.tsinghua.edu.cn/simple/`
   - Python 下载代理：`https://ghfast.top`
3. **执行用户级别安装**（安装到 `~/.local/bin/`）
4. **配置环境变量**
   - 添加 `~/.local/bin` 到 PATH
5. **创建配置文件**（`~/.config/uv/uv.toml`）
6. **可选：安装 conda 环境联动 hooks**

## [检查] 配置文件

fastuv 会自动创建 `~/.config/uv/uv.toml`：

```toml
python-install-mirror = "https://ghfast.top/https://github.com/astral-sh/python-build-standalone/releases/download"

[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple/"
default = true
```

## [协作] Conda 环境联动

如果你是 conda/mamba 用户，fastuv 会自动配置环境联动，让 uv 能够识别和使用当前激活的 conda 环境。

## [安全] 安全说明

- fastuv 下载的是 uv 官方安装脚本，只注入镜像配置
- 所有修改都在用户目录下进行，不会影响系统
- 完整开源，代码透明

## 🆚 与其他方案对比

| 方案 | 安装方式 | 镜像配置 | 用户级别 | conda 联动 |
|------|----------|----------|----------|------------|
| **fastuv** | `pip install + fastuv install` | [完成] 自动 | [完成] 是 | [完成] 自动 |
| 官方 uv | `curl | sh` | [错误] 手动 | [错误] 需要 sudo | [错误] 手动 |
| uv-custom | `curl | sh` | [完成] 自动 | [完成] 是 | [完成] 可选 |

## 🐛 故障排除

### 安装失败

```bash
# 检查网络连接
fastuv install --proxy https://ghproxy.com

# 使用不同镜像
fastuv install --mirror https://mirrors.aliyun.com/pypi/simple/
```

### uv 命令未找到

```bash
# 手动添加 PATH（临时）
export PATH="$HOME/.local/bin:$PATH"

# 或重启终端让配置生效
source ~/.bashrc
```

### 查看配置

```bash
# 检查 uv 配置
cat ~/.config/uv/uv.toml

# 检查 uv 版本
uv --version
```

## [协作] 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [uv](https://github.com/astral-sh/uv) - 极速的 Python 包管理器
- [uv-custom](https://gitee.com/wangnov/uv-custom) - 提供了优秀的镜像配置模板