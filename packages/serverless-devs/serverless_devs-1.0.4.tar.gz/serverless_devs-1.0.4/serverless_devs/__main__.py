"""
Serverless Devs 命令行入口
智能调用 s 命令（支持多种安装方式）
"""

import subprocess
import sys
import shutil
import os

def find_s_command():
    """
    智能查找 s 命令
    返回: (命令路径或可执行方式, 是否为 node 脚本)
    """
    # 方法1: 直接在 PATH 中查找
    s_path = shutil.which('s')
    if s_path:
        return s_path, False
    
    # 方法2: 通过 npm 查找全局安装
    try:
        result = subprocess.run(
            ['npm', 'root', '-g'],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode == 0:
            npm_root = result.stdout.strip()
            s_js = os.path.join(npm_root, '@serverless-devs', 's', 'bin', 's.js')
            if os.path.exists(s_js):
                return s_js, True
    except Exception:
        pass
    
    # 方法3: 检查常见安装位置
    home = os.path.expanduser('~')
    common_paths = [
        os.path.join(home, '.s', 'bin', 's'),
        '/usr/local/bin/s',
        os.path.join(home, '.local', 'bin', 's'),
    ]
    
    # Windows 特殊路径
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            common_paths.extend([
                os.path.join(appdata, 'npm', 's.cmd'),
                os.path.join(appdata, 'npm', 's'),
            ])
    
    for path in common_paths:
        if os.path.exists(path):
            return path, False
    
    return None, False

def show_help_message():
    """显示帮助信息"""
    print("Error: 's' command not found", file=sys.stderr)
    print("", file=sys.stderr)
    print("This usually means Serverless Devs is not installed yet.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Solutions:", file=sys.stderr)
    print("  1. Reinstall this package:", file=sys.stderr)
    print("     pip install --force-reinstall serverless-devs", file=sys.stderr)
    print("", file=sys.stderr)
    print("  2. Manual installation:", file=sys.stderr)
    print("     s-install", file=sys.stderr)
    print("", file=sys.stderr)
    print("  3. Install via npm directly:", file=sys.stderr)
    print("     npm install -g @serverless-devs/s", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 尝试诊断问题
    if shutil.which('npm'):
        print("Diagnostics:", file=sys.stderr)
        try:
            result = subprocess.run(
                ['npm', 'list', '-g', '@serverless-devs/s', '--depth=0'],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='ignore'
            )
            if '@serverless-devs/s' in result.stdout:
                print("  - Serverless Devs is installed via npm", file=sys.stderr)
                
                # 提示 PATH 问题
                npm_bin_result = subprocess.run(
                    ['npm', 'bin', '-g'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding='utf-8',
                    errors='ignore'
                )
                if npm_bin_result.returncode == 0:
                    npm_bin = npm_bin_result.stdout.strip()
                    print(f"  - Add to PATH: {npm_bin}", file=sys.stderr)
                    
                    if sys.platform == 'win32':
                        print("", file=sys.stderr)
                        print("  To add to PATH on Windows:", file=sys.stderr)
                        print(f'    setx PATH "%PATH%;{npm_bin}"', file=sys.stderr)
                    else:
                        shell_rc = '~/.bashrc'
                        if os.path.exists(os.path.expanduser('~/.zshrc')):
                            shell_rc = '~/.zshrc'
                        print("", file=sys.stderr)
                        print(f"  To add to PATH on Unix:", file=sys.stderr)
                        print(f'    echo \'export PATH="{npm_bin}:$PATH"\' >> {shell_rc}', file=sys.stderr)
                        print(f"    source {shell_rc}", file=sys.stderr)
            else:
                print("  - Serverless Devs is NOT installed", file=sys.stderr)
                print("  - Run: s-install", file=sys.stderr)
        except Exception:
            pass
    else:
        print("Note: npm not found. Node.js may not be installed.", file=sys.stderr)
        print("      Download: https://nodejs.org/", file=sys.stderr)

def main():
    """主入口：调用 s 命令"""
    s_path, is_node_script = find_s_command()
    
    if s_path:
        try:
            if is_node_script:
                # Node.js 脚本，使用 node 执行
                cmd = ['node', s_path] + sys.argv[1:]
            else:
                # 可执行文件，直接执行
                cmd = [s_path] + sys.argv[1:]
            
            result = subprocess.run(cmd)
            sys.exit(result.returncode)
            
        except KeyboardInterrupt:
            # Ctrl+C 中断
            sys.exit(130)
        except Exception as e:
            print(f"Error: Failed to execute 's' command: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 找不到 s 命令
        show_help_message()
        sys.exit(1)

if __name__ == '__main__':
    main()