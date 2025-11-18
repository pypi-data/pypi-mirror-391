def create_directory(dir_path):
    """创建目录，如果目录已存在则不做任何操作"""
    os.makedirs(dir_path, exist_ok=True)

def get_output_directory(ofd_path):
    """获取输出目录，自动创建img文件夹"""
    output_dir = os.path.join(os.path.dirname(ofd_path), 'img')
    create_directory(output_dir)
    return output_dir

def format_png_filename(base_name, page_num):
    """格式化PNG文件名"""
    return f"{base_name}_{page_num}.png"