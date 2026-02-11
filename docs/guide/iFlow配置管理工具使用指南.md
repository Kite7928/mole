# iFlow CLI 配置管理工具使用指南

## 📦 工具概述

本项目包含两个强大的配置管理工具：

1. **iflow-config-manager.ps1** - 配置导出/导入工具
2. **project-config-converter.ps1** - 项目间转换工具

---

## 🚀 工具一：配置导出/导入工具

### 功能

- ✅ 导出当前项目的 iFlow 配置
- ✅ 从备份或其他项目导入配置
- ✅ 验证配置完整性
- ✅ 自动备份现有配置

### 使用方法

#### 1. 导出配置

```powershell
# 导出所有配置
.\scripts\iflow-config-manager.ps1 -Action export -All

# 仅导出特定组件
.\scripts\iflow-config-manager.ps1 -Action export -IncludeAgents
.\scripts\iflow-config-manager.ps1 -Action export -IncludeCommands
.\scripts\iflow-config-manager.ps1 -Action export -IncludeSkills
.\scripts\iflow-config-manager.ps1 -Action export -IncludeSettings
```

**导出结果**：
```
.iflow-export/
└── gzh_20260210_143022/
    ├── metadata.json          # 元数据
    ├── settings.json          # 设置
    ├── agents/               # 代理
    │   ├── python-reviewer.md
    │   └── code-reviewer.md
    ├── commands/             # 命令
    │   ├── plan.md
    │   └── tdd.md
    └── skills/               # 技能
        ├── python-patterns/
        └── backend-patterns/
```

#### 2. 导入配置

```powershell
# 从导出目录导入所有配置
.\scripts\iflow-config-manager.ps1 -Action import -InputPath ".iflow-export\gzh_20260210_143022"

# 仅导入特定组件
.\scripts\iflow-config-manager.ps1 -Action import -InputPath "..." -IncludeAgents
```

#### 3. 验证配置

```powershell
# 验证当前配置
.\scripts\iflow-config-manager.ps1 -Action validate
```

**验证输出**：
```
🔍 验证 iFlow CLI 配置...

✓ .iflow 目录存在

📝 Settings:
  ✓ settings.json 有效
  • Agents: 3
  • Commands: 2
  • Skills: 4

🤖 Agents:
  • 数量: 2
    ✓ python-reviewer.md (2.5 KB)
    ✓ code-reviewer.md (3.1 KB)

⚡ Commands:
  • 数量: 2
    ✓ plan.md (4.2 KB)
    ✓ tdd.md (2.8 KB)

📚 Skills:
  • 文件: 8
  • 目录: 2
    ✓ python-patterns/best-practices.md (5.1 KB)
    ✓ backend-patterns/api-design.md (3.7 KB)
```

---

## 🔄 工具二：项目间转换工具

### 功能

- ✅ 将 iFlow 配置转换为其他项目格式
- ✅ 从其他项目格式转换为 iFlow 配置
- ✅ 支持多种格式：Claude Code、Cursor、GitHub Copilot 等
- ✅ 通用 JSON 格式用于跨平台共享

### 支持的格式

| 格式 | 方向 | 兼容性 |
|------|------|--------|
| Claude Code | 双向 | ⭐⭐⭐⭐⭐ |
| Cursor | to-iflow | ⭐⭐⭐ |
| GitHub Copilot | to-iflow | ⭐⭐⭐ |
| Generic JSON | 双向 | ⭐⭐⭐⭐⭐ |

### 使用方法

#### 1. 查看支持的格式

```powershell
.\scripts\project-config-converter.ps1 -Action list
```

#### 2. 导出为 Claude Code 格式

```powershell
# 从 iFlow 转换为 Claude Code
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat claude-code

# 指定源路径
.\scripts\project-config-converter.ps1 -Action from-iflow -SourcePath ".iflow" -TargetFormat claude-code
```

**输出结构**：
```
claude-code-export/
├── plugin.json           # Claude Code 插件配置
├── prompts/              # Prompts（从 Agents 转换）
│   ├── python-reviewer.md
│   └── code-reviewer.md
├── commands/             # Commands
│   ├── plan.md
│   └── tdd.md
└── skills/               # Skills
    ├── python-patterns/
    └── backend-patterns/
```

#### 3. 导出为通用 JSON 格式

```powershell
# 从 iFlow 转换为通用 JSON
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat generic
```

**输出文件**：`iflow-config-generic.json`

```json
{
  "version": "1.0.0",
  "exportedAt": "2026-02-10 14:30:22",
  "source": "iFlow CLI",
  "components": {
    "settings": { ... },
    "agents": {
      "python-reviewer": {
        "content": "...",
        "filename": "python-reviewer.md",
        "size": 2500
      }
    },
    "commands": { ... },
    "skills": { ... }
  }
}
```

#### 4. 从 Claude Code 格式导入

```powershell
# 从 Claude Code 转换为 iFlow
.\scripts\project-config-converter.ps1 -Action to-iflow -TargetFormat claude-code -SourcePath "claude-code-export"
```

#### 5. 从通用 JSON 格式导入

```powershell
# 从通用 JSON 转换为 iFlow
.\scripts\project-config-converter.ps1 -Action to-iflow -TargetFormat generic -SourcePath "iflow-config-generic.json"
```

