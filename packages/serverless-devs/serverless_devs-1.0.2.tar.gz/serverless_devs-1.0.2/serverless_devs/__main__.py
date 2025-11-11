"""
Serverless Devs 命令行入口
调用已安装的 s 命令
"""

import subprocess
import sys
import shutil

def main():
    """调用 s 命令"""
    # 查找 s 命令
    s_path = shutil.which('s')
    
    if s_path:
        try:
            # 调用实际的 s 命令，传递所有参数
            result = subprocess.run([s_path] + sys.argv[1:])
            sys.exit(result.returncode)
        except KeyboardInterrupt:
            sys.exit(130)  # 128 + SIGINT
        except Exception as e:
            print(f"错误: 执行 s 命令时出错: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("错误: 找不到 's' 命令", file=sys.stderr)
        print("", file=sys.stderr)
        print("请尝试以下解决方案:", file=sys.stderr)
        print("  1. 重新安装: pip install --force-reinstall serverless-devs", file=sys.stderr)
        print("  2. 手动安装: s-install", file=sys.stderr)
        print("  3. 使用 npm: npm install -g @serverless-devs/s", file=sys.stderr)
        print("  4. 重新加载环境变量: source ~/.bashrc (或 ~/.zshrc)", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
