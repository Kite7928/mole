# Cogview-3-Flash 图片生成配置指南

## 概述

Cogview-3-Flash 是智谱AI（Zhipu AI）提供的快速图片生成模型，具有以下特点：
- 🚀 快速生成：相比传统模型，生成速度更快
- 🎨 高质量：支持生成高质量、细节丰富的图片
- 💡 智能理解：能够准确理解中文提示词
- 🌐 国内访问：服务部署在国内，访问更稳定

## 配置步骤

### 1. 获取 API Key

1. 访问智谱AI开放平台：https://open.bigmodel.cn/
2. 注册账号并登录
3. 进入"API Key"页面
4. 创建新的 API Key
5. 复制 API Key

### 2. 配置环境变量

编辑 `backend/.env` 文件，添加以下配置：

```env
# Image Generation - Cogview (Zhipu AI)
COGVIEW_API_KEY=你的智谱AI_API密钥
COGVIEW_BASE_URL=https://open.bigmodel.cn/api/paas/v4/images/generations
COGVIEW_MODEL=cogview-3-flash
```

**配置说明**：
- `COGVIEW_API_KEY`: 从智谱AI平台获取的 API 密钥
- `COGVIEW_BASE_URL`: Cogview API 地址（默认配置，无需修改）
- `COGVIEW_MODEL`: 模型名称（默认 cogview-3-flash）

### 3. 重启后端服务

```powershell
# 停止现有服务
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 启动新服务
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 使用方法

### 前端使用

1. 访问文章创建页面：http://localhost:3000/articles/create
2. 在"输入主题"步骤中：
   - 输入文章主题
   - 选择 AI 模型和写作风格
   - ✅ 勾选"生成技术配图"
   - 选择图片生成模型：
     - **Cogview-3-Flash**（推荐）⚡
     - DALL-E 3
     - Midjourney
     - Stable Diffusion
3. 继续完成文章生成流程
4. 保存草稿或发布时，系统会自动生成封面图

### API 调用示例

```typescript
// 创建文章时生成封面图
const article = await createArticle({
  title: "文章标题",
  content: "文章内容",
  summary: "文章摘要",
  source_topic: "文章主题",
  status: "draft",
  tags: ["标签1", "标签2"],
  generate_cover_image: true,  // 启用封面图生成
  image_provider: "cogview",    // 使用 Cogview-3-Flash
  image_style: "professional"   // 图片风格
});
```

## 支持的参数

### 图片尺寸

Cogview-3-Flash 支持以下尺寸：
- `1024x1024` - 正方形（推荐）
- `768x1344` - 竖向
- `1344x768` - 横向
- `864x864` - 小正方形

### 图片风格

- `professional` - 专业、清晰、现代
- `creative` - 创意、艺术、多彩
- `minimal` - 极简、优雅、简洁
- `vibrant` - 鲜艳、活力、醒目

## 注意事项

### 1. API 配额

- 智谱AI 提供免费配额和付费配额
- 新用户注册后可获得免费配额
- 建议定期检查配额使用情况

### 2. 图片质量

- Cogview-3-Flash 生成速度快，质量优秀
- 适合生成文章封面、配图等场景
- 对于专业设计需求，建议使用其他模型

### 3. 提示词优化

- 使用清晰、具体的中文描述
- 包含关键词：风格、主题、颜色等
- 示例：
  ```
  "创建一个关于AI技术的专业封面图，风格现代简洁，蓝色调"
  ```

### 4. 保存路径

- 生成的图片默认保存在 `backend/uploads/` 目录
- 文件名格式：`cover_{timestamp}_{hash}.jpg`
- 图片会自动裁剪为 900x383 尺寸（微信封面标准）

## 故障排查

### 问题 1：生成失败

**错误信息**：`Cogview API key not configured`

**解决方案**：
1. 检查 `backend/.env` 文件中是否配置了 `COGVIEW_API_KEY`
2. 确保 API Key 正确且有效
3. 检查 API Key 是否有配额剩余

### 问题 2：连接超时

**错误信息**：`Connection error` 或 `Timeout`

**解决方案**：
1. 检查网络连接
2. 确认智谱AI服务是否正常运行
3. 尝试使用代理（如需要）

### 问题 3：图片质量不佳

**解决方案**：
1. 优化提示词，使用更具体的描述
2. 调整 `image_style` 参数
3. 尝试不同的图片尺寸

## 成本说明

### 免费配额

- 新用户注册赠送一定量的免费配额
- 免费配额可用于测试和小规模使用

### 付费配额

- 超出免费配额后需要付费
- 计费方式：按生成次数计费
- 建议根据实际需求选择合适的套餐

### 节省成本的技巧

1. **使用模拟模式**：测试时禁用图片生成
2. **缓存结果**：相同主题复用已生成的图片
3. **批量生成**：一次生成多张图片供选择

## 最佳实践

### 1. 提示词编写

- ✅ 好的提示词：
  ```
  "创建一个关于人工智能的专业封面图，现代简约风格，蓝色科技感，包含电路板元素"
  ```

- ❌ 不好的提示词：
  ```
  "AI图片"
  ```

### 2. 风格选择

根据文章类型选择合适的风格：
- 技术文章 → `professional`
- 创意文章 → `creative`
- 极简文章 → `minimal`
- 活泼文章 → `vibrant`

### 3. 尺寸选择

- 文章封面：`1024x1024`（推荐）
- 竖向海报：`768x1344`
- 横向横幅：`1344x768`

## 相关文档

- [智谱AI官方文档](https://open.bigmodel.cn/dev/api)
- [图片生成服务源码](../backend/app/services/image_generation_service.py)
- [文章创建页面](../frontend/app/articles/create/page.tsx)

## 支持

如有问题，请联系：
- 智谱AI技术支持：https://open.bigmodel.cn/support
- 项目 Issues：https://github.com/Kite7928/mole/issues

---

**更新时间**：2026-02-08
**版本**：1.0.0