# 前端代码质量指南

> 本项目的前端代码质量标准、禁止模式和最佳实践

---

## 概览

本项目遵循 **React** 和 **TypeScript** 最佳实践，强调代码的可读性、可维护性和性能。

---

## 代码风格

### 命名规范

```tsx
// 组件名：大驼峰（PascalCase）
function ArticleCard() { }
function DataChart() { }

// 函数名：小驼峰（camelCase）
function fetchArticles() { }
function handleSubmit() { }

// 变量名：小驼峰（camelCase）
const articleList = []
const isLoading = false

// 常量名：大写+下划线（UPPER_SNAKE_CASE）
const API_URL = 'http://localhost:8000'
const MAX_RETRIES = 3

// 类型/接口名：大驼峰（PascalCase）
interface ArticleProps { }
type Status = 'pending' | 'success'
```

### 文件组织

```tsx
// ✅ 正确：清晰的文件结构
'use client'

// 1. 导入
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { fetchArticles } from '@/lib/api'

// 2. 类型定义
interface ComponentProps {
  title: string
}

// 3. 组件实现
export default function Component({ title }: ComponentProps) {
  // 状态
  const [data, setData] = useState([])

  // 副作用
  useEffect(() => {
    fetchArticles().then(setData)
  }, [])

  // 事件处理
  const handleClick = () => {
    console.log('clicked')
  }

  // 渲染
  return <div>{title}</div>
}
```

---

## 禁止模式

### ❌ 1. 不要使用 any

```tsx
// ❌ 错误：使用 any
function processData(data: any) {
  return data.value
}

// ✅ 正确：使用具体类型
function processData(data: Article) {
  return data.title
}
```

### ❌ 2. 不要在渲染中创建函数

```tsx
// ❌ 错误：每次渲染都创建新函数
function Component() {
  return (
    <button onClick={() => console.log('click')}>
      点击
    </button>
  )
}

// ✅ 正确：使用 useCallback
function Component() {
  const handleClick = useCallback(() => {
    console.log('click')
  }, [])

  return <button onClick={handleClick}>点击</button>
}
```

### ❌ 3. 不要使用内联样式

```tsx
// ❌ 错误：使用内联样式
<div style={{ color: 'red', fontSize: '16px' }}>文本</div>

// ✅ 正确：使用 Tailwind CSS
<div className="text-red-500 text-base">文本</div>
```

### ❌ 4. 不要忘记 key 属性

```tsx
// ❌ 错误：缺少 key
{articles.map(article => (
  <div>{article.title}</div>
))}

// ✅ 正确：添加 key
{articles.map(article => (
  <div key={article.id}>{article.title}</div>
))}
```

### ❌ 5. 不要直接修改 state

```tsx
// ❌ 错误：直接修改 state
const [items, setItems] = useState([])
items.push(newItem)  // 错误！

// ✅ 正确：创建新数组
setItems([...items, newItem])
```

---

## 必须遵循的模式

### ✅ 1. 使用 TypeScript 类型注解

```tsx
// ✅ 正确：完整的类型注解
interface ArticleCardProps {
  article: Article
  onEdit: (id: number) => void
  onDelete: (id: number) => void
}

function ArticleCard({ article, onEdit, onDelete }: ArticleCardProps) {
  return <div>{article.title}</div>
}
```

### ✅ 2. 使用 'use client' 指令

```tsx
// ✅ 正确：在使用客户端功能时添加指令
'use client'

import { useState } from 'react'

export default function Component() {
  const [count, setCount] = useState(0)
  return <div>{count}</div>
}
```

### ✅ 3. 使用 Tailwind CSS

```tsx
// ✅ 正确：使用 Tailwind 类名
<div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
  <span className="text-lg font-bold">标题</span>
</div>
```

### ✅ 4. 使用 cn 工具函数

```tsx
// ✅ 正确：使用 cn 合并类名
import { cn } from "@/lib/utils"

<button
  className={cn(
    "px-4 py-2 rounded-md",
    isActive && "bg-blue-600 text-white",
    className
  )}
>
  按钮
</button>
```

---

## 性能优化

### 1. 使用 React.memo

```tsx
// ✅ 正确：使用 memo 避免不必要的重新渲染
const ArticleCard = React.memo(function ArticleCard({ article }: Props) {
  return <div>{article.title}</div>
})
```

### 2. 使用 useCallback

```tsx
// ✅ 正确：缓存回调函数
const handleClick = useCallback(() => {
  console.log('clicked')
}, [])
```

### 3. 使用 useMemo

```tsx
// ✅ 正确：缓存计算结果
const sortedArticles = useMemo(() => {
  return articles.sort((a, b) => a.title.localeCompare(b.title))
}, [articles])
```

