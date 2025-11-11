"""
Serverless Devs 安装器
使用官方安装脚本自动安装最新版本（包含 Node.js 环境）
支持非交互式自动安装、跨平台兼容
"""

import os
import platform
import subprocess
import sys
import tempfile
import shutil
import stat
from pathlib import Path

# 官方安装脚本 URL
INSTALL_SCRIPT_URL = "https://cli.serverless-devs.com/install.sh"
INSTALL_SCRIPT_MIRROR = "https://registry.npmmirror.com/-/binary/serverless-devs/install.sh"

def is_windows():
    """判断是否为 Windows 系统"""
    return platform.system().lower() == 'windows'

def is_command_available(command):
    """检查命令是否可用"""
    return shutil.which(command) is not None

def check_existing_installation():
    """检查是否已安装 Serverless Devs"""
    if is_command_available('s'):
        try:
            result = subprocess.run(
                ['s', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version
        except:
            pass
    return False, None

def create_wrapper_script():
    """在 Python Scripts/bin 目录创建 s 命令的包装脚本"""
    try:
        # 获取 Python Scripts/bin 目录
        if sys.platform == 'win32':
            scripts_dir = Path(sys.prefix) / 'Scripts'
            wrapper_file = scripts_dir / 's.bat'
            
            # Windows 批处理包装器
            wrapper_content = '''@echo off
where /q npm >nul 2>&1
if errorlevel 1 (
    echo Error: npm not found. Please install Node.js.
    exit /b 1
)

for /f "delims=" %%i in ('npm root -g 2^>nul') do set NPM_ROOT=%%i
if "%NPM_ROOT%"=="" (
    echo Error: Failed to get npm root directory
    exit /b 1
)

set S_BIN=%NPM_ROOT%\\@serverless-devs\\s\\bin\\s.js
if exist "%S_BIN%" (
    node "%S_BIN%" %*
) else (
    where /q s >nul 2>&1
    if not errorlevel 1 (
        s %*
    ) else (
        echo Error: Serverless Devs not found. Please run: s-install
        exit /b 1
    )
)
'''
        else:
            scripts_dir = Path(sys.prefix) / 'bin'
            wrapper_file = scripts_dir / 's'
            
            # Unix shell 包装器
            wrapper_content = '''#!/bin/bash
if ! command -v npm &> /dev/null; then
    echo "Error: npm not found. Please install Node.js."
    exit 1
fi

NPM_ROOT=$(npm root -g 2>/dev/null)
if [ -z "$NPM_ROOT" ]; then
    echo "Error: Failed to get npm root directory"
    exit 1
fi

S_BIN="$NPM_ROOT/@serverless-devs/s/bin/s.js"

if [ -f "$S_BIN" ]; then
    exec node "$S_BIN" "$@"
elif command -v s &> /dev/null; then
    exec s "$@"
else
    echo "Error: Serverless Devs not found. Please run: s-install"
    exit 1
fi
'''
        
        scripts_dir.mkdir(parents=True, exist_ok=True)
        wrapper_file.write_text(wrapper_content, encoding='utf-8')
        
        # Unix: 添加执行权限
        if sys.platform != 'win32':
            current_permissions = wrapper_file.stat().st_mode
            wrapper_file.chmod(current_permissions | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"[OK] Wrapper script created: {wrapper_file}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create wrapper: {e}")
        return False

def setup_path_instructions():
    """显示 PATH 配置说明"""
    system = platform.system().lower()
    
    if system == 'windows':
        npm_path = os.path.expandvars(r'%APPDATA%\npm')
        
        print("\n" + "="*60)
        print("PATH Configuration (if 's' command not found)")
        print("="*60)
        print(f"\nAdd this path to your system PATH:")
        print(f"  {npm_path}")
        print("\nMethod 1 - GUI:")
        print("  1. Press Win + X, select 'System'")
        print("  2. Click 'Advanced system settings'")
        print("  3. Click 'Environment Variables'")
        print("  4. Under 'User variables', select 'Path', click 'Edit'")
        print("  5. Click 'New', paste the path above")
        print("  6. Click 'OK' and restart your terminal")
        print("\nMethod 2 - PowerShell (Run as Administrator):")
        print('  $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")')
        print(f'  [Environment]::SetEnvironmentVariable("Path", "$currentPath;{npm_path}", "User")')
        print("="*60)
        
    else:
        shell_rc = None
        home = os.path.expanduser("~")
        
        # 检测 shell 配置文件
        if os.path.exists(os.path.join(home, ".zshrc")):
            shell_rc = "~/.zshrc"
        elif os.path.exists(os.path.join(home, ".bashrc")):
            shell_rc = "~/.bashrc"
        else:
            shell_rc = "~/.bashrc or ~/.zshrc"
        
        print("\n" + "="*60)
        print("Almost Done!")
        print("="*60)
        print("\nTo activate 's' command, run:")
        print(f"  source {shell_rc}")
        print("  # Or simply restart your terminal")
        print("\nIf 's' command is still not found, add to your PATH:")
        print("  export PATH=\"$HOME/.s/bin:$PATH\"")
        print(f"  # Add this line to your {shell_rc}")
        print("="*60)

def install_on_windows(non_interactive=False):
    """在 Windows 上安装 Serverless Devs"""
    if not non_interactive:
        print("Detected Windows system...")
    
    # 检查 npm 是否可用
    if not is_command_available('npm'):
        print("\n[FAIL] npm not found")
        print("Please install Node.js first:")
        print("  Download: https://nodejs.org/")
        return False
    
    if not non_interactive:
        print("\nInstalling Serverless Devs via npm...")
    
    try:
        # 设置环境变量使用国内镜像
        env = os.environ.copy()
        use_mirror = env.get('USE_MIRROR', '').lower() in ['1', 'true', 'yes']
        
        if use_mirror:
            env['NPM_CONFIG_REGISTRY'] = 'https://registry.npmmirror.com'
            if not non_interactive:
                print("(Using China mirror for acceleration)")
        
        result = subprocess.run(
            ['npm', 'install', '-g', '@serverless-devs/s'],
            env=env,
            capture_output=non_interactive,
            text=True
        )
        
        if result.returncode == 0:
            if not non_interactive:
                print("\n[OK] Installation successful!")
            return True
        else:
            print("\n[FAIL] npm installation failed")
            if result.stderr and not non_interactive:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Installation failed: {e}")
        return False

def install_on_unix(non_interactive=False):
    """在 Unix 系统（Linux/macOS）上安装 Serverless Devs"""
    system = platform.system()
    
    if not non_interactive:
        print(f"Detected {system} system...")
    
    # 检查必要的命令
    if not is_command_available('curl') and not is_command_available('wget'):
        print("\n[FAIL] curl or wget is required")
        print("Please install: sudo apt-get install curl  # Debian/Ubuntu")
        print("               sudo yum install curl       # CentOS/RHEL")
        return False
    
    if not is_command_available('bash'):
        print("\n[FAIL] bash is required")
        return False
    
    # 选择下载工具
    download_cmd = 'curl' if is_command_available('curl') else 'wget'
    
    # 选择安装脚本 URL
    use_mirror = os.environ.get('USE_MIRROR', '').lower() in ['1', 'true', 'yes']
    script_url = INSTALL_SCRIPT_MIRROR if use_mirror else INSTALL_SCRIPT_URL
    
    if use_mirror and not non_interactive:
        print("Using China mirror for acceleration...")
    
    if not non_interactive:
        print(f"\nDownloading installation script from: {script_url}")
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            temp_script = f.name
        
        # 下载安装脚本
        if download_cmd == 'curl':
            download_result = subprocess.run(
                ['curl', '-fsSL', script_url, '-o', temp_script],
                capture_output=True,
                text=True,
                timeout=60
            )
        else:
            download_result = subprocess.run(
                ['wget', '-q', script_url, '-O', temp_script],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if download_result.returncode != 0:
            print(f"\n[FAIL] Download failed: {download_result.stderr}")
            if not use_mirror:
                print("\nTip: Try using China mirror:")
                print("  export USE_MIRROR=1")
                print("  s-install")
            return False
        
        if not non_interactive:
            print("[OK] Download complete")
        
        # 添加执行权限
        os.chmod(temp_script, 0o755)
        
        # 执行安装脚本
        if not non_interactive:
            print("\nInstalling Serverless Devs...")
            print("="*60)
        
        env = os.environ.copy()
        if use_mirror:
            env['NPM_REGISTRY'] = 'https://registry.npmmirror.com'
        
        install_result = subprocess.run(
            ['bash', temp_script],
            env=env,
            capture_output=non_interactive,
            text=True
        )
        
        # 清理临时文件
        try:
            os.unlink(temp_script)
        except:
            pass
        
        if install_result.returncode == 0:
            if not non_interactive:
                print("="*60)
                print("[OK] Installation successful!")
            return True
        else:
            if not non_interactive:
                print("="*60)
            print("[FAIL] Installation failed")
            if non_interactive and install_result.stderr:
                print(install_result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("\n[FAIL] Download timeout, please check your network")
        return False
    except Exception as e:
        print(f"\n[FAIL] Installation error: {e}")
        return False

def install_serverless_devs(non_interactive=False):
    """
    安装 Serverless Devs
    
    Args:
        non_interactive: 是否非交互模式（自动安装，不询问）
    
    Returns:
        bool: 是否安装成功
    """
    if not non_interactive:
        print("="*60)
        print("Serverless Devs Installer")
        print("="*60)
    
    # 检查是否已安装
    is_installed, version = check_existing_installation()
    if is_installed:
        if non_interactive:
            # 非交互模式：已安装则跳过
            print(f"[OK] Serverless Devs already installed: {version}")
            return True
        else:
            # 交互模式：询问是否重新安装
            print(f"\nDetected existing installation: {version}")
            try:
                response = input("\nReinstall? (y/N): ")
                if response.lower() != 'y':
                    print("Installation skipped")
                    return True
            except (EOFError, KeyboardInterrupt):
                print("\nInstallation cancelled")
                return False
            print()
    
    # 根据系统选择安装方式
    if is_windows():
        success = install_on_windows(non_interactive)
    else:
        success = install_on_unix(non_interactive)
    
    if success:
        # 验证安装
        if not non_interactive:
            print("\nVerifying installation...")
        
        # 等待一下，让 npm 完成符号链接等操作
        import time
        time.sleep(2)
        
        is_installed, version = check_existing_installation()
        if is_installed:
            print(f"[OK] Installation verified! Version: {version}")
            
            # 创建包装脚本
            if create_wrapper_script():
                print("[OK] Command 's' is now available")
            
            if not non_interactive:
                setup_path_instructions()
                print("\n" + "="*60)
                print("Installation Complete! Quick Start:")
                print("="*60)
                print("  s --version   # Check version")
                print("  s config add  # Configure credentials")
                print("  s init        # Initialize project")
                print("  s deploy      # Deploy project")
                print("\nDocumentation: https://docs.serverless-devs.com/")
                print("="*60)
            return True
        else:
            print("[FAIL] Verification failed: 's' command not found")
            if not non_interactive:
                print("\nTroubleshooting:")
                print("  1. Restart your terminal")
                print("  2. Run: source ~/.bashrc  (or ~/.zshrc)")
                print("  3. Check PATH includes npm global bin")
                setup_path_instructions()
            return False
    else:
        if not non_interactive:
            print("\n" + "="*60)
            print("Installation Failed - Alternative Methods:")
            print("="*60)
            print("\nMethod 1: Install via npm directly")
            print("  npm install -g @serverless-devs/s")
            print("\nMethod 2: Use China mirror")
            if is_windows():
                print("  set USE_MIRROR=1")
            else:
                print("  export USE_MIRROR=1")
            print("  s-install")
            print("\nMethod 3: Manual installation")
            print("  Visit: https://docs.serverless-devs.com/getting-started/install")
            print("="*60)
        return False

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Serverless Devs Installer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  s-install              # Interactive installation
  s-install -y           # Auto-install (non-interactive)
  s-install --help       # Show this help

Environment Variables:
  USE_MIRROR=1           # Use China mirror for acceleration
  
For more information, visit: https://www.serverless-devs.com/
        """
    )
    
    parser.add_argument(
        '--non-interactive', '-y',
        action='store_true',
        help='Non-interactive mode, auto-install without prompts'
    )
    
    args = parser.parse_args()
    
    try:
        success = install_serverless_devs(non_interactive=args.non_interactive)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        if not args.non_interactive:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()