---

## 💡 实际使用场景

### 场景一：项目间配置共享

**目标**：将项目 A 的 iFlow 配置复制到项目 B

```powershell
# 1. 在项目 A 导出配置
cd G:\db\guwen\gzh
.\scripts\iflow-config-manager.ps1 -Action export -All

# 2. 将导出的配置复制到项目 B
xcopy .iflow-export\gzh_* G:\db\other-project\iflow-config\ /E /I

# 3. 在项目 B 导入配置
cd G:\db\other-project
.\scripts\iflow-config-manager.ps1 -Action import -InputPath "iflow-config\gzh_*"
```

### 场景二：跨工具使用配置

**目标**：在 Claude Code 中使用 iFlow 的配置

```powershell
# 1. 从 iFlow 转换为 Claude Code 格式
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat claude-code

# 2. 在 Claude Code 中使用
# - 将 claude-code-export/ 复制到 Claude Code 的插件目录
# - 重启 Claude Code
```

### 场景三：配置备份和恢复

**目标**：定期备份配置并在需要时恢复

```powershell
# 1. 导出配置（定期执行）
.\scripts\iflow-config-manager.ps1 -Action export -All -OutputPath "backups\iflow"

# 2. 需要时恢复
.\scripts\iflow-config-manager.ps1 -Action import -InputPath "backups\iflow\gzh_20260210_143022"
```

### 场景四：团队协作配置

**目标**：团队共享标准化的 iFlow 配置

```powershell
# 1. 导出为通用 JSON 格式（便于版本控制）
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat generic

# 2. 提交到 Git
git add iflow-config-generic.json
git commit -m "更新团队 iFlow 配置"

# 3. 团队成员拉取并导入
git pull
.\scripts\project-config-converter.ps1 -Action to-iflow -TargetFormat generic -SourcePath "iflow-config-generic.json"
```

---

## ⚙️ 高级用法

### Dry Run 模式

预览操作而不实际执行：

```powershell
# 导出预览
.\scripts\iflow-config-manager.ps1 -Action export -All

# 转换预览
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat claude-code -DryRun
```

### 选择性导出/导入

只处理需要的组件：

```powershell
# 只导出 Agents 和 Skills
.\scripts\iflow-config-manager.ps1 -Action export -IncludeAgents -IncludeSkills

# 只导入 Commands
.\scripts\iflow-config-manager.ps1 -Action import -InputPath "..." -IncludeCommands
```

### 自定义项目名称

```powershell
# 导出时指定项目名称
.\scripts\iflow-config-manager.ps1 -Action export -All -ProjectName "my-awesome-project"
```

---

## 🔒 安全建议

1. **定期备份**：使用导出工具定期备份配置
2. **版本控制**：将 `iflow-config-generic.json` 纳入 Git 管理
3. **敏感信息**：检查配置中是否包含敏感信息（API Key等）
4. **测试环境**：先在测试环境验证配置再应用到生产环境

---

## 🐛 故障排查

### 问题 1：导入失败

**症状**：导入时提示文件不存在

**解决**：
```powershell
# 验证源路径
Test-Path ".iflow-export\gzh_*"

# 检查 metadata.json
Test-Path ".iflow-export\gzh_*/metadata.json"
```

### 问题 2：转换后配置无法使用

**症状**：转换后的配置在 iFlow 中无法正常工作

**原因**：不同工具的配置格式可能不完全兼容

**解决**：
- 使用 `validate` 命令检查配置
- 手动调整不兼容的部分
- 参考原始格式文档

### 问题 3：权限错误

**症状**：无法复制或写入文件

**解决**：
```powershell
# 以管理员身份运行 PowerShell
# 或检查文件权限
icacls .iflow
```

---

## 📊 迁移内容可用性总结

| 内容类型 | 可用性 | 兼容性 | 说明 |
|---------|--------|--------|------|
| **Skills（知识库）** | ✅ 90% | ⭐⭐⭐⭐⭐ | 最佳实践和模式可直接复用 |
| **Agents（代理）** | ⚠️ 70% | ⭐⭐⭐⭐ | 可能需要调整提示词结构 |
| **Commands（命令）** | ⚠️ 60% | ⭐⭐⭐ | 依赖的工具可能不同 |
| **Settings（配置）** | ⚠️ 50% | ⭐⭐⭐ | 配置格式需要转换 |

---

## 🎯 快速开始

### 第一次使用

```powershell
# 1. 导出当前配置
.\scripts\iflow-config-manager.ps1 -Action export -All

# 2. 验证配置
.\scripts\iflow-config-manager.ps1 -Action validate

# 3. 转换为通用格式（便于共享）
.\scripts\project-config-converter.ps1 -Action from-iflow -TargetFormat generic
```

### 团队协作

```powershell
# 1. 团队负责人导出标准配置
.\scripts\iflow-config-manager.ps1 -Action export -All -ProjectName "team-standard"

# 2. 提交到 Git
git add .iflow-export/
git commit -m "Add standard iFlow config"

# 3. 团队成员导入
git pull
.\scripts\iflow-config-manager.ps1 -Action import -InputPath ".iflow-export/team-standard_*"
```

---

**需要更多帮助？** 请查看其他文档或提交 Issue。