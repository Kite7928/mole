# GitHub Operations Command - GitHub 操作命令

## 功能描述

使用 github 工具进行完整的 GitHub 项目协作，包括代码搜索、PR 管理、Issue 管理和代码审查。

## 使用场景

- 操作 GitHub 仓库
- 搜索开源代码
- 管理协作流程
- 创建和管理 PR
- 创建和管理 Issue
- 代码搜索和审查

## 核心能力

### 代码搜索
- `search_code` - 搜索代码（比 firecrawl 更精准）
- `search_repositories` - 搜索仓库

### PR 管理
- `create_pull_request` - 创建 PR
- `get_pull_request` - 获取 PR 详情
- `get_pull_request_diff` - 获取 PR 变更
- `list_pull_requests` - 列出 PR
- `merge_pull_request` - 合并 PR
- `create_pull_request_review` - 创建 PR 审查
- `request_copilot_review` - 自动代码审查

### Issue 管理
- `create_issue` - 创建 Issue
- `update_issue` - 更新 Issue
- `list_issues` - 列出 Issue
- `get_issue` - 获取 Issue 详情

### 文件操作
- `create_or_update_file` - 创建或更新文件
- `get_file_contents` - 获取文件内容
- `push_files` - 批量推送文件

## 使用优先级

**第三优先级**

信息检索优先级：
1. desktop-commander（本地文件）
2. context7（编程文档）
3. github（GitHub 代码）
4. web_fetch（网页内容）

## 最佳实践

### 1. 搜索代码时使用 search_code
```python
# ✅ 正确：使用 search_code
search_code(
  q="filename:main.py language:python"
)

# ❌ 错误：使用 firecrawl
web_fetch("https://github.com/search?q=...")
```

### 2. 创建 PR 前先检查变更
```python
# 步骤 1：获取 PR 差异
diff = get_pull_request_diff(owner, repo, pull_number)

# 步骤 2：审查变更
# 分析 diff 内容

# 步骤 3：创建 PR
create_pull_request(owner, repo, title, body, head, base)
```

### 3. 使用自动代码审查
```python
# 请求自动审查
request_copilot_review(owner, repo, pull_number)
```

## 示例

### 示例 1：搜索代码实现
```python
# 搜索 FastAPI 异步路由实现
results = search_code(
  q="language:python filename:main.py async def",
  per_page=30
)

# 搜索特定模式的代码
results = search_code(
  q="class UserRepository language:python",
  per_page=30
)
```

### 示例 2：创建功能 PR
```python
# 创建 PR
create_pull_request(
  owner="owner",
  repo="repo",
  title="添加用户评论功能",
  body="实现了用户评论、点赞和回复功能",
  head="feature/comments",
  base="main"
)
```

### 示例 3：管理 Issue
```python
# 创建 Issue
create_issue(
  owner="owner",
  repo="repo",
  title="修复登录时 token 验证失败",
  body="详细描述问题：\n\n1. 重现步骤\n2. 预期行为\n3. 实际行为",
  labels=["bug", "high-priority"]
)

# 更新 Issue
update_issue(
  owner="owner",
  repo="repo",
  issue_number=123,
  state="closed"
)
```

### 示例 4：代码审查流程
```python
# 步骤 1：获取 PR 详情
pr = get_pull_request(owner, repo, pull_number)

# 步骤 2：获取变更文件
files = get_pull_request_files(owner, repo, pull_number)

# 步骤 3：创建审查
create_pull_request_review(
  owner=owner,
  repo=repo,
  pull_number=pull_number,
  body="代码审查意见",
  event="COMMENT",
  comments=[
    {
      "path": "backend/app/api/comments.py",
      "line": 42,
      "body": "建议增加错误处理"
    }
  ]
)

# 步骤 4：批准或请求修改
create_pull_request_review(
  owner=owner,
  repo=repo,
  pull_number=pull_number,
  body="代码质量良好，建议合并",
  event="APPROVE"
)
```

### 示例 5：批量操作文件
```python
# 批量推送文件
push_files(
  owner="owner",
  repo="repo",
  branch="main",
  files=[
    {
      "path": "backend/app/models/comment.py",
      "content": "# Comment 模型\n..."
    },
    {
      "path": "backend/app/api/comments.py",
      "content": "# Comment API\n..."
    }
  ],
  message="添加评论功能"
)
```

### 示例 6：搜索仓库
```python
# 搜索相关仓库
repos = search_repositories(
  query="topic:fastapi language:python stars:>100",
  per_page=30
)
```

## 注意事项

⚠️ **重要提醒** ⚠️

- **优先于网页搜索**：搜索代码时优先使用 search_code
- **先检查再创建**：创建 PR 前先调用 get_pull_request_diff
- **自动审查**：使用 request_copilot_review 进行自动代码审查
- **权限检查**：确保有足够的权限执行操作

## 禁止操作

❌ **禁止使用网页工具操作 GitHub**：
- 不使用 web_search 搜索 GitHub 代码
- 不使用 web_fetch 获取 GitHub 内容
- 必须使用 github 工具

## 权限要求

- 读取：公共仓库
- 写入：需要仓库写入权限
- PR 操作：需要仓库协作者权限
- Issue 操作：需要仓库协作者权限

## 配置参数

```json
{
  "priority": 3,
  "requires_authentication": true,
  "max_per_page": 100,
  "default_per_page": 30
}
```

## 常见工作流

### 功能开发工作流
```
1. 创建分支
2. 开发功能
3. 提交代码
4. 创建 PR
5. 自动审查
6. 代码审查
7. 合并 PR
```

### Bug 修复工作流
```
1. 创建 Issue
2. 分配 Issue
3. 创建修复分支
4. 修复 Bug
5. 创建 PR
6. 关联 Issue
7. 合并 PR
8. 关闭 Issue
```

## 版本

- **版本**：1.0.0
- **最后更新**：2026-02-01