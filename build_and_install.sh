#!/bin/bash

# 构建和安装CPTK包的脚本

echo "=== 清理旧的构建文件 ==="
rm -rf build/ dist/ *.egg-info/

echo "=== 构建包 ==="
python setup.py sdist bdist_wheel

echo "=== 安装包 ==="
pip install -e .

echo "=== 安装完成 ==="
echo "现在可以使用以下命令测试包:"
echo "cptk --version"
echo "或者运行示例:"
echo "python examples/simple_example.py"