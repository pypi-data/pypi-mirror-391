from setuptools import setup, find_packages
import os

# 获取当前目录
here = os.path.abspath(os.path.dirname(__file__))

# 读取项目描述
long_description = """
PyScripts 是一个包含多个金融相关模块的Python库，包括数据库连接、模型分析、爬虫、策略实现等功能。
"""

# 定义安装依赖
install_requires = [
    'numpy>=1.19.0',
    'pandas>=1.0.0',
    'requests>=2.25.0',
    'matplotlib>=3.3.0'
]

setup(
    name="liwancai-pyscripts",
    version="0.1.0",
    description="个人使用习惯工具Python库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="liwancai",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="finance, analysis, strategy, database",
)