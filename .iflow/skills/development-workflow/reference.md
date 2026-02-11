# Development Workflow - 技术参考

本文档提供了 development-workflow Skill 的详细技术参考。

## 目录

1. [工具使用指南](#工具使用指南)
2. [评分标准详解](#评分标准详解)
3. [代码规范详解](#代码规范详解)
4. [测试规范详解](#测试规范详解)
5. [架构原则详解](#架构原则详解)
6. [常见错误与解决方案](#常见错误与解决方案)

---

## 工具使用指南

### sequential-thinking

**用途**：深度思考和分析问题

**使用场景**：
- 分析问题本质和需求
- 识别现有实现和模式
- 绘制依赖关系和集成点
- 评估技术方案和风险

**最佳实践**：
1. 至少分析 3 个现有实现或模式
2. 识别可复用的接口与约束
3. 确认输入输出协议、配置与环境需求
4. 弄清现有测试框架、命名约定和格式化规则

**输出格式**：
```
思考步骤 1: [问题描述]
思考步骤 2: [分析现有实现]
思考步骤 3: [技术方案建议]
思考步骤 4: [风险评估]
...
结论: [最终建议]
```

### task-manager / todo_write

**用途**：任务规划和拆分

**使用场景**：
- 将复杂任务拆分为可执行步骤
- 绘制依赖关系图
- 确定优先级

**最佳实践**：
1. 涉及修改超过 3 个文件的任务，必须先分解
2. 每个任务应该是独立可执行的
3. 明确任务之间的依赖关系
4. 设置合理的优先级

**输出格式**：
```json
{
  "tasks": [
    {
      "id": "1",
      "task": "任务描述",
      "status": "pending|in_progress|completed",
      "priority": "high|medium|low"
    }
  ]
}
```

### desktop-commander

**用途**：本地文件和数据分析（最高优先级）

**使用场景**：
- 任何本地文件操作
- CSV/JSON/数据分析
- 进程管理

**核心能力**：

#### 文件操作
```python
# 读取文件
read_file(absolute_path)

# 写入文件
write_file(file_path, content)

# 精确编辑
edit_block(file_path, old_string, new_string)
```

#### 目录管理
```python
# 列出目录
list_directory(path)

# 创建目录
create_directory(path)

# 移动文件
move_file(src, dst)
```

#### 搜索
```python
# 文件名和内容搜索
start_search(path, pattern, options)
```

#### 进程管理
```python
# 启动进程
start_process(command)

# 交互式 REPL
interact_with_process(process_id, input_data)
```

**最佳实践**：
1. 本地文件分析必须用此工具（不用 analysis 工具）
2. 使用 `edit_block` 进行精确文本替换（比 sed/awk 更安全）
3. 使用绝对路径以保证可靠性
4. 绝对优先于 bash 命令

**示例**：
```python
# 分析 CSV 文件
start_process("python3 -i")
interact_with_process(pid, "import pandas as pd\ndf = pd.read_csv('data.csv')\ndf.describe()")
```

### context7

**用途**：编程库/SDK/API 文档检索

**使用场景**：
- 查询编程库文档
- 获取 API 使用方法
- 查找最佳实践示例

**调用方式**：
```python
# 1. 获取库 ID
resolve-library-id(libraryName)

# 2. 获取文档
get-library-docs(context7CompatibleLibraryID, topic, tokens)
```

**示例**：
```python
# 查询 React hooks 文档
library_id = resolve-library-id("react")
docs = get-library-docs(library_id, topic="hooks")
```

**优势**：
- 专门优化编程上下文
- Token 高效
- 最新官方文档

### github

**用途**：GitHub 代码搜索和协作

**使用场景**：
- 搜索开源代码
- 创建和管理 PR
- 管理Issues

**核心能力**：

#### 代码搜索
```python
search_code(q, page, per_page)
search_repositories(query, page, perPage)
```

#### PR 管理
```python
create_pull_request(owner, repo, title, body, head, base)
get_pull_request(owner, repo, pull_number)
merge_pull_request(owner, repo, pull_number)
```

#### Issue 管理
```python
create_issue(owner, repo, title, body)
update_issue(owner, repo, issue_number, ...)
list_issues(owner, repo, ...)
```

**最佳实践**：
- 搜索代码时使用 `search_code`（比 firecrawl 更精准）
- 创建 PR 前先调用 `get_pull_request_diff` 检查变更
- 使用 `request_copilot_review` 进行自动代码审查

**示例**：
```python
# 搜索 FastAPI 评论系统实现
results = search_code("FastAPI comment system API", per_page=10)
```

### web_fetch

**用途**：网页内容获取

**使用场景**：
- 仅在无法通过上述方式获取信息时使用
- 获取最新的技术文档和教程

**最佳实践**：
1. 必须在日志中声明来源和用途
2. 检索失败时，必须在日志中声明并改用替代方法
3. 优先使用官方文档和权威来源

---

## 评分标准详解

### 技术维度（60 分）

#### 代码质量（20 分）

**评分标准**：
- 18-20 分：代码规范、可读性强、易于维护
- 15-17 分：代码规范、可读性良好、基本可维护
- 10-14 分：代码基本规范、可读性一般、维护性一般
- 0-9 分：代码不规范、难以阅读、难以维护

**检查项**：
- ✅ 遵循编程语言标准代码风格
- ✅ 遵循项目既有风格规范
- ✅ 变量命名清晰、有意义
- ✅ 函数职责单一
- ✅ 避免重复代码（DRY）
- ✅ 注释清晰准确（使用简体中文）

#### 测试覆盖（20 分）

**评分标准**：
- 18-20 分：测试覆盖率高（>80%）、测试质量高
- 15-17 分：测试覆盖率良好（60-80%）、测试质量良好
- 10-14 分：测试覆盖率一般（40-60%）、测试质量一般
- 0-9 分：测试覆盖率低（<40%）、测试质量差

**检查项**：
- ✅ 提供单元测试
- ✅ 提供集成测试
- ✅ 测试覆盖正常流程
- ✅ 测试覆盖边界条件
- ✅ 测试覆盖错误恢复
- ✅ 测试可自动运行

#### 规范遵循（20 分）

**评分标准**：
- 18-20 分：严格遵循所有规范
- 15-17 分：基本遵循规范，有少量偏差
- 10-14 分：部分遵循规范，有明显偏差
- 0-9 分：严重违反规范

**检查项**：
- ✅ 遵循 SOLID 原则
- ✅ 遵循 DRY 原则
- ✅ 遵循关注点分离原则
- ✅ 使用简体中文注释
- ✅ 无 MVP 或占位符
- ✅ 完整实现功能

### 战略维度（40 分）

#### 需求匹配（15 分）

**评分标准**：
- 13-15 分：完全满足需求，无遗漏
- 10-12 分：基本满足需求，有少量遗漏
- 7-9 分：部分满足需求，有明显遗漏
- 0-6 分：严重偏离需求

**检查项**：
- ✅ 需求字段完整性
- ✅ 覆盖原始意图无遗漏
- ✅ 交付物映射明确

#### 架构一致（15 分）

**评分标准**：
- 13-15 分：完全符合项目架构
- 10-12 分：基本符合项目架构，有少量偏差
- 7-9 分：部分符合项目架构，有明显偏差
- 0-6 分：严重偏离项目架构

**检查项**：
- ✅ 复用官方 SDK 或社区成熟方案
- ✅ 符合项目技术栈
- ✅ 符合项目设计模式
- ✅ 避免引入新技术债

#### 风险评估（10 分）

**评分标准**：
- 9-10 分：风险评估充分，无新风险
- 7-8 分：风险评估良好，有少量可控风险
- 5-6 分：风险评估一般，有可控风险
- 0-4 分：风险评估不足，有重大风险

**检查项**：
- ✅ 依赖与风险评估完毕
- ✅ 性能评估充分
- ✅ 安全评估充分（安全需求优先级最低）
- ✅ 兼容性评估充分

---

## 代码规范详解

### Python 代码规范

#### 命名规范
```python
# 类名：大驼峰
class UserService:
    pass

# 函数和变量：小写+下划线
def get_user_data(user_id):
    pass

# 常量：大写+下划线
MAX_RETRY_COUNT = 3

# 私有变量：前导下划线
def _internal_method():
    pass
```

#### 注释规范
```python
def calculate_total(price, quantity, discount=0):
    """
    计算订单总价
    
    Args:
        price: 商品单价
        quantity: 商品数量
        discount: 折扣率（0-1），默认为0
    
    Returns:
        订单总价
    
    Example:
        >>> calculate_total(100, 2, 0.1)
        180.0
    """
    subtotal = price * quantity
    total = subtotal * (1 - discount)
    return total
```

#### 类型注解
```python
from typing import List, Optional

def get_users(active_only: bool = False) -> List[dict]:
    """
    获取用户列表
    
    Args:
        active_only: 是否只返回活跃用户
    
    Returns:
        用户列表
    """
    pass
```

### TypeScript 代码规范

#### 命名规范
```typescript
// 接口：大驼峰
interface User {
  id: number
  name: string
}

// 类：大驼峰
class UserService {
  private users: User[] = []
}

// 函数和变量：小驼峰
function getUserData(userId: number): User {
  return {} as User
}

// 常量：大写+下划线
const MAX_RETRY_COUNT = 3

// 类型别名：大驼峰
type UserData = {
  id: number
  name: string
}
```

#### 注释规范
```typescript
/**
 * 计算订单总价
 * 
 * @param price - 商品单价
 * @param quantity - 商品数量
 * @param discount - 折扣率（0-1），默认为0
 * @returns 订单总价
 * 
 * @example
 * calculateTotal(100, 2, 0.1) // 返回 180.0
 */
function calculateTotal(
  price: number,
  quantity: number,
  discount: number = 0
): number {
  const subtotal = price * quantity
  const total = subtotal * (1 - discount)
  return total
}
```

---

## 测试规范详解

### Python 测试规范

#### 单元测试
```python
import pytest
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_get_user_by_id():
    """测试根据 ID 获取用户"""
    # 准备测试数据
    user_service = UserService()
    user_id = 1
    
    # 执行测试
    user = await user_service.get_user_by_id(user_id)
    
    # 验证结果
    assert user is not None
    assert user.id == user_id
    assert user.username == "test_user"

@pytest.mark.asyncio
async def test_get_user_not_found():
    """测试获取不存在的用户"""
    user_service = UserService()
    
    # 执行测试
    user = await user_service.get_user_by_id(999)
    
    # 验证结果
    assert user is None
```

#### 集成测试
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_api(client: AsyncClient):
    """测试创建用户 API"""
    # 准备测试数据
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test123"
    }
    
    # 执行测试
    response = await client.post("/api/users/", json=user_data)
    
    # 验证结果
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"
    assert "id" in data
    assert "password" not in data  # 密码不应返回
```

### TypeScript 测试规范

#### 单元测试
```typescript
import { render, screen } from '@testing-library/react'
import { UserCard } from './UserCard'

describe('UserCard', () => {
  it('显示用户信息', () => {
    // 准备测试数据
    const user = {
      id: 1,
      name: '张三',
      email: 'zhangsan@example.com'
    }
    
    // 执行测试
    render(<UserCard user={user} />)
    
    // 验证结果
    expect(screen.getByText('张三')).toBeInTheDocument()
    expect(screen.getByText('zhangsan@example.com')).toBeInTheDocument()
  })
  
  it('点击时触发回调', () => {
    const user = { id: 1, name: '张三', email: 'zhangsan@example.com' }
    const onClick = jest.fn()
    
    render(<UserCard user={user} onClick={onClick} />)
    
    screen.getByText('张三').click()
    
    expect(onClick).toHaveBeenCalledWith(user)
  })
})
```

---

## 架构原则详解

### SOLID 原则

#### S - 单一职责原则（Single Responsibility Principle）
```python
# ❌ 错误示例：一个类承担多个职责
class UserManager:
    def create_user(self, user_data):
        pass
    
    def send_welcome_email(self, user):
        pass
    
    def log_user_activity(self, user, action):
        pass

# ✅ 正确示例：每个类只承担一个职责
class UserService:
    def create_user(self, user_data):
        pass

class EmailService:
    def send_welcome_email(self, user):
        pass

class LoggingService:
    def log_user_activity(self, user, action):
        pass
```

#### O - 开闭原则（Open/Closed Principle）
```python
# ❌ 错误示例：修改现有代码
class OrderProcessor:
    def process(self, order):
        if order.type == "normal":
            return self._process_normal(order)
        elif order.type == "express":
            return self._process_express(order)
        # 每次新增订单类型都需要修改这里

# ✅ 正确示例：扩展而非修改
class OrderProcessor:
    def __init__(self):
        self.strategies = {}
    
    def register_strategy(self, order_type, strategy):
        self.strategies[order_type] = strategy
    
    def process(self, order):
        strategy = self.strategies.get(order.type)
        if strategy:
            return strategy.process(order)
        raise ValueError(f"Unknown order type: {order.type}")
```

#### L - 里氏替换原则（Liskov Substitution Principle）
```python
# ✅ 正确示例：子类可以替换父类
class Bird:
    def fly(self):
        pass

class Sparrow(Bird):
    def fly(self):
        # 麻雀可以飞
        pass

class Ostrich(Bird):
    def fly(self):
        # 鸵鸟不能飞，违反里氏替换原则
        raise NotImplementedError("Ostrich cannot fly")

# 更好的设计
class Bird:
    pass

class FlyingBird(Bird):
    def fly(self):
        pass

class Sparrow(FlyingBird):
    def fly(self):
        pass

class Ostrich(Bird):
    # 鸵鸟继承自 Bird，而不是 FlyingBird
    pass
```

#### I - 接口隔离原则（Interface Segregation Principle）
```python
# ❌ 错误示例：臃肿的接口
class Worker:
    def work(self):
        pass
    
    def eat(self):
        pass
    
    def sleep(self):
        pass

# ✅ 正确示例：分离接口
class Workable:
    def work(self):
        pass

class Eatable:
    def eat(self):
        pass

class Sleepable:
    def sleep(self):
        pass

class Robot(Workable):
    def work(self):
        pass
    # 机器人不需要 eat 和 sleep
```

#### D - 依赖倒置原则（Dependency Inversion Principle）
```python
# ❌ 错误示例：依赖具体实现
class LightBulb:
    def turn_on(self):
        pass

class Switch:
    def __init__(self):
        self.bulb = LightBulb()  # 依赖具体实现
    
    def toggle(self):
        self.bulb.turn_on()

# ✅ 正确示例：依赖抽象
class Switchable(ABC):
    @abstractmethod
    def turn_on(self):
        pass

class LightBulb(Switchable):
    def turn_on(self):
        pass

class Switch:
    def __init__(self, device: Switchable):
        self.device = device  # 依赖抽象
    
    def toggle(self):
        self.device.turn_on()
```

### DRY 原则（Don't Repeat Yourself）

```python
# ❌ 错误示例：重复代码
def calculate_circle_area(radius):
    return 3.14159 * radius * radius

def calculate_circle_circumference(radius):
    return 2 * 3.14159 * radius

# ✅ 正确示例：提取常量
PI = 3.14159

def calculate_circle_area(radius):
    return PI * radius * radius

def calculate_circle_circumference(radius):
    return 2 * PI * radius
```

### 关注点分离原则

```python
# ❌ 错误示例：混合多个关注点
def create_user_and_send_email(user_data):
    # 数据验证
    if not user_data.get("username"):
        raise ValueError("Username is required")
    
    # 数据库操作
    user = User(**user_data)
    db.add(user)
    db.commit()
    
    # 发送邮件
    send_email(user.email, "Welcome!")

# ✅ 正确示例：分离关注点
class UserService:
    def create_user(self, user_data):
        # 数据验证和数据库操作
        if not user_data.get("username"):
            raise ValueError("Username is required")
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        return user

class EmailService:
    def send_welcome_email(self, user):
        # 发送邮件
        send_email(user.email, "Welcome!")

class UserRegistration:
    def __init__(self, user_service, email_service):
        self.user_service = user_service
        self.email_service = email_service
    
    def register(self, user_data):
        user = self.user_service.create_user(user_data)
        self.email_service.send_welcome_email(user)
        return user
```

---

## 常见错误与解决方案

### 错误 1：违反中文规范

**错误现象**：
```python
# ❌ 使用英文注释
def get_user(user_id):
    """Get user by ID"""
    pass
```

**解决方案**：
```python
# ✅ 使用中文注释
def get_user(user_id):
    """根据 ID 获取用户"""
    pass
```

### 错误 2：使用 MVP 或占位符

**错误现象**：
```python
# ❌ 使用占位符
def process_data(data):
    # TODO: 实现数据处理逻辑
    pass
```

**解决方案**：
```python
# ✅ 完整实现
def process_data(data):
    """处理数据"""
    if not data:
        return []
    
    validated = validate_data(data)
    processed = transform_data(validated)
    return processed
```

### 错误 3：缺少测试

**错误现象**：
```python
# ❌ 只写代码，不写测试
def calculate_discount(price, discount_rate):
    return price * (1 - discount_rate)
```

**解决方案**：
```python
# ✅ 完整实现 + 测试
def calculate_discount(price, discount_rate):
    """计算折扣价格"""
    return price * (1 - discount_rate)

# 测试
import pytest

@pytest.mark.parametrize("price,discount,expected", [
    (100, 0.1, 90),
    (200, 0.2, 160),
    (50, 0, 50),
])
def test_calculate_discount(price, discount, expected):
    assert calculate_discount(price, discount) == expected
```

### 错误 4：重复代码

**错误现象**：
```python
# ❌ 重复代码
def get_user_from_cache(user_id):
    key = f"user:{user_id}"
    return cache.get(key)

def get_product_from_cache(product_id):
    key = f"product:{product_id}"
    return cache.get(key)
```

**解决方案**：
```python
# ✅ 提取公共逻辑
def get_from_cache(prefix, id):
    """从缓存获取数据"""
    key = f"{prefix}:{id}"
    return cache.get(key)

def get_user_from_cache(user_id):
    return get_from_cache("user", user_id)

def get_product_from_cache(product_id):
    return get_from_cache("product", product_id)
```

### 错误 5：函数职责不单一

**错误现象**：
```python
# ❌ 一个函数做太多事
def process_order(order):
    # 验证订单
    if not order.items:
        raise ValueError("Order is empty")
    
    # 计算总价
    total = sum(item.price * item.quantity for item in order.items)
    
    # 更新库存
    for item in order.items:
        item.product.stock -= item.quantity
    
    # 创建支付
    payment = create_payment(total)
    
    # 发送确认邮件
    send_email(order.user.email, "Order confirmed")
    
    return payment
```

**解决方案**：
```python
# ✅ 拆分为多个函数
def validate_order(order):
    """验证订单"""
    if not order.items:
        raise ValueError("Order is empty")

def calculate_order_total(order):
    """计算订单总价"""
    return sum(item.price * item.quantity for item in order.items)

def update_inventory(order):
    """更新库存"""
    for item in order.items:
        item.product.stock -= item.quantity

def process_order(order):
    """处理订单"""
    validate_order(order)
    total = calculate_order_total(order)
    update_inventory(order)
    payment = create_payment(total)
    send_email(order.user.email, "Order confirmed")
    return payment
```

---

## 更多资源

- [SKILL.md](./SKILL.md) - 主文档
- [examples.md](./examples.md) - 使用示例
- [templates/](./templates/) - 模板文件