### 4. 懒加载组件

```tsx
// ✅ 正确：使用动态导入
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <div>加载中...</div>
})
```

---

## 错误处理

### 1. 使用错误边界

```tsx
// ✅ 正确：使用错误边界
'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return <div>出错了</div>
    }

    return this.props.children
  }
}
```

### 2. 处理异步错误

```tsx
// ✅ 正确：处理异步错误
async function fetchData() {
  try {
    const response = await fetch('/api/data')
    if (!response.ok) {
      throw new Error('请求失败')
    }
    return response.json()
  } catch (error) {
    console.error('获取数据失败:', error)
    throw error
  }
}
```

---

## 可访问性（A11y）

### 1. 使用语义化 HTML

```tsx
// ✅ 正确：使用语义化标签
<nav>
  <ul>
    <li><a href="/home">首页</a></li>
  </ul>
</nav>

// ❌ 错误：滥用 div
<div>
  <div>
    <div><a href="/home">首页</a></div>
  </div>
</div>
```

### 2. 添加 ARIA 属性

```tsx
// ✅ 正确：添加 ARIA 属性
<button
  aria-label="关闭对话框"
  aria-pressed={isPressed}
  onClick={handleClose}
>
  <X size={20} />
</button>
```

### 3. 支持键盘导航

```tsx
// ✅ 正确：支持键盘导航
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick()
    }
  }}
>
  可点击元素
</div>
```

---

## 测试要求

### 测试文件组织

```
frontend/
├── components/
│   └── ui/
│       ├── button.tsx
│       └── button.test.tsx  # 测试文件与组件同目录
└── lib/
    ├── utils.ts
    └── utils.test.ts
```

### 测试命名规范

```tsx
// 测试文件：{组件名}.test.tsx
// 测试用例：describe + it

describe('Button', () => {
  it('renders correctly', () => {
    // 测试逻辑
  })

  it('handles click events', () => {
    // 测试逻辑
  })
})
```

---

## 代码审查清单

### 提交前检查

- [ ] 代码遵循命名规范
- [ ] 所有组件都有 TypeScript 类型
- [ ] 使用 Tailwind CSS 而不是内联样式
- [ ] 没有使用 any 类型
- [ ] 列表渲染都有 key 属性
- [ ] 使用了 'use client' 指令（如需要）
- [ ] 没有直接修改 state
- [ ] 清理了所有副作用
- [ ] 添加了必要的 ARIA 属性

### 审查要点

1. **类型安全**
   - 是否使用了 TypeScript 类型
   - 是否避免了 any
   - 是否处理了 null/undefined

2. **性能**
   - 是否有不必要的重新渲染
   - 是否使用了 memo/useCallback/useMemo
   - 是否有内存泄漏

3. **可访问性**
   - 是否使用了语义化 HTML
   - 是否添加了 ARIA 属性
   - 是否支持键盘导航

4. **代码质量**
   - 是否遵循命名规范
   - 是否有重复代码
   - 是否有清晰的注释

---

## 常见错误

### 1. 忘记使用 'use client'

```tsx
// ❌ 错误：使用客户端功能但没有声明
import { useState } from 'react'

export default function Component() {
  const [count, setCount] = useState(0)  // 错误！
  return <div>{count}</div>
}

// ✅ 正确：添加 'use client' 指令
'use client'

import { useState } from 'react'

export default function Component() {
  const [count, setCount] = useState(0)
  return <div>{count}</div>
}
```

### 2. 依赖数组不完整

```tsx
// ❌ 错误：缺少依赖项
useEffect(() => {
  fetchUser(userId)
}, [])  // 缺少 userId

// ✅ 正确：包含所有依赖项
useEffect(() => {
  fetchUser(userId)
}, [userId])
```

### 3. 忘记清理副作用

```tsx
// ❌ 错误：没有清理
useEffect(() => {
  const subscription = subscribe()
}, [])

// ✅ 正确：返回清理函数
useEffect(() => {
  const subscription = subscribe()
  return () => subscription.unsubscribe()
}, [])
```

---

## 参考示例

- **良好的组件**：`components/ui/button.tsx`
- **良好的页面**：`app/articles/page.tsx`
- **良好的 Hook**：`lib/store.ts`

---

## 总结

- 遵循 **命名规范** 和 **代码风格**
- 使用 **TypeScript** 类型注解
- 使用 **Tailwind CSS** 而不是内联样式
- 避免 **禁止模式**（any、内联函数、直接修改 state）
- 遵循 **性能优化** 最佳实践
- 确保 **可访问性**（A11y）
