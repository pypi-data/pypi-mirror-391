# 开发指南

## 项目结构

```
serverless-devs-python/
├── .github/
│   └── workflows/
│       ├── publish.yml       # 自动发布到 PyPI
│       └── test.yml          # 自动测试
├── serverless_devs/          # Python 包目录
│   ├── __init__.py          # 包初始化
│   ├── __main__.py          # 命令行入口
│   └── installer.py         # 安装器（使用官方脚本）
├── setup.py                 # 安装配置
├── pyproject.toml          # 项目元数据
├── README.md               # 项目说明
├── LICENSE                 # 许可证
├── MANIFEST.in             # 打包清单
└── DEVELOPMENT.md          # 本文件
```

## 本地开发

### 1. 克隆项目

```bash
cd serverless-devs-python
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 安装开发模式

```bash
pip install -e .
```

### 4. 测试安装

```bash
# 测试安装器
s-install

# 测试命令
s --version
```

## 版本管理

本项目的版本号只需要修改 `setup.py` 和 `serverless_devs/__init__.py` 中的 Python 包版本。

Serverless Devs 本身的版本会自动获取最新版，无需手动更新。

需要修改的文件：
1. `setup.py` - `version='1.0.x'`
2. `serverless_devs/__init__.py` - `__version__ = "1.0.x"`

## GitHub Actions 自动发布

### 配置步骤

1. **获取 PyPI API Token**
   - 访问 https://pypi.org/manage/account/
   - 生成 API Token
   - 复制 token（格式：`pypi-...`）

2. **配置 GitHub Secrets**
   - 进入 GitHub 仓库的 Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: 粘贴你的 PyPI token
   - 点击 "Add secret"

3. **发布新版本**

   ```bash
   # 1. 更新版本号
   vim setup.py  # 修改 version
   vim serverless_devs/__init__.py  # 修改 __version__
   
   # 2. 提交更改
   git add .
   git commit -m "chore: bump version to 1.0.x"
   git push
   
   # 3. 创建并推送标签
   git tag v1.0.x
   git push origin v1.0.x
   ```

4. **自动发布流程**
   - GitHub Actions 会自动检测到新标签
   - 自动构建 Python 包
   - 自动发布到 PyPI
   - 自动创建 GitHub Release

### 手动触发发布

也可以在 GitHub Actions 页面手动触发：

1. 进入 Actions 标签页
2. 选择 "Publish to PyPI" workflow
3. 点击 "Run workflow"
4. 选择分支并运行

## 本地手动发布（不推荐）

如果需要手动发布：

```bash
# 1. 清理旧文件
rm -rf build/ dist/ *.egg-info

# 2. 安装构建工具
pip install build twine

# 3. 构建
python -m build

# 4. 检查
twine check dist/*

# 5. 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 6. 上传到 PyPI（正式）
twine upload dist/*
```

## 测试安装

### 测试本地构建

```bash
# 构建
python -m build

# 在新环境中测试
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate
pip install dist/serverless_devs-*.whl

# 测试
s-install
s --version
```

### 测试 TestPyPI 版本

```bash
pip install -i https://test.pypi.org/simple/ serverless-devs
s-install
s --version
```

### 测试正式 PyPI 版本

```bash
pip install serverless-devs
s --version
```

## 使用国内镜像

安装时使用国内镜像加速：

### Linux/macOS

```bash
export USE_MIRROR=1
s-install
```

### Windows

```cmd
set USE_MIRROR=1
s-install
```

或在 PowerShell 中：

```powershell
$env:USE_MIRROR=1
s-install
```

## 故障排查

### 1. 安装失败

```bash
# 查看详细日志
s-install

# 或直接使用 npm
npm install -g @serverless-devs/s
```

### 2. 命令找不到

```bash
# 重新加载环境变量
source ~/.bashrc  # 或 ~/.zshrc

# 检查 PATH
echo $PATH

# 查找 s 命令位置
which s
```

### 3. 权限问题

```bash
# Linux/macOS 使用 sudo
sudo pip install serverless-devs

# 或安装到用户目录
pip install --user serverless-devs
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## License

MIT License
