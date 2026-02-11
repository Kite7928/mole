# 代码质量指南

> 本项目的代码质量标准、禁止模式和最佳实践

---

## 概览

本项目遵循 **Python PEP 8** 规范，强调代码的可读性、可维护性和一致性。

---

## 代码风格

### 命名规范

```python
# 类名：大驼峰（PascalCase）
class ArticleService:
    pass

# 函数/方法名：小写+下划线（snake_case）
async def create_article():
    pass

# 变量名：小写+下划线（snake_case）
article_list = []
api_key = "xxx"

# 常量名：大写+下划线（UPPER_SNAKE_CASE）
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# 私有属性/方法：前缀单下划线
class MyClass:
    def __init__(self):
        self._private_var = 0

    def _private_method(self):
        pass
```

### 类型注解（必须）

```python
# ✅ 正确：使用类型注解
async def get_article_by_id(
    db: AsyncSession,
    article_id: int
) -> Optional[Article]:
    pass

# ❌ 错误：缺少类型注解
async def get_article_by_id(db, article_id):
    pass
```

### 文档字符串（必须）

```python
# ✅ 正确：使用中文文档字符串
async def create_article(db: AsyncSession, data: CreateArticleRequest) -> Article:
    """创建文章

    Args:
        db: 数据库会话
        data: 文章创建请求数据

    Returns:
        创建的文章对象

    Raises:
        ValidationError: 数据验证失败
    """
    pass

# ❌ 错误：缺少文档字符串
async def create_article(db, data):
    pass
```

---

## 禁止模式

### ❌ 1. 不要在路由中写业务逻辑

```python
# ❌ 错误
@router.post("/articles")
async def create_article(data: CreateArticleRequest, db: AsyncSession = Depends(get_db)):
    article = Article(title=data.title, content=data.content)
    db.add(article)
    await db.commit()
    # 大量业务逻辑...
    return article

# ✅ 正确
@router.post("/articles")
async def create_article(data: CreateArticleRequest, db: AsyncSession = Depends(get_db)):
    article = await article_service.create_article(db, data)
    return ArticleResponse.from_article(article)
```

### ❌ 2. 不要在模型中写业务逻辑

```python
# ❌ 错误
class Article(Base):
    def publish_to_wechat(self):
        wechat_api.publish(self.content)

# ✅ 正确：在服务层实现
class WechatService:
    async def publish_article(self, article: Article):
        pass
```

### ❌ 3. 不要使用裸 except

```python
# ❌ 错误
try:
    result = await operation()
except:  # 捕获所有异常，包括 KeyboardInterrupt
    pass

# ✅ 正确
try:
    result = await operation()
except Exception as e:
    logger.error(f"操作失败: {str(e)}")
    raise
```

### ❌ 4. 不要在循环中查询数据库

```python
# ❌ 错误
for article_id in article_ids:
    article = await db.execute(select(Article).where(Article.id == article_id))

# ✅ 正确
articles = await db.execute(
    select(Article).where(Article.id.in_(article_ids))
)
```

### ❌ 5. 不要使用可变默认参数

```python
# ❌ 错误
def process_items(items=[]):  # 可变默认参数
    items.append("new")
    return items

# ✅ 正确
def process_items(items: Optional[List] = None):
    if items is None:
        items = []
    items.append("new")
    return items
```

---

## 必须遵循的模式

### ✅ 1. 使用依赖注入

```python
# ✅ 正确
@router.get("/articles")
async def list_articles(db: AsyncSession = Depends(get_db)):
    pass

# ❌ 错误
@router.get("/articles")
async def list_articles():
    db = get_db_connection()  # 手动创建连接
```

### ✅ 2. 使用 Pydantic 模型验证

```python
# ✅ 正确
class CreateArticleRequest(BaseModel):
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容")

@router.post("/articles")
async def create_article(data: CreateArticleRequest):
    pass

# ❌ 错误
@router.post("/articles")
async def create_article(title: str, content: str):
    pass
```

### ✅ 3. 使用自定义异常

```python
# ✅ 正确
if not article:
    raise NotFoundError("文章", str(article_id))

# ❌ 错误
if not article:
    raise Exception("文章不存在")
```

### ✅ 4. 使用异步函数

```python
# ✅ 正确
async def get_article(db: AsyncSession, article_id: int):
    result = await db.execute(select(Article).where(Article.id == article_id))
    return result.scalar_one_or_none()

# ❌ 错误：在异步项目中使用同步函数
def get_article(db, article_id):
    return db.query(Article).filter(Article.id == article_id).first()
```

---

## 测试要求

### 测试文件组织

```
backend/tests/
├── test_models.py          # 模型测试
├── test_api.py             # API 测试
├── test_services.py        # 服务层测试
└── test_*.py               # 其他测试
```

### 测试命名规范

```python
# 测试函数命名：test_{功能}_{场景}
def test_create_article_success():
    """测试成功创建文章"""
    pass

def test_create_article_validation_error():
    """测试创建文章时验证失败"""
    pass
```

### 测试覆盖要求

- **核心业务逻辑**：必须有测试
- **API 端点**：建议有测试
- **工具函数**：建议有测试

---

## 代码审查清单

### 提交前检查

- [ ] 代码遵循 PEP 8 规范
- [ ] 所有函数都有类型注解
- [ ] 所有公共函数都有文档字符串
- [ ] 没有使用禁止模式
- [ ] 异常处理正确
- [ ] 日志记录适当
- [ ] 没有硬编码的敏感信息
- [ ] 测试通过（如果有）

### 审查要点

1. **代码结构**
   - 是否遵循分层架构（API → Service → Model）
   - 是否有循环依赖

2. **错误处理**
   - 是否使用自定义异常
   - 是否记录错误日志
   - 是否有适当的错误恢复

3. **性能**
   - 是否有 N+1 查询
   - 是否有不必要的数据库查询
   - 是否使用了索引

4. **安全性**
   - 是否有 SQL 注入风险
   - 是否暴露敏感信息
   - 是否验证用户输入

---

## 常见错误

### 1. 忘记 await

```python
# ❌ 错误
result = db.execute(select(Article))  # 忘记 await

# ✅ 正确
result = await db.execute(select(Article))
```

### 2. 忘记处理 None

```python
# ❌ 错误
article = result.scalar_one()  # 如果不存在会抛出异常

# ✅ 正确
article = result.scalar_one_or_none()
if not article:
    raise NotFoundError("文章", str(article_id))
```

### 3. 在异步函数中使用同步代码

```python
# ❌ 错误
async def process_file():
    with open("file.txt") as f:  # 阻塞 I/O
        content = f.read()

# ✅ 正确
async def process_file():
    async with aiofiles.open("file.txt") as f:
        content = await f.read()
```

---

## 参考示例

- **良好的 API 实现**：`backend/app/api/articles.py`
- **良好的服务实现**：`backend/app/services/unified_ai_service.py`
- **良好的模型定义**：`backend/app/models/article.py`

---

## 总结

- 遵循 **PEP 8** 规范
- 使用 **类型注解** 和 **文档字符串**
- 遵循 **分层架构**（API → Service → Model）
- 使用 **自定义异常** 和 **依赖注入**
- 避免 **禁止模式**
