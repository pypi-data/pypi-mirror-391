# Opentrons Analyze CLI

Opentrons 命令行工具，用于在命令行环境中分析 Opentrons 协议。

## 功能

该工具提供了一个命令行接口，可以：
- 分析 Opentrons 协议文件
- 输出协议分析结果
- 执行协议检查

## 安装

```bash
pip install opentrons-analyze
```

## 使用方法

安装后，可以通过以下命令使用：

```bash
opentrons_analyze "输入文件地址" --check --json-output "输出文件地址"
```

参数说明：
- `"输入文件地址"` - 要分析的协议文件路径
- `--check` - 执行协议检查
- `--json-output "输出文件地址"` - 将JSON格式的结果输出到指定文件

## 开发

### 先决条件

- Python 3.10 或更高版本
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```