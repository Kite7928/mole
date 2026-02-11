# File Analysis Command - 本地文件分析命令

## 功能描述

使用 desktop-commander 工具进行本地文件操作和数据分析，是信息检索的最高优先级工具。

## 使用场景

- 分析本地 CSV/JSON 数据文件
- 搜索代码模式
- 管理后台进程
- 文本替换和编辑
- 目录管理和搜索

## 核心能力

### 文件操作
- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `edit_block` - 精确文本替换（外科手术式）
- `list_directory` - 列出目录内容
- `create_directory` - 创建目录
- `move_file` - 移动文件

### 搜索功能
- `start_search` - 流式文件搜索（支持文件名和内容搜索）
- 渐进式返回结果
- 可提前终止

### 进程管理
- `start_process` - 启动进程
- `interact_with_process` - 交互式 REPL

### 数据分析
- 支持 Python REPL 进行 CSV/JSON/日志分析
- 支持 Node.js REPL
- 交互式工作流

## 使用优先级

**最高优先级** - 任何本地文件操作、CSV/JSON/数据分析、进程管理必须使用此工具

## 最佳实践

### 1. 本地文件分析必用
- 所有本地 CSV/JSON/数据文件分析必须用此工具
- 禁止使用 analysis/REPL 工具（会失败）

### 2. 交互式工作流
```python
# 启动 Python REPL
start_process("python3 -i")

# 交互式加载数据
interact_with_process("import pandas as pd")
interact_with_process("df = pd.read_csv('data.csv')")
interact_with_process("df.head()")

# 分析数据
interact_with_process("df.describe()")
```

### 3. 精确编辑
- 使用 `edit_block` 进行外科手术式文本替换
- 比 sed/awk 更安全
- 支持精确的上下文匹配

### 4. 流式搜索
- 大目录搜索使用 `start_search`
- 渐进式返回结果
- 可提前终止

## 优势

- 比 bash 更安全和结构化
- 支持 REPL 交互
- 适合数据科学工作流
- 精确的文本编辑能力

## 示例

### 示例 1：分析 CSV 文件
```python
# 启动 Python REPL
start_process("python3 -i")

# 加载数据
interact_with_process("import pandas as pd")
interact_with_process("df = pd.read_csv('sales.csv')")

# 分析数据
interact_with_process("df.info()")
interact_with_process("df.describe()")
interact_with_process("df.groupby('category').sum()")
```

### 示例 2：搜索代码模式
```python
# 搜索文件
start_search("pattern", path="backend/app")

# 搜索内容
start_search("async def", path="backend/app/api", type="content")
```

### 示例 3：精确文本替换
```python
# 替换特定代码块
edit_block(
    file="backend/app/api/news.py",
    old_text="@router.get(\"/hotspots\")\nasync def get_hotspots():",
    new_text="@router.get(\"/hotspots\")\nasync def get_hotspots(db: AsyncSession = Depends(get_db)):"
)
```

### 示例 4：读取配置文件
```python
# 读取 JSON 配置
read_file("config.json")

# 读取环境变量
read_file(".env")
```

## 注意事项

⚠️ **重要提醒** ⚠️

- **绝对优先于 bash**：不要使用 cat/grep/find 等 bash 命令
- **本地文件分析**：禁止使用 analysis/REPL 工具
- **使用绝对路径**：以保证可靠性
- **精确匹配**：edit_block 需要精确的上下文匹配

## 禁止操作

❌ **禁止使用以下命令进行本地文件操作**：
- `cat`
- `grep`
- `find`
- `sed`
- `awk`
- `ls`
- `cp`
- `mv`
- `rm`

## 替代方案

| 命令 | 替代工具 |
|------|---------|
| `cat` | `read_file` |
| `grep` | `start_search` |
| `find` | `start_search` |
| `sed` | `edit_block` |
| `ls` | `list_directory` |
| `cp` | `copy_file` |
| `mv` | `move_file` |
| `rm` | `delete_file` |

## 配置参数

```json
{
  "priority": "highest",
  "supports_repl": true,
  "supports_streaming": true,
  "file_operations": [
    "read",
    "write",
    "edit",
    "list",
    "create",
    "move",
    "delete"
  ],
  "search_types": [
    "filename",
    "content",
    "regex"
  ]
}
```

## 版本

- **版本**：1.0.0
- **最后更新**：2026-02-01