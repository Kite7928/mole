# 状态管理指南

> 本项目的状态管理策略和最佳实践

---

## 概览

本项目使用 **Zustand** 进行全局状态管理，使用 **React Hooks** 管理本地状态。

---

## 状态分类

### 1. 本地状态（Local State）

**定义**：仅在单个组件内使用的状态

**使用场景**：
- 表单输入值
- UI 交互状态（展开/折叠、选中等）
- 临时数据

**实现方式**：使用 `useState`

```tsx
function Component() {
  const [isOpen, setIsOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')

  return (
    <div>
      <input value={inputValue} onChange={e => setInputValue(e.target.value)} />
      <button onClick={() => setIsOpen(!isOpen)}>切换</button>
    </div>
  )
}
```

### 2. 全局状态（Global State）

**定义**：多个组件共享的状态

**使用场景**：
- 用户信息
- 主题设置
- 应用配置

**实现方式**：使用 Zustand

```tsx
// lib/store.ts
import { create } from 'zustand'

interface AppState {
  user: User | null
  setUser: (user: User | null) => void
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}))

// 使用
function Component() {
  const user = useAppStore(state => state.user)
  const setUser = useAppStore(state => state.setUser)

  return <div>{user?.name}</div>
}
```

### 3. 服务器状态（Server State）

**定义**：从服务器获取的数据

**使用场景**：
- API 数据
- 数据库记录
- 远程资源

**实现方式**：使用自定义 Hook + useEffect

```tsx
function useArticles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchArticles()
      .then(setArticles)
      .finally(() => setIsLoading(false))
  }, [])

  return { articles, isLoading }
}
```

### 4. URL 状态（URL State）

**定义**：存储在 URL 中的状态

**使用场景**：
- 搜索参数
- 分页信息
- 过滤条件

**实现方式**：使用 Next.js `useSearchParams`

```tsx
'use client'

import { useSearchParams, useRouter } from 'next/navigation'

function Component() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const page = searchParams.get('page') || '1'

  const setPage = (newPage: string) => {
    const params = new URLSearchParams(searchParams)
    params.set('page', newPage)
    router.push(`?${params.toString()}`)
  }

  return <div>当前页: {page}</div>
}
```

---

## 何时使用全局状态

### ✅ 应该使用全局状态

- 多个页面/组件需要访问
- 需要持久化（localStorage）
- 频繁更新且影响多个组件

```tsx
// ✅ 正确：主题设置（多个组件使用）
const useThemeStore = create((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}))
```

### ❌ 不应该使用全局状态

- 仅在单个组件使用
- 临时的 UI 状态
- 可以通过 props 传递

```tsx
// ❌ 错误：表单输入值不应该放在全局状态
const useFormStore = create((set) => ({
  inputValue: '',
  setInputValue: (value) => set({ inputValue: value }),
}))

// ✅ 正确：使用本地状态
function Form() {
  const [inputValue, setInputValue] = useState('')
  return <input value={inputValue} onChange={e => setInputValue(e.target.value)} />
}
```

---

## Zustand 使用模式

### 基础 Store

```tsx
// lib/store.ts
import { create } from 'zustand'

interface AppState {
  count: number
  increment: () => void
  decrement: () => void
}

export const useAppStore = create<AppState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}))
```

### 持久化 Store

```tsx
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'light',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'theme-storage',  // localStorage key
    }
  )
)
```

### 选择性订阅

```tsx
// ✅ 正确：只订阅需要的状态
function Component() {
  const count = useAppStore(state => state.count)  // 只订阅 count
  return <div>{count}</div>
}

// ❌ 错误：订阅整个 store
function Component() {
  const store = useAppStore()  // 任何状态变化都会重新渲染
  return <div>{store.count}</div>
}
```

---

## 状态更新模式

### 不可变更新

```tsx
// ✅ 正确：不可变更新
const useStore = create((set) => ({
  items: [],
  addItem: (item) => set((state) => ({
    items: [...state.items, item]  // 创建新数组
  })),
  updateItem: (id, updates) => set((state) => ({
    items: state.items.map(item =>
      item.id === id ? { ...item, ...updates } : item
    )
  })),
}))

// ❌ 错误：直接修改状态
const useStore = create((set) => ({
  items: [],
  addItem: (item) => set((state) => {
    state.items.push(item)  // 错误！直接修改
    return { items: state.items }
  }),
}))
```

### 批量更新

```tsx
// ✅ 正确：批量更新
const useStore = create((set) => ({
  user: null,
  isLoading: false,
  error: null,
  fetchUser: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const user = await fetchUser(id)
      set({ user, isLoading: false })
    } catch (error) {
      set({ error, isLoading: false })
    }
  },
}))
```

---

## 常见错误

### 1. 过度使用全局状态

```tsx
// ❌ 错误：所有状态都放在全局
const useStore = create((set) => ({
  modalOpen: false,
  inputValue: '',
  selectedTab: 0,
  // ... 100+ 个状态
}))

// ✅ 正确：只把真正需要共享的状态放在全局
const useStore = create((set) => ({
  user: null,
  theme: 'light',
}))

// 本地状态使用 useState
function Component() {
  const [modalOpen, setModalOpen] = useState(false)
  const [inputValue, setInputValue] = useState('')
}
```

### 2. 直接修改状态

```tsx
// ❌ 错误：直接修改
const useStore = create((set) => ({
  user: { name: 'John' },
  updateName: (name) => set((state) => {
    state.user.name = name  // 错误！
    return state
  }),
}))

// ✅ 正确：创建新对象
const useStore = create((set) => ({
  user: { name: 'John' },
  updateName: (name) => set((state) => ({
    user: { ...state.user, name }
  })),
}))
```

### 3. 忘记清理副作用

```tsx
// ❌ 错误：没有清理订阅
function Component() {
  useEffect(() => {
    const unsubscribe = useStore.subscribe(
      state => state.count,
      (count) => console.log(count)
    )
    // 没有清理！
  }, [])
}

// ✅ 正确：返回清理函数
function Component() {
  useEffect(() => {
    const unsubscribe = useStore.subscribe(
      state => state.count,
      (count) => console.log(count)
    )
    return unsubscribe
  }, [])
}
```

---

## 参考示例

- **应用状态**：`lib/store.ts`
- **主题状态**：`lib/theme-store.ts`
- **页面状态**：`app/articles/page.tsx`

---

## 总结

- **本地状态** 用 useState
- **全局状态** 用 Zustand
- **服务器状态** 用自定义 Hook
- **URL 状态** 用 useSearchParams
- 避免 **过度使用全局状态**
- 使用 **不可变更新** 模式
