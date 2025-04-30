from setuptools import setup, find_packages
import os

# 读取README.md作为长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="tabular_tool_kit",
    version="1.0.5",
    author="Kaller",
    author_email="sjy84789@gmail.com",
    description="CSV处理工具包 (CSV Process Tool Kit)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KallerIsaac10086/tabular_tool_kit",
    packages=find_packages(),
    package_dir={'': '.'},
    include_package_data=True,
    dependency_links=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas>=1.0.0',
        'tqdm>=4.45.0',
        'openpyxl>=3.0.0',
        'XlsxWriter>=3.2.0',
    ],
    entry_points={
        'console_scripts': [
            'tabular_tool_kit=tabular_tool_kit.cli:main'
        ],
    },
    # 保留第22行的url声明
)