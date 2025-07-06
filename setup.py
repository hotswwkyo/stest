#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import setuptools

with open('README.md', 'r', encoding='UTF-8') as f:
    long_description = f.read()

setuptools.setup(
    name="stest",
    version="1.0.7",
    author="思文伟",
    author_email="hotswwkyo@qq.com",
    description="更友好、更灵活的编写、管理与运行测试，生成更加美观的独立单文件HTML报告。内置参数化测试数据存取方案，省去设计的烦恼，节省更多的时间，从而更快的投入到编写用例阶段",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/hotswwkyo/stest",
    packages=setuptools.find_packages(),
    install_requires=["xlrd==1.2.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    package_data={
        "stest": ["samples/*.xlsx", "report/resources/*.*"],
    },
)
