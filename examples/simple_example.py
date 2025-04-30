#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单示例：展示如何使用CPTK包
"""

import os
import sys
import pandas as pd
import random

# 添加父目录到路径，以便导入cptk包
# 注意：安装包后不需要这一步
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cptk import CSVSplitterConverter

def create_sample_csv(filename, rows=10000):
    """
    创建一个示例CSV文件用于测试
    """
    # 创建一个简单的数据框
    data = {
        'ID': range(1, rows + 1),
        'Name': [f'Person-{i}' for i in range(1, rows + 1)],
        'Age': [random.randint(18, 80) for _ in range(rows)],
        'Salary': [random.randint(3000, 15000) for _ in range(rows)],
        'Department': [random.choice(['HR', 'IT', 'Finance', 'Marketing', 'Operations']) for _ in range(rows)]
    }
    
    df = pd.DataFrame(data)
    
    # 保存为CSV
    df.to_csv(filename, index=False)
    print(f"已创建示例CSV文件: {filename} (包含 {rows} 行数据)")
    return filename

def main():
    # 创建示例目录
    os.makedirs('sample_data', exist_ok=True)
    
    # 创建示例CSV文件
    csv_file = os.path.join('sample_data', 'large_data.csv')
    create_sample_csv(csv_file, rows=50000)  # 创建一个包含50000行的CSV文件
    
    # 创建输出目录
    output_dir = os.path.join('sample_data', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n开始拆分和转换CSV文件...")
    
    # 创建处理器并执行
    processor = CSVSplitterConverter(
        input_file=csv_file,
        output_dir=output_dir,
        max_size_mb=1,  # 设置较小的值以便演示拆分效果
        verbose=True
    )
    
    # 执行拆分和转换
    num_files = processor.split_csv()
    
    print(f"\n处理完成！共生成 {num_files} 个文件")
    print(f"CSV文件位于: {os.path.join(output_dir, 'split_csv')}")
    print(f"XLSX文件位于: {os.path.join(output_dir, 'split_xlsx')}")

if __name__ == "__main__":
    main()