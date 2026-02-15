/**
 * 全文搜索组件
 * 支持自动补全、热门关键词、高亮结果
 */

'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Search,
  X,
  Loader2,
  TrendingUp,
  Clock,
  FileText,
  Tag
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { API_URL } from '@/lib/api'

interface SearchResult {
  id: number
  title: string
  summary?: string
  highlight?: string
  tags: string[]
  view_count: number
  like_count: number
  created_at: string
  search_rank: number
}

interface SearchBoxProps {
  onResultSelect?: (result: SearchResult) => void
  placeholder?: string
  className?: string
}

export default function SearchBox({
  onResultSelect,
  placeholder = "搜索文章标题、内容、标签...",
  className = ""
}: SearchBoxProps) {
  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [popularKeywords, setPopularKeywords] = useState<Array<{keyword: string; count: number}>>([])
  const [searchHistory, setSearchHistory] = useState<string[]>([])
  const [results, setResults] = useState<SearchResult[]>([])
  const [totalResults, setTotalResults] = useState(0)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const debounceTimer = useRef<NodeJS.Timeout | null>(null)

  // 加载热门关键词
  useEffect(() => {
    loadPopularKeywords()
    loadSearchHistory()
  }, [])

  // 点击外部关闭下拉框
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }
    
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // 加载热门关键词
  const loadPopularKeywords = async () => {
    try {
      const response = await fetch(`${API_URL}/api/search/popular-keywords?limit=10`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setPopularKeywords(data.keywords)
        }
      }
    } catch (error) {
      console.error('加载热门关键词失败:', error)
    }
  }

  // 加载搜索历史
  const loadSearchHistory = () => {
    const history = localStorage.getItem('search_history')
    if (history) {
      setSearchHistory(JSON.parse(history))
    }
  }

  // 保存搜索历史
  const saveSearchHistory = (keyword: string) => {
    const newHistory = [keyword, ...searchHistory.filter(h => h !== keyword)].slice(0, 10)
    setSearchHistory(newHistory)
    localStorage.setItem('search_history', JSON.stringify(newHistory))
  }

  // 获取搜索建议
  const fetchSuggestions = useCallback(async (input: string) => {
    if (input.length < 2) {
      setSuggestions([])
      return
    }
    
    try {
      const response = await fetch(
        `${API_URL}/api/search/suggestions?q=${encodeURIComponent(input)}&limit=5`
      )
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setSuggestions(data.suggestions)
        }
      }
    } catch (error) {
      console.error('获取建议失败:', error)
    }
  }, [])

  // 执行搜索
  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return
    
    setIsSearching(true)
    saveSearchHistory(searchQuery)
    
    try {
      const response = await fetch(
        `${API_URL}/api/search?q=${encodeURIComponent(searchQuery)}&limit=20`
      )
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setResults(data.articles)
          setTotalResults(data.total)
        }
      }
    } catch (error) {
      console.error('搜索失败:', error)
    } finally {
      setIsSearching(false)
    }
  }

  // 输入处理
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    setShowDropdown(true)
    
    // 防抖获取建议
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }
    
    debounceTimer.current = setTimeout(() => {
      fetchSuggestions(value)
    }, 300)
  }

  // 选择建议
  const handleSelectSuggestion = (suggestion: string) => {
    setQuery(suggestion)
    setShowDropdown(false)
    performSearch(suggestion)
  }

  // 清除搜索
  const handleClear = () => {
    setQuery('')
    setResults([])
    setSuggestions([])
    inputRef.current?.focus()
  }

  // 高亮匹配文本
  const highlightText = (text: string, query: string) => {
    if (!text || !query) return text
    
    const regex = new RegExp(`(${query.split(/\s+/).join('|')})`, 'gi')
    return text.replace(regex, '<mark class="bg-yellow-200 text-yellow-900 px-0.5 rounded">$1</mark>')
  }

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* 搜索输入框 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <Input
          ref={inputRef}
          value={query}
          onChange={handleInputChange}
          onFocus={() => setShowDropdown(true)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              setShowDropdown(false)
              performSearch(query)
            }
          }}
          placeholder={placeholder}
          className="pl-10 pr-10 h-12 bg-white border-gray-200 focus:border-blue-500 focus:ring-blue-500"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* 下拉面板 */}
      {showDropdown && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
          {/* 搜索建议 */}
          {suggestions.length > 0 && (
            <div className="p-3 border-b border-gray-100">
              <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                <Search className="w-3 h-3" />
                搜索建议
              </div>
              <div className="space-y-1">
                {suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectSuggestion(suggestion)}
                    className="w-full text-left px-3 py-2 rounded hover:bg-gray-100 text-sm text-gray-700"
                  >
                    <span dangerouslySetInnerHTML={{
                      __html: highlightText(suggestion, query)
                    }} />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 搜索历史 */}
          {searchHistory.length > 0 && !query && (
            <div className="p-3 border-b border-gray-100">
              <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                搜索历史
              </div>
              <div className="flex flex-wrap gap-2">
                {searchHistory.map((history, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectSuggestion(history)}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors"
                  >
                    {history}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 热门关键词 */}
          {!query && popularKeywords.length > 0 && (
            <div className="p-3">
              <div className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                热门关键词
              </div>
              <div className="flex flex-wrap gap-2">
                {popularKeywords.map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectSuggestion(item.keyword)}
                    className="px-3 py-1 bg-blue-50 hover:bg-blue-100 rounded-full text-sm text-blue-700 transition-colors"
                  >
                    {item.keyword}
                    <span className="ml-1 text-xs text-blue-400">{item.count}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 搜索结果 */}
      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50 max-h-[32rem] overflow-y-auto">
          <div className="p-3 border-b border-gray-100 flex items-center justify-between">
            <span className="text-sm text-gray-600">
              找到 <span className="font-medium text-gray-900">{totalResults}</span> 条结果
            </span>
            <button
              onClick={() => setResults([])}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              关闭
            </button>
          </div>
          
          <div className="divide-y divide-gray-100">
            {results.map((result) => (
              <button
                key={result.id}
                onClick={() => {
                  onResultSelect?.(result)
                  setResults([])
                }}
                className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <h4 
                  className="font-medium text-gray-900 mb-1"
                  dangerouslySetInnerHTML={{
                    __html: highlightText(result.title, query)
                  }}
                />
                {result.highlight && (
                  <p 
                    className="text-sm text-gray-500 line-clamp-2 mb-2"
                    dangerouslySetInnerHTML={{
                      __html: highlightText(result.highlight, query)
                    }}
                  />
                )}
                <div className="flex items-center gap-3 text-xs text-gray-400">
                  <span className="flex items-center gap-1">
                    <FileText className="w-3 h-3" />
                    {result.view_count} 阅读
                  </span>
                  <span>•</span>
                  <span>{new Date(result.created_at).toLocaleDateString('zh-CN')}</span>
                  {result.tags.length > 0 && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Tag className="w-3 h-3" />
                        {result.tags.slice(0, 3).join(', ')}
                      </span>
                    </>
                  )}
                </div>
              </button>
            ))}
          </div>
          
          {totalResults > results.length && (
            <div className="p-3 border-t border-gray-100 text-center">
              <button
                onClick={() => performSearch(query)}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                查看全部结果
              </button>
            </div>
          )}
        </div>
      )}

      {/* 搜索中状态 */}
      {isSearching && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 z-50 p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
          <p className="text-sm text-gray-500">搜索中...</p>
        </div>
      )}
    </div>
  )
}
