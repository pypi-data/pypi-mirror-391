from setuptools import setup, find_packages

setup(
    name="xbyter_common",           # 包名
    version="0.3.17",                # 版本号
    author="xbyter",
    author_email="amorcc@163.com",
    description="Common config and utilities for Xbyter projects",
    packages=find_packages(),
    python_requires=">=3.11.9",
    install_requires=[
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0"
    ],
)