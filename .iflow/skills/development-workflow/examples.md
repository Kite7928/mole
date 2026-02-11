# Development Workflow - 使用示例

本文档提供了 development-workflow Skill 的详细使用示例。

## 目录

1. [示例 1：开发用户评论功能](#示例-1开发用户评论功能)
2. [示例 2：修复登录 Bug](#示例-2修复登录-bug)
3. [示例 3：API 端点开发](#示例-3api-端点开发)
4. [示例 4：数据库操作](#示例-4数据库操作)
5. [示例 5：前端组件开发](#示例-5前端组件开发)

---

## 示例 1：开发用户评论功能

### 用户请求
```
开发一个用户评论功能，支持点赞和回复
```

### 完整执行流程

#### 步骤 1：深度思考分析
```
工具: sequential-thinking

分析内容:
- 识别需求核心：用户评论系统（发布、查看、点赞、回复）
- 分析现有项目结构：查找已有用户系统、文章系统
- 分析现有实现：参考文章评论功能的实现（如有）
- 技术方案选择：
  * 数据库设计：评论表、点赞表
  * API 设计：RESTful 端点
  * 前端组件：评论列表、评论表单
- 依赖关系：用户认证系统、文章系统
- 风险评估：性能优化（评论数量多时）、敏感词过滤
```

#### 步骤 2：任务规划
```
工具: task-manager

任务清单:
1. 设计数据库表结构（comments, comment_likes）
2. 创建数据库模型（models/comment.py）
3. 实现 API 端点（api/comments.py）
4. 实现业务逻辑（services/comment_service.py）
5. 创建前端评论组件（components/comment-list.tsx）
6. 创建前端评论表单组件（components/comment-form.tsx）
7. 编写单元测试
8. 编写集成测试
9. 执行测试验证
10. 代码审查
```

#### 步骤 3：信息检索
```
工具优先级:
1. desktop-commander - 查看现有数据库结构、API 端点
2. context7 - 查询 SQLAlchemy、FastAPI 文档
3. github - 搜索评论系统最佳实践示例

检索结果:
- 现有用户表：users (id, username, email)
- 现有文章表：articles (id, title, content, author_id)
- SQLAlchemy 异步模式用法
- FastAPI 路由依赖注入
```

#### 步骤 4：代码实现

**数据库模型** (backend/app/models/comment.py):
```python
# 评论数据模型
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="comments")
    article = relationship("Article", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent")
```

**API 端点** (backend/app/api/comments.py):
```python
# 评论 API 端点
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.post("/")
async def create_comment(
    request: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建评论"""
    # 实现评论创建逻辑
    pass

@router.get("/article/{article_id}")
async def get_article_comments(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取文章评论列表"""
    # 实现评论列表查询
    pass
```

#### 步骤 5：编写测试

**单元测试** (backend/tests/test_comments.py):
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_comment(client: AsyncClient, auth_headers):
    """测试创建评论"""
    response = await client.post(
        "/api/comments/",
        json={
            "content": "这是一条测试评论",
            "article_id": 1
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["content"] == "这是一条测试评论"
```

#### 步骤 6：自动验证
```
执行命令:
pytest backend/tests/test_comments.py -v

结果:
PASSED test_create_comment
PASSED test_get_article_comments
PASSED test_like_comment
```

#### 步骤 7：质量审查

**技术维度评分**:
- 代码质量: 18/20 (遵循规范，但可优化)
- 测试覆盖: 19/20 (覆盖主要场景)
- 规范遵循: 19/20 (严格遵循规范)

**战略维度评分**:
- 需求匹配: 15/15 (完全满足需求)
- 架构一致: 14/15 (符合项目架构)
- 风险评估: 9/10 (性能风险已考虑)

**综合评分**: 94/100

**建议**: 通过 ✅

#### 步骤 8：决策
```
决策: 通过
理由: 综合评分 94 分，满足所有要求，代码质量高，测试覆盖完整
```

---

## 示例 2：修复登录 Bug

### 用户请求
```
修复用户登录时 token 验证失败的问题
```

### 完整执行流程

#### 步骤 1：深度思考分析
```
工具: sequential-thinking

分析内容:
- 问题描述：用户登录后 token 验证失败
- 可能原因：
  * token 生成逻辑错误
  * token 验证逻辑错误
  * token 过期时间设置问题
  * 数据库存储问题
- 排查方案：
  * 检查 token 生成代码
  * 检查 token 验证代码
  * 检查 token 配置
  * 编写复现测试
```

#### 步骤 2：任务规划
```
工具: task-manager

任务清单:
1. 检查登录相关代码
2. 编写复现测试
3. 定位问题根因
4. 修复问题
5. 运行测试验证
6. 代码审查
```

#### 步骤 3：信息检索
```
工具: desktop-commander

检索操作:
- 查看登录 API 端点代码
- 查看 token 生成和验证逻辑
- 查看配置文件
```

#### 步骤 4：编写复现测试
```python
# backend/tests/test_login_bug.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_token_verification_bug(client: AsyncClient):
    """复现 token 验证失败问题"""
    # 1. 登录获取 token
    login_response = await client.post(
        "/api/auth/login",
        json={"username": "test", "password": "test123"}
    )
    token = login_response.json()["access_token"]
    
    # 2. 使用 token 访问受保护端点
    protected_response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 3. 验证应该成功但实际失败
    assert protected_response.status_code == 200  # 实际会失败
```

#### 步骤 5：定位问题
```
测试结果:
FAILED test_token_verification_bug

错误信息:
Token verification failed: Signature has expired

根因分析:
token 过期时间设置为 1 小时，但实际验证时使用了分钟作为单位
```

#### 步骤 6：修复代码
```python
# 修复前
expire_minutes = 60  # 误认为是 60 分钟

# 修复后
expire_minutes = 60  # 正确：60 分钟
```

#### 步骤 7：验证修复
```
执行命令:
pytest backend/tests/test_login_bug.py -v

结果:
PASSED test_token_verification_bug
```

#### 步骤 8：质量审查

**技术维度评分**:
- 代码质量: 20/20 (简单清晰的修复)
- 测试覆盖: 20/20 (编写了复现测试)
- 规范遵循: 20/20 (严格遵循规范)

**战略维度评分**:
- 需求匹配: 15/15 (完全修复问题)
- 架构一致: 15/15 (符合现有架构)
- 风险评估: 10/10 (无新风险)

**综合评分**: 100/100

**建议**: 通过 ✅

---

## 示例 3：API 端点开发

### 用户请求
```
开发一个获取文章列表的 API 端点，支持分页和排序
```

### 关键要点

#### 分页实现
```python
@router.get("/api/articles")
async def get_articles(
    page: int = 1,
    size: int = 10,
    sort_by: str = "created_at",
    order: str = "desc",
    db: AsyncSession = Depends(get_db)
):
    """获取文章列表（支持分页和排序）"""
    offset = (page - 1) * size
    
    # 构建查询
    query = select(Article)
    
    # 排序
    sort_column = getattr(Article, sort_by, Article.created_at)
    if order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # 分页
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return {
        "items": articles,
        "total": len(articles),
        "page": page,
        "size": size
    }
```

#### 测试覆盖
```python
@pytest.mark.asyncio
async def test_get_articles_with_pagination(client: AsyncClient):
    """测试分页功能"""
    response = await client.get("/api/articles?page=2&size=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 5
    assert len(data["items"]) <= 5

@pytest.mark.asyncio
async def test_get_articles_with_sorting(client: AsyncClient):
    """测试排序功能"""
    response = await client.get("/api/articles?sort_by=title&order=asc")
    assert response.status_code == 200
    data = response.json()
    titles = [item["title"] for item in data["items"]]
    assert titles == sorted(titles)
```

---

## 示例 4：数据库操作

### 用户请求
```
创建一个数据库迁移，添加用户头像字段
```

### 执行流程

#### 1. 创建迁移脚本
```python
# backend/migrations/add_user_avatar.py
from sqlalchemy import text

async def upgrade(db):
    """添加用户头像字段"""
    await db.execute(text(
        "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)"
    ))

async def downgrade(db):
    """回滚迁移"""
    await db.execute(text(
        "ALTER TABLE users DROP COLUMN avatar_url"
    ))
```

#### 2. 更新数据模型
```python
# backend/app/models/user.py
class User(Base):
    __tablename__ = "users"
    
    # ... 现有字段 ...
    avatar_url = Column(String(255), nullable=True)
```

#### 3. 编写测试
```python
@pytest.mark.asyncio
async def test_user_avatar_field(db: AsyncSession):
    """测试用户头像字段"""
    # 创建用户
    user = User(username="test", avatar_url="https://example.com/avatar.png")
    db.add(user)
    await db.commit()
    
    # 查询验证
    result = await db.execute(select(User).where(User.username == "test"))
    user = result.scalar_one()
    assert user.avatar_url == "https://example.com/avatar.png"
```

---

## 示例 5：前端组件开发

### 用户请求
```
创建一个文章卡片组件，显示文章标题、摘要、作者和发布时间
```

### 执行流程

#### 1. 组件实现
```typescript
// frontend/components/article-card.tsx
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

interface ArticleCardProps {
  id: number
  title: string
  summary: string
  author: string
  publishedAt: string
}

export function ArticleCard({ id, title, summary, author, publishedAt }: ArticleCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <Link href={`/articles/${id}`}>
        <h3 className="text-xl font-semibold mb-2 hover:text-blue-600">{title}</h3>
      </Link>
      <p className="text-gray-600 mb-4 line-clamp-3">{summary}</p>
      <div className="flex items-center text-sm text-gray-500">
        <span className="mr-4">作者: {author}</span>
        <span>
          {formatDistanceToNow(new Date(publishedAt), { addSuffix: true })}
        </span>
      </div>
    </div>
  )
}
```

#### 2. 使用示例
```typescript
// frontend/app/articles/page.tsx
import { ArticleCard } from '@/components/article-card'

export default function ArticlesPage() {
  const articles = [
    {
      id: 1,
      title: "如何使用 iFlow Skill",
      summary: "本文介绍了 iFlow Skill 的使用方法和最佳实践...",
      author: "张三",
      publishedAt: "2026-02-08T10:00:00Z"
    }
  ]
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {articles.map(article => (
        <ArticleCard key={article.id} {...article} />
      ))}
    </div>
  )
}
```

#### 3. 测试
```typescript
// frontend/components/__tests__/article-card.test.tsx
import { render, screen } from '@testing-library/react'
import { ArticleCard } from '../article-card'

describe('ArticleCard', () => {
  it('显示文章标题', () => {
    render(
      <ArticleCard
        id={1}
        title="测试标题"
        summary="测试摘要"
        author="测试作者"
        publishedAt="2026-02-08T10:00:00Z"
      />
    )
    expect(screen.getByText('测试标题')).toBeInTheDocument()
  })
  
  it('显示发布时间', () => {
    render(
      <ArticleCard
        id={1}
        title="测试标题"
        summary="测试摘要"
        author="测试作者"
        publishedAt="2026-02-08T10:00:00Z"
      />
    )
    expect(screen.getByText(/ago/)).toBeInTheDocument()
  })
})
```

---

## 最佳实践总结

### 1. 始终从深度思考开始
- 不要急于编码，先理解问题本质
- 分析现有实现，避免重复造轮子
- 识别依赖关系和潜在风险

### 2. 编写可复现的测试
- Bug 修复必须先编写复现测试
- 新功能必须编写单元测试和集成测试
- 测试应该覆盖正常流程和边界条件

### 3. 遵循项目规范
- 使用简体中文注释
- 遵循 SOLID、DRY 原则
- 保持代码简洁和可读性

### 4. 完整实现，无占位符
- 不要使用 MVP 或最小实现
- 完成全量功能和数据路径
- 删除过时和重复代码

### 5. 自动验证和质量审查
- 所有验证由本地 AI 自动执行
- 生成详细的验证报告
- 根据评分决定通过或退回

---

## 常见问题

### Q1: 如何处理复杂的业务逻辑？
A: 使用 sequential-thinking 深度分析，拆分为多个小任务，逐步实现。

### Q2: 测试覆盖率要求多少？
A: 至少覆盖主要功能和边界条件，目标覆盖率 80% 以上。

### Q3: 什么时候需要创建新的 Skill？
A: 当某个流程重复出现 3 次以上，且可以标准化时，考虑创建 Skill。

### Q4: 如何处理性能问题？
A: 在设计阶段评估时间复杂度，识别瓶颈，提供优化建议。

---

## 更多资源

- [SKILL.md](./SKILL.md) - 主文档
- [reference.md](./reference.md) - 参考文档
- [templates/](./templates/) - 模板文件