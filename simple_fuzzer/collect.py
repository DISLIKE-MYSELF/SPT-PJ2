import os

def collect_py_files_to_txt(root_dir: str, output_file: str):
    with open(output_file, 'w', encoding='utf-8') as out:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    file_path = os.path.join(dirpath, filename)
                    out.write(f"\n\n### File: {file_path} ###\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"\n[Error reading {file_path}: {e}]\n")

    print(f"✅ 所有 Python 文件已写入到: {output_file}")

# 示例用法（你可以改成你项目根目录）
collect_py_files_to_txt('./..', 'all_code_output.txt')
