# Tabular Tool Kit - 表格数据处理工具包 (Tabular Data Processing Toolkit)

[English](#english) | [中文](#中文)

## 中文

### 简介

Tabular Tool Kit 是一个高性能的表格数据处理工具包，专为处理大型CSV文件而设计。它能够将大型CSV文件拆分成多个小文件，并自动转换为Excel格式，解决了Excel无法打开超过100万行数据的限制问题。

### 特点

- **高性能多线程处理**：自动检测CPU核心数，充分利用多线程性能
- **智能拆分**：预先计算文件大小和行数，智能确定拆分数量
- **严格控制文件大小**：确保每个拆分后的文件小于指定大小
- **自动格式转换**：自动将拆分后的CSV文件转换为XLSX格式
- **进度可视化**：实时显示处理进度

### 安装

```bash
pip install tabular_tool_kit
```

### 使用方法

#### 命令行使用

```bash
# 基本用法
cptk input.csv output_directory

# 指定每个文件的最大大小(MB)
cptk input.csv output_directory --max-size 50

# 安静模式，不显示进度条
cptk input.csv output_directory --quiet

# 显示中文帮助
cptk -h --zh

# 显示英文帮助
cptk -h --en

# 显示版本信息
cptk --version
```

#### 作为Python模块使用

```python
from cptk import CSVSplitterConverter

# 创建处理器
processor = CSVSplitterConverter(
    input_file="large_file.csv",
    output_dir="output",
    max_size_mb=95,  # 每个文件最大大小(MB)
    verbose=True  # 是否显示详细输出
)

# 执行拆分和转换
num_files = processor.split_csv()
print(f"共生成 {num_files} 个文件")
```

### 输出目录结构

```
output_directory/
├── split_csv/  # 拆分后的CSV文件
│   ├── original-0001.csv
│   ├── original-0002.csv
│   └── ...
└── split_xlsx/  # 转换后的XLSX文件
    ├── original-0001.xlsx
    ├── original-0002.xlsx
    └── ...
```

## English

### Introduction

CPTK (CSV Process Tool Kit) is a high-performance CSV file processing toolkit designed for processing large CSV files. It can split large CSV files into multiple smaller files and automatically convert them to Excel format, solving the limitation of Excel being unable to open data with more than 1 million rows.

### Features

- **High-performance multi-threading**: Automatically detects CPU cores and fully utilizes multi-threading performance
- **Intelligent splitting**: Pre-calculates file size and line count to intelligently determine split quantity
- **Strict file size control**: Ensures each split file is smaller than the specified size
- **Automatic format conversion**: Automatically converts split CSV files to XLSX format
- **Progress visualization**: Displays processing progress in real-time

### Installation

```bash
pip install tabular_tool_kit
```

### Usage

#### Command Line Usage

```bash
# Basic usage
cptk input.csv output_directory

# Specify maximum file size (MB)
cptk input.csv output_directory --max-size 50

# Quiet mode, no progress bars
cptk input.csv output_directory --quiet

# Show Chinese help
cptk -h --zh

# Show English help
cptk -h --en

# Show version information
cptk --version
```

#### Use as a Python Module

```python
from cptk import CSVSplitterConverter

# Create processor
processor = CSVSplitterConverter(
    input_file="large_file.csv",
    output_dir="output",
    max_size_mb=95,  # Maximum file size (MB)
    verbose=True  # Whether to display detailed output
)

# Execute splitting and conversion
num_files = processor.split_csv()
print(f"Generated {num_files} files")
```

### Output Directory Structure

```
output_directory/
├── split_csv/  # Split CSV files
│   ├── original-0001.csv
│   ├── original-0002.csv
│   └── ...
└── split_xlsx/  # Converted XLSX files
    ├── original-0001.xlsx
    ├── original-0002.xlsx
    └── ...
```

## License

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Licensed under the Apache License, Version 2.0