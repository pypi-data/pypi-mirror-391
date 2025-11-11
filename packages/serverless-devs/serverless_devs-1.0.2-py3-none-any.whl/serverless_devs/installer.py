"""
Serverless Devs 安装器
使用官方安装脚本自动安装最新版本（包含 Node.js 环境）
"""

import os
import platform
import subprocess
import sys
import tempfile
import shutil
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
            result = subprocess.run(['s', '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version
        except:
            pass
    return False, None

def install_on_windows():
    """在 Windows 上安装 Serverless Devs"""
    print("检测到 Windows 系统...")
    print("\n推荐安装方式:")
    print("  1. 通过 npm 安装 (推荐):")
    print("     npm install -g @serverless-devs/s")
    print("\n  2. 下载二进制文件:")
    print("     访问 https://github.com/Serverless-Devs/Serverless-Devs/releases")
    print("     下载 s-*-win.exe.zip 并解压到 PATH 目录")
    print("\n正在尝试通过 npm 安装...")
    
    # 检查 npm 是否可用
    if not is_command_available('npm'):
        print("\n✗ 未检测到 npm，请先安装 Node.js:")
        print("  下载地址: https://nodejs.org/")
        return False
    
    # 使用 npm 安装
    try:
        print("\n执行: npm install -g @serverless-devs/s")
        
        # 设置环境变量使用国内镜像
        env = os.environ.copy()
        if os.environ.get('USE_NPM_MIRROR', '').lower() in ['1', 'true', 'yes']:
            env['NPM_CONFIG_REGISTRY'] = 'https://registry.npmmirror.com'
            print("(使用国内镜像加速)")
        
        result = subprocess.run(
            ['npm', 'install', '-g', '@serverless-devs/s'],
            env=env,
            capture_output=False,  # 显示实时输出
            text=True
        )
        
        if result.returncode == 0:
            print("\n✓ 安装成功!")
            return True
        else:
            print("\n✗ npm 安装失败")
            return False
            
    except Exception as e:
        print(f"\n✗ 安装失败: {e}")
        return False

def install_on_unix():
    """在 Unix 系统（Linux/macOS）上安装 Serverless Devs"""
    system = platform.system()
    print(f"检测到 {system} 系统...")
    
    # 检查必要的命令
    if not is_command_available('curl') and not is_command_available('wget'):
        print("\n✗ 错误: 需要 curl 或 wget 命令")
        print("请先安装: sudo apt-get install curl  # Debian/Ubuntu")
        print("         sudo yum install curl     # CentOS/RHEL")
        return False
    
    if not is_command_available('bash'):
        print("\n✗ 错误: 需要 bash")
        return False
    
    # 选择下载工具
    download_cmd = 'curl' if is_command_available('curl') else 'wget'
    
    # 选择安装脚本 URL（支持镜像）
    use_mirror = os.environ.get('USE_MIRROR', '').lower() in ['1', 'true', 'yes']
    script_url = INSTALL_SCRIPT_MIRROR if use_mirror else INSTALL_SCRIPT_URL
    
    if use_mirror:
        print("使用国内镜像加速...")
    
    print(f"\n正在下载安装脚本: {script_url}")
    
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
        else:  # wget
            download_result = subprocess.run(
                ['wget', '-q', script_url, '-O', temp_script],
                capture_output=True,
                text=True,
                timeout=60
            )
        
        if download_result.returncode != 0:
            print(f"\n✗ 下载失败: {download_result.stderr}")
            if not use_mirror:
                print("\n提示: 可以尝试使用国内镜像:")
                print("  export USE_MIRROR=1")
                print("  s-install")
            return False
        
        print("✓ 下载完成")
        
        # 添加执行权限
        os.chmod(temp_script, 0o755)
        
        # 执行安装脚本
        print("\n开始安装 Serverless Devs...")
        print("="*60)
        
        env = os.environ.copy()
        if use_mirror:
            env['NPM_REGISTRY'] = 'https://registry.npmmirror.com'
        
        install_result = subprocess.run(
            ['bash', temp_script],
            env=env,
            text=True
        )
        
        # 清理临时文件
        try:
            os.unlink(temp_script)
        except:
            pass
        
        if install_result.returncode == 0:
            print("="*60)
            print("✓ 安装成功!")
            return True
        else:
            print("="*60)
            print("✗ 安装失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ 下载超时，请检查网络连接")
        return False
    except Exception as e:
        print(f"\n✗ 安装过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_serverless_devs():
    """
    安装 Serverless Devs
    
    Returns:
        bool: 是否安装成功
    """
    print("="*60)
    print("Serverless Devs 安装器")
    print("="*60)
    
    # 检查是否已安装
    is_installed, version = check_existing_installation()
    if is_installed:
        print(f"\n检测到已安装 Serverless Devs: {version}")
        response = input("\n是否重新安装? (y/N): ")
        if response.lower() != 'y':
            print("跳过安装")
            return True
        print()
    
    # 根据系统选择安装方式
    if is_windows():
        success = install_on_windows()
    else:
        success = install_on_unix()
    
    if success:
        # 验证安装
        print("\n验证安装...")
        is_installed, version = check_existing_installation()
        if is_installed:
            print(f"✓ 验证成功! 已安装版本: {version}")
            print("\n" + "="*60)
            print("安装完成! 请运行以下命令开始使用:")
            print("  s --version  # 查看版本")
            print("  s config add # 配置密钥")
            print("  s init       # 初始化项目")
            print("="*60)
            return True
        else:
            print("✗ 验证失败: 找不到 s 命令")
            print("\n请尝试:")
            print("  1. 重新打开终端")
            print("  2. 运行: source ~/.bashrc  (或 ~/.zshrc)")
            print("  3. 手动添加到 PATH")
            return False
    else:
        print("\n" + "="*60)
        print("安装失败，请尝试:")
        print("="*60)
        print("\n方式1: 使用 npm 直接安装")
        print("  npm install -g @serverless-devs/s")
        print("\n方式2: 使用国内镜像")
        if is_windows():
            print("  set USE_NPM_MIRROR=1")
        else:
            print("  export USE_MIRROR=1")
        print("  s-install")
        print("\n方式3: 手动安装")
        print("  访问: https://docs.serverless-devs.com/getting-started/install")
        print("="*60)
        return False

def main():
    """命令行入口"""
    try:
        success = install_serverless_devs()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户取消安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
