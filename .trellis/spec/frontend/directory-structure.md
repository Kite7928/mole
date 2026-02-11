# 前端目录结构

> 本项目前端代码的组织方式和目录结构规范

---

## 概览

本项目使用 **Next.js 13+ App Router** + **TypeScript** + **Tailwind CSS**，采用组件化开发模式。

---

## 目录布局

```
frontend/
├── app/                      # Next.js 13+ App Router 页面
│   ├── page.tsx              # 首页（仪表盘）
│   ├── layout.tsx            # 根布局
│   ├── globals.css           # 全局样式
│   ├── articles/             # 文章管理模块
│   │   ├── page.tsx          # 文章列表页
│   │   └── create/           # 创建文章页
│   │       └── page.tsx
│   ├── hotspots/             # 热点监控模块
│   │   └── page.tsx
│   ├── publish/              # 多平台发布模块
│   │   └── page.tsx
│   └── settings/             # 系统设置模块
│       └── page.tsx
│
├── components/               # React 组件
│   ├── ui/                   # 基础 UI 组件（shadcn/ui）
│   │   ├── button.tsx        # 按钮组件
│   │   ├── card.tsx          # 卡片组件
│   │   ├── tabs.tsx          # 标签页组件
│   │   ├── badge.tsx         # 徽章组件
│   │   ├── progress.tsx      # 进度条组件
│   │   ├── skeleton.tsx      # 骨架屏组件
│   │   ├── toast.tsx         # 提示组件
│   │   └── ...
│   ├── layout/               # 布局组件
│   │   ├── sidebar.tsx       # 侧边栏
│   │   ├── header.tsx        # 顶部栏
│   │   ├── resizable-sidebar.tsx  # 可调整大小的侧边栏
│   │   └── brightness-control.tsx # 亮度控制
│   ├── charts/               # 图表组件
│   │   ├── data-chart.tsx    # 数据图表
│   │   └── chart-generator.tsx # 图表生成器
│   ├── onboarding/           # 引导组件
│   │   ├── onboarding-modal.tsx
│   │   ├── onboarding-tooltip.tsx
│   │   └── config-wizard.tsx
│   ├── skeletons/            # 骨架屏组件
│   │   └── article-card-skeleton.tsx
│   ├── ai-provider-status.tsx      # AI 提供商状态
│   ├── multiplatform-publish-dialog.tsx  # 多平台发布对话框
│   └── theme-init.tsx        # 主题初始化
│
├── lib/                      # 工具函数和配置
│   ├── api.ts                # API 请求封装
│   ├── utils.ts              # 通用工具函数
│   ├── error-handler.ts      # 错误处理
│   ├── store.ts              # 状态管理（Zustand）
│   └── theme-store.ts        # 主题状态管理
│
├── public/                   # 静态资源
│   └── ...
│
├── package.json              # 依赖配置
├── tsconfig.json             # TypeScript 配置
├── tailwind.config.ts        # Tailwind CSS 配置
└── next.config.js            # Next.js 配置
```

---

## 模块组织原则

### 1. 页面层（`app/`）

**职责**：
- 定义路由和页面结构
- 数据获取和状态管理
- 页面级布局

**命名规范**：
- 页面文件：`page.tsx`
- 布局文件：`layout.tsx`
- 加载状态：`loading.tsx`
- 错误处理：`error.tsx`

**示例**：`frontend/app/articles/page.tsx`

```tsx
'use client'

import { useEffect, useState } from 'react'
import { API_URL } from '@/lib/api'

export default function ArticlesPage() {
  const [articles, setArticles] = useState([])

  useEffect(() => {
    fetchArticles()
  }, [])

  const fetchArticles = async () => {
    const response = await fetch(`${API_URL}/api/articles`)
    const data = await response.json()
    setArticles(data.articles || [])
  }

  return (
    <div>
      {/* 页面内容 */}
    </div>
  )
}
```

### 2. 组件层（`components/`）

**职责**：
- 可复用的 UI 组件
- 业务逻辑组件
- 布局组件

**组织方式**：
- **基础 UI 组件**（`ui/`）：通用的、无业务逻辑的组件
- **布局组件**（`layout/`）：页面布局相关组件
- **业务组件**（根目录）：包含业务逻辑的组件

**命名规范**：
- 文件名：小写 + 连字符（`kebab-case`）
  - ✅ `sidebar.tsx`
  - ✅ `data-chart.tsx`
  - ❌ `Sidebar.tsx`
  - ❌ `dataChart.tsx`

- 组件名：大驼峰（`PascalCase`）
  - ✅ `Sidebar`
  - ✅ `DataChart`
  - ❌ `sidebar`

