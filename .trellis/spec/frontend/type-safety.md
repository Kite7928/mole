# 类型安全指南

> 本项目的 TypeScript 使用规范和类型安全实践

---

## 概览

本项目使用 **TypeScript** 进行类型检查，确保代码的类型安全和可维护性。

---

## 类型组织

### 类型定义位置

```
frontend/
├── lib/
│   └── api.ts              # API 相关类型
├── components/
│   └── ui/
│       └── button.tsx      # 组件 Props 类型（与组件同文件）
└── app/
    └── articles/
        └── page.tsx        # 页面级类型（与页面同文件）
```

### 共享类型 vs 本地类型

```tsx
// ✅ 正确：组件 Props 类型定义在组件文件中
// components/ui/button.tsx
export interface ButtonProps {
  variant?: 'default' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}

// ✅ 正确：API 响应类型定义在 lib/api.ts 中
// lib/api.ts
export interface ArticleResponse {
  id: number
  title: string
  content: string
}

// ❌ 错误：所有类型都放在一个 types.ts 文件中
// types.ts
export interface ButtonProps { ... }
export interface ArticleResponse { ... }
// ... 100+ 个类型定义
```

---

## 类型定义规范

### Interface vs Type

```tsx
// ✅ 正确：组件 Props 使用 interface
export interface ComponentProps {
  title: string
  onAction?: () => void
}

// ✅ 正确：联合类型使用 type
export type Status = 'pending' | 'success' | 'error'

// ✅ 正确：工具类型使用 type
export type Nullable<T> = T | null
```

### 类型命名

```tsx
// ✅ 正确：清晰的命名
export interface ArticleResponse {
  id: number
  title: string
}

export interface CreateArticleRequest {
  title: string
  content: string
}

export type ArticleStatus = 'draft' | 'published'

// ❌ 错误：不清晰的命名
export interface Article { ... }  // 是请求还是响应？
export type Status { ... }        // 什么的状态？
```

### 可选属性

```tsx
// ✅ 正确：使用 ? 标记可选属性
export interface ArticleProps {
  title: string
  description?: string  // 可选
  tags?: string[]       // 可选
}

// ❌ 错误：使用 | undefined
export interface ArticleProps {
  title: string
  description: string | undefined
}
```

---

## 类型推断

### 利用类型推断

```tsx
// ✅ 正确：利用类型推断
const [count, setCount] = useState(0)  // 自动推断为 number
const articles = data.articles || []   // 自动推断为 Article[]

// ❌ 错误：不必要的类型注解
const [count, setCount] = useState<number>(0)
const articles: Article[] = data.articles || []
```

### 函数返回类型

```tsx
// ✅ 正确：显式声明返回类型（公共 API）
export async function fetchArticles(): Promise<Article[]> {
  const response = await fetch('/api/articles')
  return response.json()
}

// ✅ 正确：利用推断（内部函数）
function formatDate(date: Date) {
  return date.toLocaleDateString()  // 自动推断返回 string
}
```

---

## 常用模式

### 扩展 HTML 元素属性

```tsx
// ✅ 正确：扩展原生元素属性
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline'
}

// 使用
<Button onClick={handleClick} disabled={isLoading} variant="outline" />
```

### 泛型组件

```tsx
// ✅ 正确：使用泛型
interface SelectProps<T> {
  options: T[]
  value: T
  onChange: (value: T) => void
  getLabel: (option: T) => string
}

export function Select<T>({ options, value, onChange, getLabel }: SelectProps<T>) {
  return (
    <select value={getLabel(value)} onChange={(e) => {
      const option = options.find(o => getLabel(o) === e.target.value)
      if (option) onChange(option)
    }}>
      {options.map(option => (
        <option key={getLabel(option)} value={getLabel(option)}>
          {getLabel(option)}
        </option>
      ))}
    </select>
  )
}
```

### 类型守卫

```tsx
// ✅ 正确：使用类型守卫
function isArticle(data: unknown): data is Article {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'title' in data
  )
}

// 使用
if (isArticle(data)) {
  console.log(data.title)  // TypeScript 知道 data 是 Article
}
```

---

## 禁止模式

### ❌ 不要使用 any

```tsx
// ❌ 错误：使用 any
function processData(data: any) {
  return data.value  // 没有类型检查
}

// ✅ 正确：使用 unknown 或具体类型
function processData(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return (data as { value: string }).value
  }
  throw new Error('Invalid data')
}
```

### ❌ 不要滥用类型断言

```tsx
// ❌ 错误：滥用 as
const data = response.json() as Article  // 不安全！

// ✅ 正确：使用类型守卫验证
const data = response.json()
if (isArticle(data)) {
  // 使用 data
}
```

### ❌ 不要使用 @ts-ignore

```tsx
// ❌ 错误：使用 @ts-ignore
// @ts-ignore
const value = data.unknownProperty

// ✅ 正确：修复类型问题
const value = 'unknownProperty' in data
  ? (data as any).unknownProperty
  : undefined
```

---

## API 类型定义

### 请求和响应类型

```tsx
// lib/api.ts

// 请求类型
export interface CreateArticleRequest {
  title: string
  content: string
  summary?: string
  tags?: string[]
}

// 响应类型
export interface ArticleResponse {
  id: number
  title: string
  content: string
  status: string
  created_at: string
  updated_at?: string
}

// API 函数
export async function createArticle(
  data: CreateArticleRequest
): Promise<ArticleResponse> {
  return fetchAPI('/api/articles', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
```

---

## 常见错误

### 1. 忘记处理 null/undefined

```tsx
// ❌ 错误：没有处理 undefined
function Component({ article }: { article?: Article }) {
  return <div>{article.title}</div>  // 可能报错！
}

// ✅ 正确：处理 undefined
function Component({ article }: { article?: Article }) {
  if (!article) return null
  return <div>{article.title}</div>
}
```

### 2. 类型过于宽泛

```tsx
// ❌ 错误：类型过于宽泛
interface Props {
  status: string  // 可以是任何字符串
}

// ✅ 正确：使用联合类型
interface Props {
  status: 'pending' | 'success' | 'error'
}
```

### 3. 忘记导出类型

```tsx
// ❌ 错误：没有导出类型
interface ArticleProps {
  article: Article
}

// ✅ 正确：导出类型供其他文件使用
export interface ArticleProps {
  article: Article
}
```

---

## 参考示例

- **API 类型**：`lib/api.ts`
- **组件 Props**：`components/ui/button.tsx`
- **页面类型**：`app/articles/page.tsx`

---

## 总结

- 使用 **interface** 定义组件 Props
- 使用 **type** 定义联合类型和工具类型
- **利用类型推断** 减少冗余注解
- **禁止使用 any**，使用 unknown 代替
- 使用 **类型守卫** 进行运行时验证
