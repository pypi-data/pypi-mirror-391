from setuptools import setup, find_packages
from setuptools.command.install import install
import sys
import os

# 添加当前目录到 Python 路径，以便导入 installer
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class PostInstallCommand(install):
    """安装后自动安装 Serverless Devs"""
    def run(self):
        install.run(self)
        print("\n" + "="*60)
        print("开始安装 Serverless Devs ...")
        print("="*60 + "\n")
        
        try:
            from serverless_devs.installer import install_serverless_devs
            success = install_serverless_devs()
            if success:
                print("\n" + "="*60)
                print("✓ Serverless Devs 安装完成!")
                print("  请运行 's --version' 验证安装")
                print("="*60 + "\n")
            else:
                print("\n" + "="*60)
                print("✗ 安装失败")
                print("  请手动运行 's-install' 重试")
                print("="*60 + "\n")
        except Exception as e:
            print(f"\n安装过程中出现错误: {e}")
            print("请手动运行 's-install' 重试\n")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='serverless-devs',
    version='1.0.2',  # 这个是 Python 包的版本，不是 Serverless Devs 的版本
    description='Serverless Devs 开发者工具 - Python 安装包（自动安装最新版本）',
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
