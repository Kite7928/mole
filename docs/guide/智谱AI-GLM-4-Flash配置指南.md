# 智谱 AI (GLM-4-Flash) 配置指南

## 概述

智谱 AI 是国内领先的大语言模型服务商，GLM-4-Flash 是其推出的超快响应模型，适合需要快速生成内容的场景。

## 配置步骤

### 1. 获取 API Key

1. 访问智谱 AI 开放平台：https://open.bigmodel.cn/
2. 注册并登录账号
3. 进入 API 密钥管理页面
4. 创建新的 API Key

### 2. 配置环境变量

在 `backend/.env` 文件中添加以下配置：

```env
# 智谱 AI 配置
ZHIPU_API_KEY=your-zhipu-api-key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-4-flash
```

### 3. 通过界面配置

1. 访问系统设置页面：`http://localhost:3000/settings`
2. 在 AI 配置部分选择"智谱 AI"
3. 输入 API Key
4. 保存配置

## 支持的模型

- **glm-4-flash**: 超快响应模型（推荐）
- **glm-4**: 主力模型
- **glm-4-air**: 轻量级模型
- **glm-4-plus**: 增强版模型

## 模型特点

### GLM-4-Flash

- **响应速度**: 极快，适合实时对话
- **上下文长度**: 支持 128k tokens
- **价格**: 性价比高
- **适用场景**: 快速生成标题、摘要、短文

### GLM-4

- **性能**: 综合能力强
- **上下文长度**: 支持 128k tokens
- **适用场景**: 深度内容生成、长文写作

### GLM-4-Plus

- **性能**: 最强模型
- **上下文长度**: 支持 128k tokens
- **适用场景**: 复杂任务、高质量内容

## API 调用示例

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="your-zhipu-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4"
)

response = await client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "user", "content": "你好，请介绍一下智谱 AI"}
    ],
    temperature=0.7,
    max_tokens=2000
)

print(response.choices[0].message.content)
```

## 注意事项

1. **API Key 安全**: 不要将 API Key 提交到代码仓库
2. **速率限制**: 免费版有调用次数限制，付费版可提升限额
3. **计费**: 按实际使用的 tokens 计费
4. **网络要求**: 需要能够访问智谱 AI 的 API 服务器

## 故障排查

### 连接失败

- 检查网络连接
- 确认 API Key 是否正确
- 检查服务是否可用：https://open.bigmodel.cn/

### 认证失败

- 确认 API Key 是否有效
- 检查 API Key 是否有足够的余额

### 响应超时

- 增加超时时间配置
- 考虑使用更快的模型（如 glm-4-flash）

## 价格参考

（具体价格请以官方文档为准：https://open.bigmodel.cn/pricing）

| 模型 | 价格 (元/千 tokens) |
|------|-------------------|
| glm-4-flash | ¥0.0001 |
| glm-4 | ¥0.001 |
| glm-4-plus | ¥0.002 |

## 相关链接

- 智谱 AI 开放平台：https://open.bigmodel.cn/
- API 文档：https://open.bigmodel.cn/dev/api
- 模型介绍：https://open.bigmodel.cn/models
- 价格说明：https://open.bigmodel.cn/pricing

## 技术支持

- 智谱 AI 社区：https://open.bigmodel.cn/usercenter
- 开发者文档：https://open.bigmodel.cn/dev/api

---

**提示**: 配置完成后，建议先进行测试调用，确保一切正常后再投入使用。