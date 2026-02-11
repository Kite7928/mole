# Hooks 使用指南

> 本项目的 React Hooks 使用规范和最佳实践

---

## 概览

本项目使用 **React Hooks** 管理组件状态和副作用，遵循 Hooks 规则和最佳实践。

---

## 内置 Hooks 使用

### useState

```tsx
// ✅ 正确：使用 useState 管理本地状态
function Component() {
  const [count, setCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [articles, setArticles] = useState<Article[]>([])

  return <div>{count}</div>
}

// ❌ 错误：在条件语句中使用 Hook
function Component({ shouldShow }) {
  if (shouldShow) {
    const [count, setCount] = useState(0)  // 错误！
  }
}
```

### useEffect

```tsx
// ✅ 正确：使用 useEffect 处理副作用
function Component() {
  const [data, setData] = useState([])

  useEffect(() => {
    // 数据获取
    fetchData().then(setData)
  }, [])  // 空依赖数组，只在挂载时执行

  useEffect(() => {
    // 订阅
    const subscription = subscribe()
    return () => subscription.unsubscribe()  // 清理函数
  }, [])

  return <div>{data.length}</div>
}

// ❌ 错误：缺少依赖项
function Component({ userId }) {
  useEffect(() => {
    fetchUser(userId)  // 使用了 userId 但没有在依赖数组中声明
  }, [])
}
```

### useCallback

```tsx
// ✅ 正确：使用 useCallback 缓存函数
function Component() {
  const [count, setCount] = useState(0)

  const handleClick = useCallback(() => {
    setCount(c => c + 1)
  }, [])  // 不依赖外部变量

  return <button onClick={handleClick}>点击</button>
}

// ❌ 错误：不必要的 useCallback
function Component() {
  const handleClick = useCallback(() => {
    console.log('click')
  }, [])

  return <div onClick={handleClick}>点击</div>  // 不会传递给子组件，不需要 useCallback
}
```

### useMemo

```tsx
// ✅ 正确：使用 useMemo 缓存计算结果
function Component({ items }) {
  const expensiveValue = useMemo(() => {
    return items.reduce((sum, item) => sum + item.value, 0)
  }, [items])

  return <div>{expensiveValue}</div>
}

// ❌ 错误：过度使用 useMemo
function Component({ name }) {
  const greeting = useMemo(() => `Hello, ${name}`, [name])  // 不需要 useMemo
  return <div>{greeting}</div>
}
```

---

## 自定义 Hooks

### 命名规范

```tsx
// ✅ 正确：以 use 开头
function useArticles() { ... }
function useLocalStorage() { ... }
function useDebounce() { ... }

// ❌ 错误：不以 use 开头
function getArticles() { ... }
function articles() { ... }
```

### 自定义 Hook 模式

```tsx
// ✅ 正确：自定义 Hook 封装逻辑
function useArticles() {
  const [articles, setArticles] = useState<Article[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    setIsLoading(true)
    fetchArticles()
      .then(setArticles)
      .catch(setError)
      .finally(() => setIsLoading(false))
  }, [])

  return { articles, isLoading, error }
}

// 使用
function Component() {
  const { articles, isLoading, error } = useArticles()

  if (isLoading) return <div>加载中...</div>
  if (error) return <div>错误: {error.message}</div>

  return <div>{articles.map(a => <div key={a.id}>{a.title}</div>)}</div>
}
```

---

## 数据获取模式

### 基础数据获取

```tsx
// ✅ 正确：使用 useEffect 获取数据
function useArticle(id: number) {
  const [article, setArticle] = useState<Article | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    setIsLoading(true)
    fetchArticle(id)
      .then(data => {
        if (!cancelled) {
          setArticle(data)
          setError(null)
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false)
        }
      })

    return () => {
      cancelled = true  // 清理函数，防止内存泄漏
    }
  }, [id])

  return { article, isLoading, error }
}
```

### 带重试的数据获取

```tsx
function useArticleWithRetry(id: number) {
  const [article, setArticle] = useState<Article | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(() => {
    setIsLoading(true)
    fetchArticle(id)
      .then(setArticle)
      .catch(setError)
      .finally(() => setIsLoading(false))
  }, [id])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { article, isLoading, error, refetch }
}
```

---

## 常用自定义 Hooks

### useLocalStorage

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }, [key, storedValue])

  return [storedValue, setValue] as const
}
```

### useDebounce

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

// 使用
function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('')
  const debouncedSearchTerm = useDebounce(searchTerm, 500)

  useEffect(() => {
    if (debouncedSearchTerm) {
      // 执行搜索
      search(debouncedSearchTerm)
    }
  }, [debouncedSearchTerm])

  return <input value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
}
```

---

## 常见错误

### 1. 在循环或条件中使用 Hooks

```tsx
// ❌ 错误：在条件中使用 Hook
function Component({ shouldShow }) {
  if (shouldShow) {
    const [count, setCount] = useState(0)
  }
}

// ✅ 正确：始终调用 Hook
function Component({ shouldShow }) {
  const [count, setCount] = useState(0)

  if (!shouldShow) return null

  return <div>{count}</div>
}
```

### 2. 忘记清理副作用

```tsx
// ❌ 错误：没有清理订阅
function Component() {
  useEffect(() => {
    const subscription = subscribe()
    // 没有清理！
  }, [])
}

// ✅ 正确：返回清理函数
function Component() {
  useEffect(() => {
    const subscription = subscribe()
    return () => subscription.unsubscribe()
  }, [])
}
```

### 3. 依赖数组不完整

```tsx
// ❌ 错误：缺少依赖项
function Component({ userId }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetchUser(userId).then(setUser)
  }, [])  // 缺少 userId
}

// ✅ 正确：包含所有依赖项
function Component({ userId }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    fetchUser(userId).then(setUser)
  }, [userId])
}
```

---

## 参考示例

- **数据获取 Hook**：`app/articles/page.tsx`
- **本地存储 Hook**：`lib/store.ts`
- **主题 Hook**：`lib/theme-store.ts`

---

## 总结

- 遵循 **Hooks 规则**（顶层调用、不在条件中使用）
- 自定义 Hook 以 **use** 开头
- 使用 **useCallback** 和 **useMemo** 优化性能
- **清理副作用** 防止内存泄漏
- **完整的依赖数组** 避免 bug
