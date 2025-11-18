# OFD 转 PNG 转换器

这是一个用于将 OFD（Open Fixed Document）文件转换为 PNG 图片的 Python 包。支持单文件转换和多文件批量转换两种模式。

## 功能特点

- **单文件转换**：将单个 OFD 文件转换为 PNG 图片
- **批量转换**：将目录中的所有 OFD 文件转换为 PNG 图片
- **自动创建输出目录**：转换后的 PNG 文件将保存在与 OFD 文件相同目录下的 `img` 文件夹中
- **按页命名**：转换后的 PNG 文件将按页码命名，格式为 `原文件名_页码.png`

## 安装方法

### 从源代码安装

克隆或下载此仓库后，在项目根目录执行以下命令：

```bash
pip install ofd2png
```

### 开发模式安装

如果您需要修改代码并实时测试，可以使用开发模式安装：

```bash
pip install -e .
```

## 使用方法

### Python API 调用

#### 单文件转换

```python
from ofd2png import convert_file

# 转换单个 OFD 文件，转换后的 PNG 会保存在同一目录下的 img 文件夹中
convert_file('path/to/your/file.ofd')
```

#### 批量文件转换

```python
from ofd2png import convert_folder

# 转换目录中的所有 OFD 文件，每个文件的 PNG 会保存在各自目录下的 img 文件夹中
convert_folder('path/to/your/ofd_directory')
```

### 命令行工具

安装完成后，会自动安装一个名为 `ofd2png-cli` 的命令行工具。

#### 查看帮助信息

```bash
ofd2png-cli --help
```

#### 单文件转换

```bash
ofd2png-cli single path/to/your/file.ofd
```

#### 批量文件转换

```bash
ofd2png-cli batch path/to/your/ofd_directory
```

## 项目结构

```
ofd2png-package/
├── src/
│   └── ofd2png/
│       ├── __init__.py      # 包的公共 API 入口
│       ├── cli.py           # 命令行工具实现
│       ├── converter.py     # 核心转换逻辑
│       └── utils.py         # 辅助工具函数
├── tests/
│   └── test_converter.py    # 单元测试文件
├── README.md                # 项目说明文档
├── LICENSE                  # 许可证文件
├── pyproject.toml           # 项目配置文件
├── setup.cfg                # 安装配置文件
└── setup.py                 # 安装脚本
```

## 依赖包

- Pillow: 用于图片处理和生成
- lxml: 用于解析 OFD 文件的 XML 结构

## 开发与测试

### 运行测试

```bash
pytest tests/test_converter.py
```

### 代码格式

建议使用以下工具保持代码格式一致：

- black: Python 代码格式化工具
- flake8: 代码风格检查工具

## 许可证

本项目使用 MIT 许可证，详情请见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！