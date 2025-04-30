import os
import sys
import argparse
from .splitter import CSVSplitterConverter

def get_help_text(lang='zh'):
    """
    获取帮助文本，支持中英双语
    
    参数:
        lang: 语言，'zh'为中文，'en'为英文
    """
    if lang == 'zh':
        return {
            'prog': '高性能多线程CSV处理工具包',
            'description': '''
            CPTK - CSV处理工具包 (CSV Process Tool Kit)
            功能说明:
            1. 预先计算文件大小和行数，智能确定拆分数量
            2. 自动检测CPU核心数并充分利用多线程性能
            3. 严格保证每个CSV文件小于指定大小
            4. 自动转换拆分后的CSV文件为XLSX格式
            ''',
            'input_file': '要拆分的CSV文件路径',
            'output_dir': '输出目录路径',
            'max_size': '每个文件的最大大小(MB，默认95)',
            'quiet': '安静模式，不显示进度条和详细信息',
            'version': '显示版本信息'
        }
    else:  # 英文
        return {
            'prog': 'High-performance Multi-threaded CSV Process Tool Kit',
            'description': '''
            CPTK - CSV Process Tool Kit
            Features:
            1. Pre-calculates file size and line count to intelligently determine split quantity
            2. Automatically detects CPU cores and fully utilizes multi-threading performance
            3. Strictly ensures each CSV file is smaller than the specified size
            4. Automatically converts split CSV files to XLSX format
            ''',
            'input_file': 'Path to the CSV file to split',
            'output_dir': 'Output directory path',
            'max_size': 'Maximum size of each file in MB (default 95)',
            'quiet': 'Quiet mode, do not display progress bars and detailed information',
            'version': 'Show version information'
        }

def main():
    """
    命令行入口函数
    """
    # 检测语言环境
    lang = 'en' if os.environ.get('LANG', '').startswith('en') else 'zh'
    
    # 如果命令行参数中包含-h，则根据是否有--en参数决定显示哪种语言的帮助
    if '-h' in sys.argv or '--help' in sys.argv:
        if '--en' in sys.argv:
            lang = 'en'
            # 移除--en参数，避免argparse解析错误
            sys.argv.remove('--en')
        elif '--zh' in sys.argv:
            lang = 'zh'
            sys.argv.remove('--zh')
    
    help_text = get_help_text(lang)
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description=help_text['description'], prog=help_text['prog'])
    parser.add_argument('input_file', help=help_text['input_file'])
    parser.add_argument('output_dir', help=help_text['output_dir'])
    parser.add_argument('-m', '--max-size', type=float, default=95, help=help_text['max_size'])
    parser.add_argument('-q', '--quiet', action='store_true', help=help_text['quiet'])
    parser.add_argument('-v', '--version', action='store_true', help=help_text['version'])
    
    # 解析参数
    args = parser.parse_args()
    
    # 显示版本信息
    if args.version:
        from . import __version__
        print(f"CPTK v{__version__}")
        return
    
    # 检查文件是否存在
    if not os.path.isfile(args.input_file):
        print("错误：输入文件不存在！" if lang == 'zh' else "Error: Input file does not exist!")
        return 1
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 创建处理器并执行
    processor = CSVSplitterConverter(
        args.input_file, 
        args.output_dir, 
        args.max_size,
        verbose=not args.quiet
    )
    
    try:
        num_files = processor.split_csv()
        if not args.quiet:
            if lang == 'zh':
                print(f"处理完成！文件已保存到：{args.output_dir}")
                print(f"- CSV文件位于: {os.path.join(args.output_dir, 'split_csv')}")
                print(f"- XLSX文件位于: {os.path.join(args.output_dir, 'split_xlsx')}")
            else:
                print(f"Processing complete! Files saved to: {args.output_dir}")
                print(f"- CSV files located at: {os.path.join(args.output_dir, 'split_csv')}")
                print(f"- XLSX files located at: {os.path.join(args.output_dir, 'split_xlsx')}")
        return 0
    except Exception as e:
        print(f"错误：{str(e)}" if lang == 'zh' else f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())