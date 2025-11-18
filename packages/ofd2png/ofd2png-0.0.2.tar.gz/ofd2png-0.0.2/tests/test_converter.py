# 导入必要的模块
import os
import shutil
from pathlib import Path

# 导入 pytest 测试框架
import pytest
# 导入 Pillow 库用于处理图片
from PIL import Image

# 从 ofd2png 包中导入所需函数
from ofd2png import convert_file, convert_folder


# 测试函数：使用实际 OFD 文件测试 convert_file
# 确保转换过程能正确生成 PNG 文件

def test_convert_file_with_real_ofd(tmp_path):
    """测试使用真实 OFD 文件转换为 PNG"""
    # 真实 OFD 文件路径（替换为你实际的 OFD 文件路径）
    REAL_OFD_PATH = "d:/ofdtopng/tempofd/ofd3.ofd"
    
    # 验证 OFD 文件存在
    assert os.path.exists(REAL_OFD_PATH), f"OFD 文件不存在: {REAL_OFD_PATH}"
    
    # 将真实 OFD 文件复制到临时目录
    test_ofd_filename = os.path.basename(REAL_OFD_PATH)
    test_ofd_path = os.path.join(tmp_path, test_ofd_filename)
    shutil.copy(REAL_OFD_PATH, test_ofd_path)
    
    # 调用文件转换函数
    generated_pngs = convert_file(test_ofd_path)
    
    # 验证生成了 PNG 文件
    assert generated_pngs, "转换后未生成任何 PNG 文件"
    
    for png_path in generated_pngs:
        # 验证 PNG 文件存在
        assert os.path.exists(png_path), f"PNG 文件未生成: {png_path}"
        # 验证是有效的 PNG 文件
        assert png_path.lower().endswith(".png"), f"生成的不是 PNG 文件: {png_path}"
        
        # 尝试打开图片以验证其完整性
        try:
            with Image.open(png_path) as img:
                img.verify()  # 验证图片完整性
        except Exception as e:
            pytest.fail(f"生成的 PNG 文件损坏: {png_path}, 错误: {str(e)}")


# 测试函数：使用实际 OFD 文件夹测试 convert_folder
# 确保批量转换功能正常工作

def test_convert_folder_with_real_ofds(tmp_path):
    """测试批量转换真实 OFD 文件夹"""
    # 真实 OFD 文件夹路径
    REAL_OFD_DIR = "d:/ofdtopng/tempofd"
    
    # 验证 OFD 文件夹存在
    assert os.path.isdir(REAL_OFD_DIR), f"OFD 文件夹不存在: {REAL_OFD_DIR}"
    
    # 获取所有 OFD 文件
    ofd_files = [f for f in os.listdir(REAL_OFD_DIR) if f.lower().endswith(".ofd")]
    assert ofd_files, "OFD 文件夹中没有 OFD 文件"
    
    # 创建临时输入目录并复制 OFD 文件
    input_dir = os.path.join(tmp_path, "input_ofds")
    os.makedirs(input_dir)
    
    for ofd_file in ofd_files:
        src_path = os.path.join(REAL_OFD_DIR, ofd_file)
        dst_path = os.path.join(input_dir, ofd_file)
        shutil.copy(src_path, dst_path)
    
    # 调用批量转换函数
    convert_folder(input_dir)
    
    # 验证输出目录存在
    output_dir = os.path.join(input_dir, "img")
    assert os.path.isdir(output_dir), f"未生成输出目录: {output_dir}"
    
    # 验证生成了 PNG 文件
    generated_pngs = [f for f in os.listdir(output_dir) if f.lower().endswith(".png")]
    assert generated_pngs, "批量转换后未生成任何 PNG 文件"
    
    for png_file in generated_pngs:
        # 验证 PNG 文件名格式正确（例如：ofd3_1.png）
        assert "_" in png_file, f"PNG 文件名格式不正确: {png_file}"
        
        # 验证文件完整性
        png_path = os.path.join(output_dir, png_file)
        try:
            with Image.open(png_path) as img:
                img.verify()  # 验证图片完整性
        except Exception as e:
            pytest.fail(f"生成的 PNG 文件损坏: {png_path}, 错误: {str(e)}")


# 测试函数：测试当 OFD 文件不存在时，convert_file 会抛出异常

def test_convert_file_missing_raises(tmp_path):
    """测试转换不存在的 OFD 文件会抛出 FileNotFoundError"""
    # 创建一个不存在的 OFD 文件路径
    non_existent_ofd = tmp_path / "non_existent.ofd"
    
    # 断言调用 convert_file 函数会抛出异常
    with pytest.raises(FileNotFoundError):
        convert_file(str(non_existent_ofd))


# 测试函数：测试当输入不是目录时，convert_folder 会抛出异常

def test_convert_folder_not_dir_raises(tmp_path):
    """测试输入非目录时会抛出 NotADirectoryError"""
    # 创建一个文件而不是目录
    not_dir = tmp_path / "not_a_directory.ofd"
    not_dir.write_text("this is a file, not a directory")
    
    # 断言调用 convert_folder 函数会抛出异常
    with pytest.raises(NotADirectoryError):
        convert_folder(str(not_dir))


# 添加main块，使测试文件可以直接通过python命令执行
if __name__ == "__main__":
    import pytest
    import sys
    
    # 运行所有测试
    sys.exit(pytest.main([__file__, "-v"]))