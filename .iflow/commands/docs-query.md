# Docs Query Command - 编程文档查询命令

## 功能描述

使用 context7 工具查询编程库、框架、SDK、API 的官方文档，是编程文档检索的最高优先级工具。

## 使用场景

- 查询编程库的用法
- 查询框架 API 文档
- 查询 SDK 使用方法
- 查询数据库查询语法
- 查询前端组件用法

## 触发条件

任何关于编程库、框架、SDK、API 的问题

## 调用方式

### 步骤 1：获取库 ID
```python
resolve-library-id("react")
```

返回：
```
{
  "library_id": "/facebook/react",
  "name": "React",
  "description": "用于构建用户界面的 JavaScript 库",
  "reason": "最流行的 React 官方文档"
}
```

### 步骤 2：获取文档
```python
get-library-docs(
  context7CompatibleLibraryID="/facebook/react",
  topic="hooks",
  tokens=10000
)
```

## 优势

- 专门优化编程上下文
- Token 高效
- 最新官方文档
- 结构化输出

## 最佳实践

### 1. 必须先 resolve-library-id
```python
# ❌ 错误：直接使用库名
get-library-docs("react")

# ✅ 正确：先获取库 ID
library = resolve-library-id("react")
get-library-docs(library["library_id"])
```

### 2. 使用 topic 参数聚焦
```python
# 聚焦特定主题
get-library-docs("/facebook/react", topic="useEffect")

# 不指定 topic 获取完整文档
get-library-docs("/facebook/react")
```

### 3. 控制返回内容
```python
# 获取详细文档（更多 tokens）
get-library-docs("/facebook/react", tokens=15000)

# 获取简要文档（更少 tokens）
get-library-docs("/facebook/react", tokens=5000)
```

## 示例

### 示例 1：查询 React Hooks
```python
# 步骤 1：获取 React 库 ID
react = resolve-library-id("react")
# 返回：{"library_id": "/facebook/react", ...}

# 步骤 2：查询 Hooks 文档
hooks_docs = get-library-docs(
  context7CompatibleLibraryID="/facebook/react",
  topic="hooks",
  tokens=10000
)
```

### 示例 2：查询 Next.js 路由
```python
# 步骤 1：获取 Next.js 库 ID
nextjs = resolve-library-id("next.js")
# 返回：{"library_id": "/vercel/next.js", ...}

# 步骤 2：查询路由文档
routing_docs = get-library-docs(
  context7CompatibleLibraryID="/vercel/next.js",
  topic="routing",
  tokens=10000
)
```

### 示例 3：查询 MongoDB 查询语法
```python
# 步骤 1：获取 MongoDB 库 ID
mongodb = resolve-library-id("mongodb")
# 返回：{"library_id": "/mongodb/docs", ...}

# 步骤 2：查询查询语法
query_docs = get-library-docs(
  context7CompatibleLibraryID="/mongodb/docs",
  topic="query",
  tokens=10000
)
```

### 示例 4：查询 FastAPI 依赖注入
```python
# 步骤 1：获取 FastAPI 库 ID
fastapi = resolve-library-id("fastapi")
# 返回：{"library_id": "/tiangolo/fastapi", ...}

# 步骤 2：查询依赖注入文档
di_docs = get-library-docs(
  context7CompatibleLibraryID="/tiangolo/fastapi",
  topic="dependencies",
  tokens=10000
)
```

## 常用库 ID

### 前端框架
- React: `/facebook/react`
- Vue: `/vuejs/core`
- Next.js: `/vercel/next.js`
- Nuxt: `/nuxt/nuxt`

### 后端框架
- FastAPI: `/tiangolo/fastapi`
- Django: `/django/django`
- Flask: `/pallets/flask`
- Express: `/expressjs/express`

### 数据库
- MongoDB: `/mongodb/docs`
- PostgreSQL: `/postgres/docs`
- MySQL: `/mysql/docs`
- Redis: `/redis/docs`

### 工具库
- Axios: `/axios/axios`
- Lodash: `/lodash/lodash`
- Moment: `/moment/moment`
- Dayjs: `/iamkun/dayjs`

## 注意事项

⚠️ **重要提醒** ⚠️

- **必须先 resolve-library-id**：除非用户明确提供 `/org/project` 格式的库 ID
- **优先于网页搜索**：编程文档查询优先使用 context7
- **Token 高效**：context7 专门优化了编程上下文
- **最新文档**：确保获取的是最新官方文档

## 优先级

**第二优先级**（仅次于 desktop-commander）

信息检索优先级：
1. desktop-commander（本地文件）
2. context7（编程文档）
3. github（GitHub 代码）
4. web_fetch（网页内容）

## 禁止操作

❌ **禁止使用网页搜索查询编程文档**：
- 不使用 web_search 查询编程库用法
- 不使用 web_fetch 获取编程文档
- 必须使用 context7 工具

## 配置参数

```json
{
  "priority": 2,
  "requires_library_id": true,
  "supports_topic": true,
  "default_tokens": 10000,
  "max_tokens": 20000
}
```

## 版本

- **版本**：1.0.0
- **最后更新**：2026-02-01