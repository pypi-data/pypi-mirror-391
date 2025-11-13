#! /usr/bin/env python3

"""
制作PIP包教程
1. 先设置一个setup文件
2. 运行setup.py sdist
3. 然后会得到一个dist文件, 这个时候就可用pip install dist/xxxxx 来安装文件了
4. 到PYPI上创建一个API Token(现在不支持user/passwd模型上传package了)
5. 在本地的创建一个$HOME/.pypirc文件
    其中:ls
    [pypi]
    username = __token__
    password = # 这里改成放申请下来的token
6. twine upload dist/* 可上传安装,需要输入pypi的用户名和密码
"""
from setuptools import setup, find_packages

setup(
    # 包的名称
    name="jhu",
    # 包的版本,每次更新或升级包都需要更新它
    version="1.7.0",
    # 描述
    description="jhu是一个工具包,简化或自动化的做一些任务",
    # 作者
    author="J.Hu",
    # 作者邮箱
    email="joestarhu@163.com",
    # github
    url="https://github.com/joestarhu/jhu",

    packages=find_packages(
        # 包内不需要引用的文件
        exclude=["test", "examples", "script", "tutorials"],
    ),

    classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.14"
    ],

    # 依赖的包必须安装
    install_requires=[],

    # 可选的安装包
    extras_require={
        "auth": ["requests"],
        "email": [],
        "orm": ["sqlalchemy", "pytz"],
        "security": ["python-jose", "bcrypt", "pycryptodomex"],
        "webhook": ["requests"],
    },

    zip_safe=True
)
