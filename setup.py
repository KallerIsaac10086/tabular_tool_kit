from setuptools import setup, find_packages
import os

# 读取README.md作为长描述
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="tabular_tool_kit",
    version="1.0.0",
    author="CPTK Team",
    author_email="example@example.com",
    description="CSV处理工具包 (CSV Process Tool Kit)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cptk",
    packages=find_packages() + ['XlsxWriter'],
    package_data={'XlsxWriter': ['*', '**/*']},
    package_dir={'': '.'},
    include_package_data=True,
    dependency_links=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
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
            'cptk=cptk.cli:main',
        ],
    },
)