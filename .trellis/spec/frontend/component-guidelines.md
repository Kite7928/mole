# 组件开发指南

> 本项目的组件开发规范和最佳实践

---

## 概览

本项目使用 **React 函数组件** + **TypeScript** + **Tailwind CSS**，遵循组件化和可复用原则。

---

## 组件结构

### 标准组件结构

```tsx
'use client'  // Next.js 客户端组件指令（如需要）

import * as React from "react"
import { cn } from "@/lib/utils"

// 1. 类型定义
export interface ComponentProps {
  title: string
  description?: string
  onAction?: () => void
  className?: string
}

// 2. 组件实现
export function Component({
  title,
  description,
  onAction,
  className
}: ComponentProps) {
  // 3. 状态和副作用
  const [isOpen, setIsOpen] = React.useState(false)

  React.useEffect(() => {
    // 副作用逻辑
  }, [])

  // 4. 事件处理函数
  const handleClick = () => {
    setIsOpen(!isOpen)
    onAction?.()
  }

  // 5. 渲染
  return (
    <div className={cn("base-styles", className)}>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      <button onClick={handleClick}>操作</button>
    </div>
  )
}
```

### 使用 forwardRef 的组件

```tsx
import * as React from "react"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline' | 'ghost'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(/* 样式 */, className)}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button }
```

---

## Props 约定

### Props 类型定义

```tsx
// ✅ 正确：使用 interface 定义 Props
export interface ArticleCardProps {
  article: Article
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  className?: string
}

// ❌ 错误：使用 type（虽然可以，但 interface 更适合组件 Props）
export type ArticleCardProps = {
  article: Article
}
```

### Props 命名规范

```tsx
// ✅ 正确：清晰的命名
interface Props {
  isLoading: boolean      // 布尔值用 is/has/should 前缀
  onSubmit: () => void    // 事件处理用 on 前缀
  articleList: Article[]  // 数组用复数或 List 后缀
  className?: string      // 可选的样式类名
}

// ❌ 错误：不清晰的命名
interface Props {
  loading: boolean        // 缺少 is 前缀
  submit: () => void      // 缺少 on 前缀
  article: Article[]      // 数组应该用复数
}
```

### 默认 Props

```tsx
// ✅ 正确：使用默认参数
export function Component({
  variant = 'default',
  size = 'medium',
  isDisabled = false
}: ComponentProps) {
  // ...
}

// ❌ 错误：使用 defaultProps（已废弃）
Component.defaultProps = {
  variant: 'default'
}
```

---

## 样式模式

### 使用 Tailwind CSS

```tsx
// ✅ 正确：使用 Tailwind 类名
<div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
  <span className="text-lg font-bold text-gray-900">标题</span>
</div>

// ❌ 错误：使用内联样式
<div style={{ display: 'flex', padding: '16px' }}>
  <span style={{ fontSize: '18px', fontWeight: 'bold' }}>标题</span>
</div>
```

### 使用 cn 工具函数合并类名

```tsx
import { cn } from "@/lib/utils"

// ✅ 正确：使用 cn 合并类名
<button
  className={cn(
    "px-4 py-2 rounded-md",
    variant === 'primary' && "bg-blue-600 text-white",
    variant === 'outline' && "border border-gray-300",
    isDisabled && "opacity-50 cursor-not-allowed",
    className
  )}
>
  按钮
</button>

// ❌ 错误：手动拼接字符串
<button
  className={`px-4 py-2 ${variant === 'primary' ? 'bg-blue-600' : ''} ${className}`}
>
  按钮
</button>
```

### 条件样式

```tsx
// ✅ 正确：清晰的条件样式
<div className={cn(
  "base-class",
  isActive && "active-class",
  isDisabled && "disabled-class"
)}>
  内容
</div>

// ❌ 错误：复杂的三元表达式
<div className={isActive ? isDisabled ? "class1" : "class2" : "class3"}>
  内容
</div>
```

---

## 组件组合

### 组合模式

```tsx
// ✅ 正确：使用组合模式
export function Card({ children, className }: CardProps) {
  return <div className={cn("card", className)}>{children}</div>
}

export function CardHeader({ children }: CardHeaderProps) {
  return <div className="card-header">{children}</div>
}

export function CardContent({ children }: CardContentProps) {
  return <div className="card-content">{children}</div>
}

// 使用
<Card>
  <CardHeader>标题</CardHeader>
  <CardContent>内容</CardContent>
</Card>
```

### Children Props

```tsx
// ✅ 正确：使用 React.ReactNode
interface Props {
  children: React.ReactNode
}

// ❌ 错误：使用 JSX.Element（过于严格）
interface Props {
  children: JSX.Element
}
```

---

## 可访问性（A11y）

### 语义化 HTML

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

### ARIA 属性

```tsx
// ✅ 正确：添加 ARIA 属性
<button
  aria-label="关闭对话框"
  aria-pressed={isPressed}
  onClick={handleClose}
>
  <X size={20} />
</button>

// ❌ 错误：缺少 ARIA 属性
<button onClick={handleClose}>
  <X size={20} />
</button>
```

### 键盘导航

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

## 常见错误

### 1. 忘记使用 'use client' 指令

```tsx
// ❌ 错误：在 Next.js 13+ 中使用客户端功能但没有声明
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

### 2. 直接修改 Props

```tsx
// ❌ 错误：直接修改 props
function Component({ data }: Props) {
  data.value = 'new'  // 错误！
  return <div>{data.value}</div>
}

// ✅ 正确：使用状态
function Component({ data }: Props) {
  const [value, setValue] = useState(data.value)
  return <div>{value}</div>
}
```

### 3. 在渲染中创建函数

```tsx
// ❌ 错误：每次渲染都创建新函数
function Component() {
  return (
    <button onClick={() => console.log('click')}>
      点击
    </button>
  )
}

// ✅ 正确：使用 useCallback 或提取到外部
function Component() {
  const handleClick = useCallback(() => {
    console.log('click')
  }, [])

  return <button onClick={handleClick}>点击</button>
}
```

---

## 参考示例

- **按钮组件**：`components/ui/button.tsx`
- **卡片组件**：`components/ui/card.tsx`
- **侧边栏组件**：`components/layout/sidebar.tsx`
- **数据图表组件**：`components/charts/data-chart.tsx`

---

## 总结

- 使用 **函数组件** + **TypeScript**
- 使用 **Tailwind CSS** 而不是内联样式
- 使用 **cn 工具函数** 合并类名
- 遵循 **可访问性** 标准
- 使用 **组合模式** 构建复杂组件
