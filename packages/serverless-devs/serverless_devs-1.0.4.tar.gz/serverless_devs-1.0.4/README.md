# Serverless Devs - Python Package

[![PyPI version](https://img.shields.io/pypi/v/serverless-devs.svg)](https://pypi.org/project/serverless-devs/)
[![Python Versions](https://img.shields.io/pypi/pyversions/serverless-devs.svg)](https://pypi.org/project/serverless-devs/)
[![License](https://img.shields.io/pypi/l/serverless-devs.svg)](https://github.com/Serverless-Devs/Serverless-Devs/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Serverless-Devs/Serverless-Devs.svg?style=social)](https://github.com/Serverless-Devs/Serverless-Devs)

[简体中文](./README_zh.md) | English

Install Serverless Devs developer tools via Python pip (automatically installs the latest version).

## Features

- ✅ Automatically installs the latest version of Serverless Devs
- ✅ Automatically handles Node.js environment dependencies
- ✅ Supports Windows, Linux, macOS
- ✅ One-click installation, ready to use
- 🌍 Supports domestic mirror acceleration

## Installation

### Install via pip

```bash
pip install serverless-devs
```

### Use domestic mirror for acceleration

```bash
# China mirror
pip install serverless-devs -i https://pypi.tuna.tsinghua.edu.cn/simple
```

The installation process will automatically:
1. Download and run the official Serverless Devs installation script
2. Detect and install Node.js (if needed)
3. Install the latest version of Serverless Devs

## Usage

After installation, you can use the `s` command directly:

```bash
# Check version
s --version

# View help
s --help

# Configure credentials
s config add

# Initialize project
s init

# Deploy project
s deploy
```

## Manual Installation/Reinstallation

If automatic installation fails or you need to reinstall the latest version:

```bash
s-install
```

Use domestic mirror:

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

## Uninstallation

```bash
pip uninstall serverless-devs
```

> Note: This only uninstalls the Python wrapper, not Serverless Devs itself.
> To completely uninstall, manually delete Serverless Devs:
> - Linux/macOS: `rm -rf ~/.s`
> - Windows: Delete `C:\Users\<username>\.s` directory

## Supported Platforms

- ✅ Windows (x64)
- ✅ Linux (x64)
- ✅ macOS (x64/arm64)

## Requirements

- Python 3.7+
- Internet connection (for downloading installation script)

## How It Works

After installing via pip, this package executes the official Serverless Devs installation script:

```bash
curl -o- -L https://cli.serverless-devs.com/install.sh | bash
```

The script will:
1. Detect system environment
2. Automatically install Node.js (if needed)
3. Install the latest version of Serverless Devs via npm

## Troubleshooting

### Q: Installation failed?

A: Try these solutions:
```bash
# 1. Run installation manually
s-install

# 2. Use domestic mirror
export USE_MIRROR=1  # Linux/macOS
s-install

# 3. Use official installation script directly
curl -o- -L https://cli.serverless-devs.com/install.sh | bash
```

### Q: How to update to the latest version?

A: Rerun the installation command:
```bash
s-install
```

Or use npm:
```bash
npm update -g @serverless-devs/s
```

### Q: How to check the installed version?

A: Run:
```bash
s --version
```

### Q: PowerShell execution policy issue on Windows

A: Run PowerShell as administrator and execute:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Links

- Official Website: https://www.serverless-devs.com/
- GitHub: https://github.com/Serverless-Devs/Serverless-Devs
- Documentation: https://docs.serverless-devs.com/
- Registry: https://registry.serverless-devs.com/
- DingTalk Group: 33947367

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