**示例**：`frontend/components/ui/button.tsx`

```tsx
import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', ...props }, ref) => {
    return (
      <button
        className={cn(/* 样式类 */, className)}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
```

### 3. 工具层（`lib/`）

**职责**：
- API 请求封装
- 通用工具函数
- 状态管理
- 类型定义

**命名规范**：
- 文件名：小写 + 连字符（`kebab-case`）
  - ✅ `api.ts`
  - ✅ `error-handler.ts`
  - ❌ `API.ts`
  - ❌ `errorHandler.ts`

**示例**：`frontend/lib/api.ts`

```tsx
// API 基础 URL 配置
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 通用请求封装
export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(endpoint, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(error.detail || error.message)
  }

  return response.json()
}
```

---

## 命名约定

### 文件命名

- **页面文件**：`page.tsx`（Next.js 约定）
- **组件文件**：小写 + 连字符（`kebab-case`）
  - ✅ `sidebar.tsx`
  - ✅ `data-chart.tsx`
  - ❌ `Sidebar.tsx`

- **工具文件**：小写 + 连字符（`kebab-case`）
  - ✅ `api.ts`
  - ✅ `error-handler.ts`

### 代码命名

- **组件名**：大驼峰（`PascalCase`）
  - ✅ `Sidebar`
  - ✅ `DataChart`
  - ❌ `sidebar`

- **函数名**：小驼峰（`camelCase`）
  - ✅ `fetchArticles`
  - ✅ `handleSubmit`
  - ❌ `FetchArticles`

- **变量名**：小驼峰（`camelCase`）
  - ✅ `articleList`
  - ✅ `isLoading`
  - ❌ `ArticleList`

- **常量名**：大写 + 下划线（`UPPER_SNAKE_CASE`）
  - ✅ `API_URL`
  - ✅ `MAX_RETRIES`
  - ❌ `apiUrl`

- **类型/接口名**：大驼峰（`PascalCase`）
  - ✅ `ArticleResponse`
  - ✅ `ButtonProps`
  - ❌ `articleResponse`

---

## 新功能开发流程

### 添加新页面

1. **创建页面目录**：`app/{功能}/page.tsx`
2. **创建页面组件**：
   ```tsx
   'use client'

   export default function NewFeaturePage() {
     return <div>新功能页面</div>
   }
   ```
3. **添加到导航**：在 `components/layout/sidebar.tsx` 中添加导航项

### 添加新组件

1. **确定组件类型**：
   - 基础 UI 组件 → `components/ui/`
   - 布局组件 → `components/layout/`
   - 业务组件 → `components/`

2. **创建组件文件**：`components/{类型}/{组件名}.tsx`
3. **定义组件**：
   ```tsx
   import * as React from "react"

   export interface NewComponentProps {
     // Props 定义
   }

   export function NewComponent({ ...props }: NewComponentProps) {
     return <div>新组件</div>
   }
   ```

---

## 反模式（禁止）

### ❌ 不要在页面中写复杂的业务逻辑

```tsx
// ❌ 错误
export default function ArticlesPage() {
  // 大量复杂的业务逻辑
  const processArticles = () => {
    // 100+ 行代码
  }

  return <div>...</div>
}
```

```tsx
// ✅ 正确：提取到自定义 Hook 或工具函数
export default function ArticlesPage() {
  const { articles, processArticles } = useArticles()

  return <div>...</div>
}
```

### ❌ 不要使用内联样式

```tsx
// ❌ 错误
<div style={{ color: 'red', fontSize: '16px' }}>文本</div>

// ✅ 正确：使用 Tailwind CSS
<div className="text-red-500 text-base">文本</div>
```

### ❌ 不要直接修改 props

```tsx
// ❌ 错误
function Component({ data }) {
  data.value = 'new value'  // 直接修改 props
  return <div>{data.value}</div>
}

// ✅ 正确：使用状态管理
function Component({ data }) {
  const [value, setValue] = useState(data.value)
  return <div>{value}</div>
}
```

---

## 参考示例

### 良好组织的模块

- **首页**：`app/page.tsx`
- **文章管理**：`app/articles/page.tsx` + `components/`
- **侧边栏**：`components/layout/sidebar.tsx`
- **按钮组件**：`components/ui/button.tsx`
- **API 封装**：`lib/api.ts`

---

## 总结

- 使用 **Next.js 13+ App Router** 组织页面
- 组件按 **功能和类型** 分类存放
- 遵循 **命名规范**（文件名 kebab-case，组件名 PascalCase）
- **分离关注点**（页面、组件、工具）
- 使用 **Tailwind CSS** 而不是内联样式
