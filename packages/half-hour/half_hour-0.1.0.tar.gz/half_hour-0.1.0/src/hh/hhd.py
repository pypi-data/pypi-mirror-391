import sys
import yaml
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python hhd.py <number_of_lines_to_delete>")
        return
    
    try:
        n = int(sys.argv[1])
        if n <= 0:
            print("Number of lines to delete must be positive.")
            return
    except ValueError:
        print("Usage: python hhd.py <number_of_lines_to_delete>")
        return

    # 读取配置文件路径（与脚本同目录）
    config_path = os.path.join(os.path.dirname(__file__), 'hh.yaml')
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    
    notefile_path = config.get('notefile')
    if notefile_path is None:
        raise ValueError("notefile not found in config")

    if not os.path.exists(notefile_path):
        print(f"Note file {notefile_path} does not exist.")
        return

    # 读取所有行
    with open(notefile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 如果要删除的行数大于等于总行数，则清空文件
    if n >= len(lines):
        with open(notefile_path, 'w', encoding='utf-8') as f:
            pass  # 清空文件
    else:
        # 保留除最后 n 行外的所有行
        with open(notefile_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-n])

if __name__ == '__main__':
    main()