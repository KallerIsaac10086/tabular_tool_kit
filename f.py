import os
import csv
import threading
import queue
from tqdm import tqdm
import math
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import argparse
from xlsx_io import detect_file_type, XLSXReader

class CSVSplitter:
    def __init__(self, input_file, output_dir, max_size_mb=95):
        """
        初始化CSV拆分器
        
        参数:
            input_file: 输入CSV文件路径
            output_dir: 输出目录
            max_size_mb: 每个输出文件的最大大小(MB)，默认为95MB
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        
        # 获取CPU核心数
        self.cpu_count = multiprocessing.cpu_count()
        print(f"检测到 {self.cpu_count} 个CPU核心，将充分利用多线程性能")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 获取输入文件的基本名称
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # 预计算文件信息
        self.total_size = os.path.getsize(input_file)
        self.total_lines = self.count_lines()
        self.num_files = max(1, math.ceil(self.total_size / self.max_size_bytes))
        self.lines_per_file = math.ceil(self.total_lines / self.num_files)
        
        print(f"文件总大小: {self.total_size/1024/1024:.2f}MB")
        print(f"总行数: {self.total_lines}")
        print(f"将拆分为 {self.num_files} 个文件")
        print(f"每个文件约 {self.lines_per_file} 行")
        
    def count_lines(self):
        """快速计算文件总行数"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    
    def read_csv_header(self):
        """读取CSV文件的表头"""
        with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            return next(reader)
    
    def process_file(self):
        if self.file_type == 'xlsx':
            self._split_xlsx()
        else:
            self._split_csv()
    
    def _split_xlsx(self):
        """拆分XLSX文件的主要方法"""
        header = self.read_csv_header()
        
        # 创建进度条
        pbar = tqdm(total=self.num_files, desc="CSV拆分进度", unit="文件")
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            # 启动工作线程
            futures = []
            for _ in range(self.cpu_count):
                future = executor.submit(
                    self.csv_worker, 
                    header, 
                    pbar
                )
                futures.append(future)
            
            # 读取文件并分配任务
            with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过表头
                
                current_chunk = 1
                current_rows = []
                
                for i, row in enumerate(reader, 1):
                    current_rows.append(row)
                    
                    if i % self.lines_per_file == 0:
                        self.queue.put((current_chunk, current_rows.copy()))
                        current_chunk += 1
                        current_rows.clear()
                
                # 添加最后一个块
                if current_rows:
                    self.queue.put((current_chunk, current_rows))
            
            # 添加结束信号
            for _ in range(self.cpu_count):
                self.queue.put(None)
            
            # 等待所有线程完成
            for future in futures:
                future.result()
        
        pbar.close()
        print(f"\n处理完成！共生成 {current_chunk} 个CSV文件。")
    
    def csv_worker(self, header, pbar):
        """CSV工作线程"""
        while True:
            task = self.queue.get()
            if task is None:
                self.queue.task_done()
                break
                
            chunk_num, rows = task
            csv_filename = f"{self.base_name}-{chunk_num:04d}.csv"
            csv_path = os.path.join(self.output_dir, csv_filename)
            
            # 写入CSV文件
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            # 更新进度条
            with self.lock:
                pbar.update(1)
            
            self.queue.task_done()

def main():
    parser = argparse.ArgumentParser(description='高性能文件处理工具')
    parser.add_argument('-i', '--input', required=True, help='输入文件路径')
    parser.add_argument('-o', '--output', required=True, help='输出目录路径')
    parser.add_argument('-s', '--size', type=float, default=95, help='最大文件大小(MB)')
    parser.add_argument('-w', '--workers', type=int, help='并发线程数')
    args = parser.parse_args()

    processor = CSVSplitter(args.input, args.output, args.size)
    processor.split_csv()

if __name__ == "__main__":
    main()