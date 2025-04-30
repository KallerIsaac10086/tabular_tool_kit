# CPTK 安装指南

[English](#english) | [中文](#中文)

## 中文

### 从PyPI安装

最简单的安装方法是使用pip从PyPI安装：

```bash
pip install csvsplitxl
```

### 从源代码安装

您也可以从源代码安装：

```bash
# 克隆仓库
git clone https://github.com/yourusername/cptk.git
cd cptk

# 安装包
pip install -e .
```

### 依赖项

CSVSplitXL 依赖以下Python包：

- pandas >= 1.0.0
- tqdm >= 4.45.0
- openpyxl >= 3.0.0

这些依赖项会在安装过程中自动安装。

### 验证安装

安装完成后，您可以通过运行以下命令验证安装是否成功：

```bash
csvsplitxl --version
```

如果显示版本号，则表示安装成功。

## English

### Install from PyPI

The easiest way to install is using pip from PyPI:

```bash
pip install csvsplitxl
```

### Install from Source

You can also install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/cptk.git
cd cptk

# Install the package
pip install -e .
```

### Dependencies

CSVSplitXL depends on the following Python packages:

- pandas >= 1.0.0
- tqdm >= 4.45.0
- openpyxl >= 3.0.0

These dependencies will be automatically installed during the installation process.

### Verify Installation

After installation, you can verify that the installation was successful by running:

```bash
csvsplitxl --version
```

If it displays the version number, the installation was successful.