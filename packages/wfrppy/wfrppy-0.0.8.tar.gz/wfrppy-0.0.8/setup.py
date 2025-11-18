#!/usr/bin/env python
# -*- coding:utf-8 -*-


#############################################
# File Name: setup.py
# Author: Cai Jianping
# Mail: jpingcai@163.com
# Created Time:  2025-11-14 09:18:47
#############################################


from setuptools import setup, find_packages

setup(
    name="wfrppy",
    version="0.0.8",
    keywords=["frp", "service", "windows"],
    description="Windows \u5e73\u53f0\u7684 FRP \u670d\u52a1\u7ba1\u7406\u5de5\u5177",
    long_description="\u63d0\u4f9b frpc / frps \u7684 Windows \u670d\u52a1\u90e8\u7f72\u3001\u542f\u505c\u4e0e\u6e05\u7406\u80fd\u529b\u3002",
    license="MIT Licence",
    author="Cai Jianping",
    author_email="jpingcai@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],
    entry_points={"console_scripts": ["frpc=wfrppy.core.cli:main", "frps=wfrppy.core.cli:main"]}
)
