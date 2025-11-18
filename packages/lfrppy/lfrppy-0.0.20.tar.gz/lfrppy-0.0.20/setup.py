#!/usr/bin/env python
# -*- coding:utf-8 -*-


#############################################
# File Name: setup.py
# Author: Cai Jianping
# Mail: jpingcai@163.com
# Created Time:  2025-11-14 09:19:34
#############################################


from setuptools import setup, find_packages

setup(
    name="lfrppy",
    version="0.0.20",
    keywords=["frp", "tunnel", "deployment"],
    description="FRP deployment helpers",
    long_description="Utilities for deploying frpc and frps.",
    license="MIT Licence",
    author="Cai Jianping",
    author_email="jpingcai@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],
    entry_points={"console_scripts": ["frpc=lfrppy.core.cli:main", "frps=lfrppy.core.cli:main"]}
)
