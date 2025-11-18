import sys
import yaml
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python half_hour.py <time> <note>")
        return
    
    # 获取命令行参数并拼接成一行
    note_line = ' '.join(sys.argv[1:])
    
    # 读取配置文件路径（与脚本同目录）
    config_path = os.path.join(os.path.dirname(__file__), 'hh.yaml')
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    
    notefile_path = config.get('notefile')
    if notefile_path is None:
        raise ValueError("notefile not found")
    
    # 写入到配置指定的文件，追加模式
    with open(notefile_path, 'a', encoding='utf-8') as f:
        f.write(note_line + '\n')

if __name__ == '__main__':
    main()