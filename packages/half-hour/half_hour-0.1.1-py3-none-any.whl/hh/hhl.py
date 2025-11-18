import sys
import yaml
import os

def main():
    # 默认显示行数
    n = 10
    if len(sys.argv) == 2:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Usage: hhl [number_of_lines]")
            return
    elif len(sys.argv) > 2:
        print("Usage: hhl [number_of_lines]")
        return

    # 读取配置文件
    config_path = os.path.join(os.path.dirname(__file__), 'hh.yaml')
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    
    notefile_path = config.get('notefile')
    if notefile_path is None:
        raise ValueError("notefile not found in config")

    if not os.path.exists(notefile_path):
        print(f"Note file {notefile_path} does not exist.")
        return

    # 读取文件最后 n 行
    with open(notefile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        last_lines = lines[-n:] if len(lines) >= n else lines
        for line in last_lines:
            print(line, end='')

if __name__ == '__main__':
    main()