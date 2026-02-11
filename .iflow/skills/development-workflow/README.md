# Development Workflow Skill

标准化开发工作流，包含深度思考、任务规划、代码实现、质量审查和自动验证。

## 快速开始

### 安装

```bash
# 刷新技能列表
/skills refresh

# 或者使用命令行
iflow skill refresh
```

### 使用

在 iFlow CLI 中，当您进行以下操作时，本 Skill 会自动激活：

- 开发新功能
- 修复 Bug
- 代码重构
- API 开发
- 数据库操作
- 前端组件开发

## 文件结构

```
development-workflow/
├── SKILL.md              # 主文件（必需）
├── README.md             # 使用说明
├── LICENSE.txt           # 许可证
├── examples.md           # 使用示例
├── reference.md          # 技术参考
└── templates/            # 模板文件
    └── verification-report.md  # 审查报告模板
```

## 核心功能

### 1. 深度思考分析
使用 `sequential-thinking` 工具分析问题本质、识别现有实现、绘制依赖关系。

### 2. 任务规划
使用 `task-manager` 工具将复杂任务拆分为可执行步骤。

### 3. 信息检索
按照优先级使用工具检索信息：
- desktop-commander（最高优先级）
- context7
- github
- web_fetch

### 4. 代码实现
遵循严格的代码规范和质量标准。

### 5. 自动验证
本地自动执行测试，失败立即终止。

### 6. 质量审查
从技术维度和战略维度进行评分，生成审查报告。

### 7. 决策
根据综合评分决定通过、退回或需讨论。

## 核心原则

### 强制深度思考
任何时候必须首先使用 `sequential-thinking` 工具梳理问题。

### 自动连续执行
不是必要的问题，不要询问用户，必须自动连续执行。

### 问题驱动优先
追求充分性而非完整性，动态调整而非僵化执行。

### 中文输出强制
所有 AI 回复、文档、注释、日志必须使用简体中文（代码标识符除外）。

## 文档

- **[SKILL.md](./SKILL.md)** - 完整的工作流文档
- **[examples.md](./examples.md)** - 详细的使用示例
- **[reference.md](./reference.md)** - 技术参考和最佳实践

## 版本历史

- **v1.0.0** (2026-02-08): 初始版本

## 作者

Kite7928

## 许可证

MIT License