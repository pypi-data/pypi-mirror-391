from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class PostInstallCommand(install):
    """安装后自动安装 Serverless Devs（非交互式）"""
    def run(self):
        install.run(self)
        print("\n" + "="*60)
        print("正在自动安装 Serverless Devs...")
        print("="*60 + "\n")
        
        try:
            from serverless_devs.installer import install_serverless_devs
            # 使用非交互模式自动安装
            success = install_serverless_devs(non_interactive=True)
            
            if success:
                print("\n" + "="*60)
                print("[OK] Serverless Devs 安装完成!")
                print("  运行 's --version' 查看版本")
                print("  运行 's config add' 配置密钥")
                print("  运行 's init' 初始化项目")
                print("="*60 + "\n")
            else:
                print("\n" + "="*60)
                print("[FAIL] 自动安装失败")
                print("  请手动运行: s-install")
                print("  或使用 npm: npm install -g @serverless-devs/s")
                print("="*60 + "\n")
        except Exception as e:
            print(f"\n安装过程中出现错误: {e}")
            print("请手动运行 's-install' 重试\n")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='serverless-devs',
    version='1.0.4',
    description='Serverless Devs Developer Tools - Python Package (Auto-install latest version)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Serverless Devs',
    author_email='service@serverless-devs.com',
    url='https://github.com/Serverless-Devs/Serverless-Devs',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            's=serverless_devs.__main__:main',
            's-install=serverless_devs.installer:main',
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='serverless devs aliyun faas function-compute',
    python_requires='>=3.7',
    project_urls={
        'Bug Reports': 'https://github.com/Serverless-Devs/Serverless-Devs/issues',
        'Source': 'https://github.com/Serverless-Devs/Serverless-Devs',
        'Documentation': 'https://www.serverless-devs.com/',
    },
)