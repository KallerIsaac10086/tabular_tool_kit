import os
import csv
from concurrent.futures import ThreadPoolExecutor
import time
from tqdm import tqdm
import xlsxwriter
import argparse

def convert_csv_to_xlsx(csv_path, xlsx_path):
    """直接完整转换单个文件（无分块）"""
    workbook = xlsxwriter.Workbook(xlsx_path)
    worksheet = workbook.add_worksheet()
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f)
        for row_idx, row in enumerate(csv_reader):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value)
    
    # 自动调整列宽（可选）
    worksheet.autofit()
    workbook.close()

def batch_convert(args):
    """暴力性能版批量转换"""
    if output_dir is None:
        output_dir = input_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件列表
    files = [
        (os.path.join(input_dir, f), 
         os.path.join(output_dir, f.replace('.csv', '.xlsx')))
        for f in os.listdir(input_dir) 
        if f.lower().endswith('.csv')
    ]
    
    if not files:
        print("未发现CSV文件")
        return
    
    print(f"⚡ 开始暴力转换 {len(files)} 个文件...")
    start_time = time.time()
    
    # 多线程并发（IO密集型任务）
    with ThreadPoolExecutor(max_workers=max_workers or os.cpu_count()) as executor:
        list(tqdm(
            executor.map(lambda x: convert_csv_to_xlsx(*x), files),
            total=len(files),
            desc="转换进度",
            unit="文件"
        ))
    
    print(f"\n✅ 全部完成! 总耗时: {time.time() - start_time:.2f}秒")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='高性能文件转换工具')
    parser.add_argument('-i', '--input', required=True, help='输入目录路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('-w', '--workers', type=int, help='并发线程数')
    args = parser.parse_args()
    batch_convert(args)