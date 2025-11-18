import zipfile
import json

with zipfile.ZipFile('dist/adam_calculator_mcp-0.1.2-py3-none-any.whl') as z:
    # 查找入口点文件
    for f in z.namelist():
        if 'entry_points' in f or f.endswith('.dist-info/'):
            print(f"文件: {f}")
            if 'entry_points.txt' in f:
                content = z.read(f).decode('utf-8')
                print("ENTRY_POINTS 文件内容:")
                print(content)
            elif 'WHEEL' in f:
                content = z.read(f).decode('utf-8')
                print("WHEEL 文件内容:")
                print(content)
            elif 'METADATA' in f:
                content = z.read(f).decode('utf-8')
                print("METADATA 文件内容:")
                print(content)
