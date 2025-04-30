#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试CSVSplitXL包的功能
"""

import os
import sys
import unittest
import tempfile
import shutil
import pandas as pd

# 添加父目录到路径，以便导入csvsplitxl包
# 注意：安装包后不需要这一步
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from csvsplitxl import CSVSplitterConverter

class TestCSVSplitXL(unittest.TestCase):
    """
    测试CSVSplitXL的功能
    """
    
    def setUp(self):
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 创建测试CSV文件
        self.csv_file = os.path.join(self.temp_dir, 'test.csv')
        data = {
            'ID': range(1, 1001),
            'Name': [f'Person-{i}' for i in range(1, 1001)],
            'Value': list(range(1, 1001))
        }
        pd.DataFrame(data).to_csv(self.csv_file, index=False)
    
    def tearDown(self):
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_split_csv(self):
        """测试CSV拆分功能"""
        # 创建处理器
        processor = CSVSplitterConverter(
            input_file=self.csv_file,
            output_dir=self.output_dir,
            max_size_mb=0.01,  # 设置很小的值以确保拆分
            verbose=False
        )
        
        # 执行拆分
        num_files = processor.split_csv()
        
        # 验证结果
        self.assertGreater(num_files, 1, "应该生成多个文件")
        
        # 检查CSV文件是否存在
        csv_dir = os.path.join(self.output_dir, 'split_csv')
        self.assertTrue(os.path.exists(csv_dir), "CSV目录应该存在")
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        self.assertEqual(len(csv_files), num_files, "CSV文件数量应该匹配")
        
        # 检查XLSX文件是否存在
        xlsx_dir = os.path.join(self.output_dir, 'split_xlsx')
        self.assertTrue(os.path.exists(xlsx_dir), "XLSX目录应该存在")
        xlsx_files = [f for f in os.listdir(xlsx_dir) if f.endswith('.xlsx')]
        self.assertEqual(len(xlsx_files), num_files, "XLSX文件数量应该匹配")

if __name__ == '__main__':
    unittest.main()