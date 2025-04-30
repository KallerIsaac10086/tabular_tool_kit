import os
import csv
import threading
import queue
from tqdm import tqdm
import math
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

class CSVSplitterConverter:
    def __init__(self, input_file, output_dir, max_size_mb=95, verbose=True):
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
            print(f"文件大小: {self.total_size / (1024*1024):.2f} MB")
            print(f"总行数: {self.total_lines}")
            print(f"将拆分为 {self.num_files} 个文件，每个文件约 {self.lines_per_file} 行")
    
    def count_lines(self):
        """
        计算CSV文件的总行数
        """
        if self.verbose:
            print("正在计算文件行数...")
        
        with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            # 使用csv模块读取，以正确处理引号内的换行符
            reader = csv.reader(f)
            count = sum(1 for _ in reader)
        
        return count
    
    def split_csv(self):
        """
        拆分CSV文件并转换为XLSX
        
        返回:
            拆分后的文件数量
        """
        if self.verbose:
            print("开始拆分CSV文件...")
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.cpu_count) as executor:
            # 提交CSV拆分任务
            executor.submit(self._split_csv_worker)
            
            # 提交多个XLSX转换任务
            for _ in range(self.cpu_count - 1):  # 预留一个线程用于CSV拆分
                executor.submit(self._convert_to_xlsx_worker)
            
            # 等待所有任务完成
            self.split_queue.join()
            self.convert_queue.join()
        
        return self.num_files
    
    def _split_csv_worker(self):
        """
        CSV拆分工作线程
        """
        try:
            # 创建进度条
            pbar = None
            if self.verbose:
                pbar = tqdm(total=self.total_lines, desc="拆分进度")
            
            with open(self.input_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                header = next(reader)  # 读取标题行
                
                file_index = 0
                row_count = 0
                current_file = None
                current_writer = None
                
                for row in reader:
                    # 如果需要创建新文件
                    if row_count % self.lines_per_file == 0:
                        # 关闭之前的文件
                        if current_file is not None:
                            current_file.close()
                            
                            # 将完成的CSV文件放入转换队列
                            csv_filename = os.path.join(self.csv_dir, f"{self.base_name}_{file_index}.csv")
                            self.convert_queue.put(csv_filename)
                        
                        # 创建新文件
                        file_index += 1
                        csv_filename = os.path.join(self.csv_dir, f"{self.base_name}_{file_index}.csv")
                        current_file = open(csv_filename, 'w', newline='', encoding='utf-8')
                        current_writer = csv.writer(current_file)
                        
                        # 写入标题行
                        current_writer.writerow(header)
                    
                    # 写入数据行
                    current_writer.writerow(row)
                    row_count += 1
                    
                    # 更新进度条
                    if pbar is not None:
                        pbar.update(1)
                
                # 关闭最后一个文件
                if current_file is not None:
                    current_file.close()
                    
                    # 将最后一个CSV文件放入转换队列
                    csv_filename = os.path.join(self.csv_dir, f"{self.base_name}_{file_index}.csv")
                    self.convert_queue.put(csv_filename)
            
            # 标记CSV拆分任务完成
            for _ in range(self.cpu_count - 1):  # 为每个XLSX转换线程添加一个结束标记
                self.convert_queue.put(None)
            
            if pbar is not None:
                pbar.close()
        
        except Exception as e:
            print(f"CSV拆分错误: {str(e)}")
            raise
    
    def _convert_to_xlsx_worker(self):
        """
        XLSX转换工作线程
        """
        try:
            while True:
                # 从队列获取CSV文件名
                csv_filename = self.convert_queue.get()
                
                # 如果收到结束标记，则退出
                if csv_filename is None:
                    self.convert_queue.task_done()
                    break
                
                try:
                    # 获取基本文件名
                    base_name = os.path.basename(csv_filename)
                    xlsx_filename = os.path.join(self.xlsx_dir, f"{os.path.splitext(base_name)[0]}.xlsx")
                    
                    # 使用pandas读取CSV并保存为XLSX
                    df = pd.read_csv(csv_filename, encoding='utf-8')
                    df.to_excel(xlsx_filename, index=False)
                    
                    if self.verbose:
                        with self.lock:
                            print(f"已转换: {xlsx_filename}")
                
                except Exception as e:
                    print(f"转换文件 {csv_filename} 时出错: {str(e)}")
                
                finally:
                    # 标记任务完成
                    self.convert_queue.task_done()
        
        except Exception as e:
            print(f"XLSX转换错误: {str(e)}")
            raise