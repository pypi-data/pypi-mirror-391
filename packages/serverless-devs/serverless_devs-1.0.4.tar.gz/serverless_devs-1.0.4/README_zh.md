# Serverless Devs - Python 安装包

[![PyPI version](https://img.shields.io/pypi/v/serverless-devs.svg)](https://pypi.org/project/serverless-devs/)
[![Python Versions](https://img.shields.io/pypi/pyversions/serverless-devs.svg)](https://pypi.org/project/serverless-devs/)
[![License](https://img.shields.io/pypi/l/serverless-devs.svg)](https://github.com/Serverless-Devs/Serverless-Devs/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Serverless-Devs/Serverless-Devs.svg?style=social)](https://github.com/Serverless-Devs/Serverless-Devs)

简体中文 | [English](./README.md)

通过 Python pip 安装 Serverless Devs 开发者工具（自动安装最新版本）。

## 特性

- ✅ 自动安装最新版 Serverless Devs
- ✅ 自动处理 Node.js 环境依赖
- ✅ 支持 Windows、Linux、macOS
- ✅ 一键安装，开箱即用
- 🌍 支持国内镜像加速

## 安装

### 使用 pip 安装

```bash
pip install serverless-devs
```

### 使用国内镜像加速

```bash
# 清华镜像
pip install serverless-devs -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像
pip install serverless-devs -i https://mirrors.aliyun.com/pypi/simple/
```

安装过程会自动：
1. 下载并执行 Serverless Devs 官方安装脚本
2. 自动检测并安装 Node.js（如果需要）
3. 安装最新版本的 Serverless Devs

## 使用

安装完成后，可以直接使用 `s` 命令：

```bash
# 查看版本
s --version

# 查看帮助
s --help

# 配置密钥
s config add

# 初始化项目
s init

# 部署项目
s deploy
```

## 手动安装/重新安装

如果自动安装失败，或需要重新安装最新版本：

```bash
s-install
```

使用国内镜像加速：

```bash
# Linux/macOS
export USE_MIRROR=1
s-install

# Windows CMD
set USE_MIRROR=1
s-install

# Windows PowerShell
$env:USE_MIRROR=1
s-install
```

## 卸载

```bash
pip uninstall serverless-devs
```

> 注意：这只会卸载 Python 包装器，不会卸载 Serverless Devs 本身。
> 如需完全卸载，请手动删除 Serverless Devs：
> - Linux/macOS: `rm -rf ~/.s`
> - Windows: 删除 `C:\Users\<用户名>\.s` 目录

## 支持的平台

- ✅ Windows (x64)
- ✅ Linux (x64)
- ✅ macOS (x64/arm64)

## 环境要求

- Python 3.7+
- 互联网连接（用于下载安装脚本）

## 工作原理

本包通过 pip 安装后，会执行 Serverless Devs 官方安装脚本：

```bash
curl -o- -L https://cli.serverless-devs.com/install.sh | bash
```

该脚本会：
1. 检测系统环境
2. 自动安装 Node.js（如果需要）
3. 通过 npm 安装最新版 Serverless Devs

## 常见问题

### Q: 安装失败怎么办？

A: 请尝试以下方法：
```bash
# 1. 手动运行安装
s-install

# 2. 使用国内镜像
export USE_MIRROR=1  # Linux/macOS
s-install

# 3. 直接使用官方安装脚本
curl -o- -L https://cli.serverless-devs.com/install.sh | bash
```

### Q: 如何更新到最新版本？

A: 重新运行安装命令：
```bash
s-install
```

或使用 npm：
```bash
npm update -g @serverless-devs/s
```

### Q: 如何查看安装的版本？

A: 运行：
```bash
s --version
```

### Q: Windows 下 PowerShell 执行策略问题

A: 以管理员身份运行 PowerShell 并执行：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: 国内网络环境安装慢或失败

A: 使用国内镜像：
```bash
# 方法1: 使用环境变量
export USE_MIRROR=1
s-install

# 方法2: 使用 npm 镜像
npm config set registry https://registry.npmmirror.com
npm install -g @serverless-devs/s
```

## 相关链接

- 官方网站: https://www.serverless-devs.com/
- GitHub: https://github.com/Serverless-Devs/Serverless-Devs
- 文档中心: https://docs.serverless-devs.com/
- 应用中心: https://registry.serverless-devs.com/
- 钉钉交流群: 33947367

## 开源协议

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
