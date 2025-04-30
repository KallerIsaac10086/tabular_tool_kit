import os
import csv
import threading
import queue
from tqdm import tqdm
import math
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

class TabularToolKitConverter:
    def __init__(self, input_file, output_dir, input_format='csv', output_format='xlsx', max_size_mb=95, verbose=True):
        """
        新增参数:
            input_format: 输入文件格式（csv/xlsx）
            output_format: 输出文件格式（csv/xlsx）
        """
        """
        初始化CSV拆分转换器
        
        参数:
            input_file: 输入CSV文件路径
            output_dir: 输出目录
            max_size_mb: 每个输出文件的最大大小(MB)，默认为95MB
            verbose: 是否显示详细输出，默认为True
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.input_format = input_format.lower()
        self.output_format = output_format.lower()
        
        # 格式校验
        if self.input_format not in ['csv', 'xlsx']:
            raise ValueError(f'不支持的输入格式：{input_format}')
        if self.output_format not in ['csv', 'xlsx']:
            raise ValueError(f'不支持的输出格式：{output_format}')
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.split_queue = queue.Queue()  # 用于CSV拆分任务
        self.convert_queue = queue.Queue()  # 用于XLSX转换任务
        self.lock = threading.Lock()
        self.processed_rows = 0  # 已处理行数计数器
        self.verbose = verbose
        
        # 获取CPU核心数
        self.cpu_count = multiprocessing.cpu_count()
        if self.verbose:
            print(f"检测到 {self.cpu_count} 个CPU核心，将充分利用多线程性能")
        
        # 创建输出子目录
        self.csv_dir = os.path.join(output_dir, 'split_csv')
        self.xlsx_dir = os.path.join(output_dir, 'split_xlsx')
        os.makedirs(self.csv_dir, exist_ok=True)
        os.makedirs(self.xlsx_dir, exist_ok=True)
        
        # 获取输入文件的基本名称
        self.base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # 预计算文件信息
        self.total_size = os.path.getsize(input_file)
        self.total_lines = self.count_lines()
        self.num_files = max(1, math.ceil(self.total_size / self.max_size_bytes))
        self.lines_per_file = math.ceil(self.total_lines / self.num_files)
        
        if self.verbose:
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
    
    def split_csv(self):
        """拆分CSV文件的主要方法"""
        header = self.read_csv_header()
        
        # 创建进度条
        if self.verbose:
            split_pbar = tqdm(total=self.total_lines, desc="CSV拆分进度", unit="行")
            convert_pbar = tqdm(total=self.num_files, desc="XLSX转换进度", unit="文件")
        else:
            split_pbar = None
            convert_pbar = None
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.cpu_count) as split_executor, \
             ThreadPoolExecutor(max_workers=self.cpu_count) as convert_executor:
            
            # 启动CSV拆分线程
            split_futures = []
            for _ in range(self.cpu_count):
                future = split_executor.submit(
                    self.csv_split_worker, 
                    header, 
                    split_pbar
                )
                split_futures.append(future)
            
            # 启动XLSX转换线程
            convert_futures = []
            for _ in range(self.cpu_count):
                future = convert_executor.submit(
                    self.xlsx_convert_worker,
                    convert_pbar
                )
                convert_futures.append(future)
            
            # 读取文件并分配任务
            with open(self.input_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # 跳过表头
                
                current_chunk = 1
                current_rows = []
                
                for i, row in enumerate(reader, 1):
                    current_rows.append(row)
                    
                    if i % self.lines_per_file == 0:
                        self.split_queue.put((current_chunk, current_rows.copy()))
                        current_chunk += 1
                        current_rows.clear()
                
                # 添加最后一个块
                if current_rows:
                    self.split_queue.put((current_chunk, current_rows))
            
            # 添加结束信号
            for _ in range(self.cpu_count):
                self.split_queue.put(None)
            
            # 等待所有拆分线程完成
            for future in split_futures:
                future.result()
            
            # 添加XLSX转换结束信号
            for _ in range(self.cpu_count):
                self.convert_queue.put(None)
            
            # 等待所有转换线程完成
            for future in convert_futures:
                future.result()
        
        if self.verbose:
            split_pbar.close()
            convert_pbar.close()
            print(f"\n处理完成！共生成 {current_chunk} 个CSV文件和XLSX文件。")
        
        return current_chunk
    
    def csv_split_worker(self, header, pbar):
        """CSV拆分工作线程"""
        while True:
            task = self.split_queue.get()
            if task is None:
                self.split_queue.task_done()
                break
                
            chunk_num, rows = task
            csv_filename = f"{self.base_name}-{chunk_num:04d}.csv"
            csv_path = os.path.join(self.csv_dir, csv_filename)
            
            # 写入CSV文件
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            # 将转换任务放入XLSX队列
            self.convert_queue.put((chunk_num, csv_path))
            
            # 更新进度条
            if pbar:
                with self.lock:
                    self.processed_rows += len(rows)
                    pbar.n = self.processed_rows
                    pbar.refresh()
            
            self.split_queue.task_done()
    
    def xlsx_convert_worker(self, pbar):
        """XLSX转换工作线程"""
        while True:
            task = self.convert_queue.get()
            if task is None:
                self.convert_queue.task_done()
                break
                
            chunk_num, csv_path = task
            xlsx_filename = f"{self.base_name}-{chunk_num:04d}.xlsx"
            xlsx_path = os.path.join(self.xlsx_dir, xlsx_filename)
            
            # 使用pandas转换CSV到XLSX
            try:
                df = pd.read_csv(csv_path)
                df.to_excel(xlsx_path, index=False, engine='openpyxl')
            except Exception as e:
                if self.verbose:
                    print(f"转换文件 {csv_path} 时出错: {str(e)}")
            
            # 更新进度条
            if pbar:
                with self.lock:
                    pbar.update(1)
            
            self.convert_queue.task_done()