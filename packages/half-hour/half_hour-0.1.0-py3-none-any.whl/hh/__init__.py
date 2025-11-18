import sys
import yaml
import os
from pathlib import Path

def _get_notefile_path():
    # 配置文件路径：$HOME/.config/half-hour/hh.yaml
    config_dir = Path.home() / '.config' / 'half-hour'
    config_path = config_dir / 'hh.yaml'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}. Please create it.")
    
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    
    notefile_path = config.get('notefile')
    if notefile_path is None:
        raise ValueError("notefile not found in config")
    
    return notefile_path

def hha():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: hha <time> <note>")
        return
    
    note_line = ' '.join(args)
    notefile_path = _get_notefile_path()
    
    with open(notefile_path, 'a', encoding='utf-8') as f:
        f.write(note_line + '\n')

def hhl():
    args = sys.argv[1:]
    n = 10
    if len(args) == 1:
        try:
            n = int(args[0])
        except ValueError:
            print("Usage: hhl [number_of_lines]")
            return
    elif len(args) > 1:
        print("Usage: hhl [number_of_lines]")
        return

    notefile_path = _get_notefile_path()
    if not os.path.exists(notefile_path):
        print(f"Note file {notefile_path} does not exist.")
        return

    with open(notefile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        last_lines = lines[-n:] if len(lines) >= n else lines
        for line in last_lines:
            print(line, end='')

def hhd():
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage: hhd <number_of_lines_to_delete>")
        return
    
    try:
        n = int(args[0])
        if n <= 0:
            print("Number of lines to delete must be positive.")
            return
    except ValueError:
        print("Usage: hhd <number_of_lines_to_delete>")
        return

    notefile_path = _get_notefile_path()
    if not os.path.exists(notefile_path):
        print(f"Note file {notefile_path} does not exist.")
        return

    with open(notefile_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if n >= len(lines):
        with open(notefile_path, 'w', encoding='utf-8') as f:
            pass
    else:
        with open(notefile_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-n])