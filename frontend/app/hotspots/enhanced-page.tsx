'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import {
  Flame,
  RefreshCw,
  Search,
  Filter,
  Clock,
  TrendingUp,
  Bookmark,
  Sparkles,
  Loader2,
  Grid3x3,
  List,
  Tag,
  ExternalLink,
  Wand2,
  X,
  BarChart3,
  PieChart,
  ArrowUp,
  ArrowDown,
  Minus,
  ChevronDown,
  ChevronUp,
  History,
  Download
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 热点新闻类型定义
interface HotspotItem {
  id?: number
  rank: number
  title: string
  summary?: string
  url: string
  source: string
  sourceName: string
  category?: string
  heat: number
  heat_trend?: number
  view_count?: number
  discuss_count?: number
  keywords?: string[]
  tags?: string[]
  is_processed?: boolean
  publishedAt: string
  heat_history?: Array<{ timestamp: string; heat: number }>
}

// 统计数据类型
interface HotspotStats {
  total_hotspots: number
  today_new: number
  source_distribution: Record<string, number>
  category_distribution: Record<string, number>
  heat_distribution: Record<string, number>
}

// 趋势数据类型
interface TrendData {
  hour: string
  total_hotspots: number
  avg_heat: number
  max_heat: number
}

// 筛选选项
interface FilterOptions {
  sources: string[]
  categories: string[]
  min_heat?: number
  max_heat?: number
  keyword?: string
  date_from?: string
  date_to?: string
  order_by: 'heat' | 'created_at' | 'rank'
  order_desc: boolean
}

// 来源配置
const SOURCE_CONFIG: Record<string, { name: string; color: string; icon: string }> = {
  weibo: { name: '微博热搜', color: '#E6162D', icon: '🔥' },
  zhihu: { name: '知乎热榜', color: '#0084FF', icon: '💡' },
  bilibili: { name: 'B站热门', color: '#FB7299', icon: '📺' },
  kr36: { name: '36氪', color: '#4285F4', icon: '🚀' },
  sspai: { name: '少数派', color: '#D93025', icon: '⌨️' },
  ithome: { name: 'IT之家', color: '#FF6B6B', icon: '📱' },
  huxiu: { name: '虎嗅', color: '#FF8C00', icon: '🐯' },
  tmpost: { name: '钛媒体', color: '#00D4AA', icon: '⚡' },
}

// 分类配置
const CATEGORY_CONFIG: Record<string, { name: string; color: string }> = {
  tech: { name: '科技', color: '#3B82F6' },
  social: { name: '社交', color: '#EC4899' },
  entertainment: { name: '娱乐', color: '#8B5CF6' },
  knowledge: { name: '知识', color: '#10B981' },
  news: { name: '新闻', color: '#F59E0B' },
  business: { name: '商业', color: '#6366F1' },
  life: { name: '生活', color: '#14B8A6' },
  finance: { name: '财经', color: '#F97316' },
}

export default function EnhancedHotspotsPage() {
  const router = useRouter()
  
  // 数据状态
  const [hotspots, setHotspots] = useState<HotspotItem[]>([])
  const [stats, setStats] = useState<HotspotStats | null>(null)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  
  // 筛选状态
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<FilterOptions>({
    sources: [],
    categories: [],
    order_by: 'heat',
    order_desc: true
  })
  
  // 视图状态
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedSource, setSelectedSource] = useState<string>('all')
  const [showStats, setShowStats] = useState(true)
  const [expandedHotspot, setExpandedHotspot] = useState<number | null>(null)
  
  // 搜索状态
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  
  // 大纲生成状态
  const [generatingOutline, setGeneratingOutline] = useState<number | null>(null)
  const [generatedOutlines, setGeneratedOutlines] = useState<Record<number, any[]>>({})
  
  // 分页状态
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  
  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery)
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery])
  
  // 获取热点数据
  const fetchHotspots = useCallback(async (isLoadMore = false) => {
    try {
      if (!isLoadMore) setLoading(true)
      
      const params = new URLSearchParams()
      params.append('limit', '50')
      
      if (selectedSource !== 'all') {
        params.append('sources', selectedSource)
      }
      
      const response = await fetch(`${API_URL}/api/hotspots?${params}`)
      if (!response.ok) throw new Error('获取热点失败')
      
      const data = await response.json()
      
      if (data.items) {
        const processedItems = data.items.map((item: any) => ({
          ...item,
          sourceName: SOURCE_CONFIG[item.source]?.name || item.source,
          publishedAt: item.created_at
        }))
        
        if (isLoadMore) {
          setHotspots(prev => [...prev, ...processedItems])
        } else {
          setHotspots(processedItems)
        }
        
        setHasMore(data.items.length === 50)
      }
    } catch (error) {
      console.error('获取热点失败:', error)
    } finally {
      setLoading(false)
    }
  }, [selectedSource])
  
  // 获取统计数据
  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/hotspots/stats/overview`)
      if (!response.ok) throw new Error('获取统计失败')
      
      const data = await response.json()
      if (data.success) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('获取统计失败:', error)
    }
  }, [])
  
  // 获取趋势数据
  const fetchTrends = useCallback(async () => {
    try {
      const source = selectedSource === 'all' ? 'weibo' : selectedSource
      const response = await fetch(
        `${API_URL}/api/hotspots/trends?source=${source}&hours=24`
      )
      if (!response.ok) throw new Error('获取趋势失败')
      
      const data = await response.json()
      if (data.success) {
        setTrends(data.trends)
      }
    } catch (error) {
      console.error('获取趋势失败:', error)
    }
  }, [selectedSource])
  
  // 初始加载
  useEffect(() => {
    fetchHotspots()
    fetchStats()
    fetchTrends()
  }, [fetchHotspots, fetchStats, fetchTrends])
  
  // 刷新数据
  const handleRefresh = async () => {
    setRefreshing(true)
    await Promise.all([fetchHotspots(), fetchStats(), fetchTrends()])
    setRefreshing(false)
  }
  
  // 加载更多
  const handleLoadMore = () => {
    setPage(prev => prev + 1)
    fetchHotspots(true)
  }
  
  // 获取热度趋势图标
  const getTrendIcon = (trend?: number) => {
    if (!trend || trend === 0) return <Minus className="w-4 h-4 text-gray-400" />
    if (trend > 0) return <ArrowUp className="w-4 h-4 text-red-500" />
    return <ArrowDown className="w-4 h-4 text-green-500" />
  }
  
  // 获取热度颜色
  const getHeatColor = (heat: number) => {
    if (heat >= 1000000) return 'text-red-500'
    if (heat >= 500000) return 'text-orange-500'
    if (heat >= 100000) return 'text-yellow-500'
    return 'text-blue-500'
  }
  
  // 格式化热度
  const formatHeat = (heat: number) => {
    if (heat >= 100000000) return `${(heat / 100000000).toFixed(1)}亿`
    if (heat >= 10000) return `${(heat / 10000).toFixed(1)}万`
    return heat.toString()
  }
  
  // 生成大纲
  const handleGenerateOutline = async (hotspot: HotspotItem) => {
    if (!hotspot.id) return
    
    setGeneratingOutline(hotspot.id)
    try {
      const response = await fetch(`${API_URL}/api/articles/generate-outlines`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: hotspot.title,
          source_url: hotspot.url
        })
      })
      
      const data = await response.json()
      if (data.success && data.outlines) {
        setGeneratedOutlines(prev => ({
          ...prev,
          [hotspot.id!]: data.outlines
        }))
      }
    } catch (error) {
      console.error('生成大纲失败:', error)
    } finally {
      setGeneratingOutline(null)
    }
  }
  
  // 获取热度历史
  const fetchHeatHistory = async (hotspotId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/hotspots/${hotspotId}/history`)
      if (!response.ok) throw new Error('获取历史失败')
      
      const data = await response.json()
      if (data.success && data.history) {
        setHotspots(prev => prev.map(h => 
          h.id === hotspotId 
            ? { ...h, heat_history: data.history }
            : h
        ))
      }
    } catch (error) {
      console.error('获取热度历史失败:', error)
    }
  }
  
  // 切换展开状态
  const toggleExpand = (hotspotId: number) => {
    if (expandedHotspot === hotspotId) {
      setExpandedHotspot(null)
    } else {
      setExpandedHotspot(hotspotId)
      const hotspot = hotspots.find(h => h.id === hotspotId)
      if (hotspot && !hotspot.heat_history) {
        fetchHeatHistory(hotspotId)
      }
    }
  }
  
  return (
    <div className="min-h-screen bg-[#0F1117] text-white p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Flame className="w-6 h-6 text-orange-500" />
            热点监控中心
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            实时监控全网热点，智能分析趋势
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={() => setShowStats(!showStats)}
          >
            <BarChart3 className="w-4 h-4 mr-2" />
            {showStats ? '隐藏统计' : '显示统计'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4 mr-2" />
            筛选
          </Button>
          <Button
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            刷新
          </Button>
        </div>
      </div>
      
      {/* 统计面板 */}
      {showStats && stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">总热点数</p>
                  <p className="text-2xl font-bold text-white">{stats.total_hotspots}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">今日新增</p>
                  <p className="text-2xl font-bold text-green-400">{stats.today_new}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">数据来源</p>
                  <p className="text-2xl font-bold text-purple-400">
                    {Object.keys(stats.source_distribution).length}
                  </p>
                </div>
                <PieChart className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-500 text-sm">分类覆盖</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {Object.keys(stats.category_distribution).length}
                  </p>
                </div>
                <Tag className="w-8 h-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* 筛选面板 */}
      {showFilters && (
        <Card className="bg-[#1A1D24] border-gray-800 mb-6">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* 来源筛选 */}
              <div>
                <Label className="text-gray-400 text-sm mb-2 block">数据来源</Label>
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant={selectedSource === 'all' ? 'default' : 'outline'}
                    className={selectedSource === 'all' 
                      ? 'bg-blue-600 text-white' 
                      : 'border-gray-700 text-gray-300'
                    }
                    onClick={() => setSelectedSource('all')}
                  >
                    全部
                  </Button>
                  {Object.entries(SOURCE_CONFIG).map(([key, config]) => (
                    <Button
                      key={key}
                      size="sm"
                      variant={selectedSource === key ? 'default' : 'outline'}
                      className={selectedSource === key 
                        ? 'bg-blue-600 text-white' 
                        : 'border-gray-700 text-gray-300'
                      }
                      onClick={() => setSelectedSource(key)}
                    >
                      {config.icon} {config.name}
                    </Button>
                  ))}
                </div>
              </div>
              
              {/* 搜索 */}
              <div>
                <Label className="text-gray-400 text-sm mb-2 block">关键词搜索</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="搜索热点关键词..."
                    className="pl-10 bg-gray-800 border-gray-700 text-white"
                  />
                </div>
              </div>
              
              {/* 视图切换 */}
              <div>
                <Label className="text-gray-400 text-sm mb-2 block">视图模式</Label>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant={viewMode === 'grid' ? 'default' : 'outline'}
                    className={viewMode === 'grid' 
                      ? 'bg-blue-600 text-white' 
                      : 'border-gray-700 text-gray-300'
                    }
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid3x3 className="w-4 h-4 mr-1" />
                    网格
                  </Button>
                  <Button
                    size="sm"
                    variant={viewMode === 'list' ? 'default' : 'outline'}
                    className={viewMode === 'list' 
                      ? 'bg-blue-600 text-white' 
                      : 'border-gray-700 text-gray-300'
                    }
                    onClick={() => setViewMode('list')}
                  >
                    <List className="w-4 h-4 mr-1" />
                    列表
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* 热点列表 */}
      {loading ? (
        <div className="text-center py-12">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-500">加载热点数据中...</p>
        </div>
      ) : hotspots.length === 0 ? (
        <div className="text-center py-12">
          <Flame className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">暂无热点数据</h3>
          <p className="text-sm text-gray-600 mb-4">点击刷新按钮获取最新热点</p>
          <Button onClick={handleRefresh} className="bg-blue-600 hover:bg-blue-700">
            <RefreshCw className="w-4 h-4 mr-2" />
            立即刷新
          </Button>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' 
          : 'space-y-3'
        }>
          {hotspots
            .filter(h => {
              if (!debouncedSearch) return true
              const searchLower = debouncedSearch.toLowerCase()
              return h.title.toLowerCase().includes(searchLower) ||
                h.keywords?.some(k => k.toLowerCase().includes(searchLower))
            })
            .map((hotspot) => (
            <div
              key={hotspot.id || `${hotspot.source}-${hotspot.rank}`}
              className={`bg-[#1A1D24] border border-gray-800 rounded-lg overflow-hidden hover:border-gray-700 transition-all ${
                viewMode === 'list' ? 'flex items-center p-4' : ''
              }`}
            >
              {/* 排名和热度 */}
              <div className={`${viewMode === 'list' ? 'flex items-center gap-4 mr-4' : 'p-4 border-b border-gray-800'}`}>
                <div className="flex items-center gap-2">
                  <span className={`text-lg font-bold ${
                    hotspot.rank <= 3 ? 'text-red-500' : 'text-gray-400'
                  }`}>
                    #{hotspot.rank}
                  </span>
                  {hotspot.heat_trend !== undefined && getTrendIcon(hotspot.heat_trend)}
                </div>
                
                <div className={`flex items-center gap-1 ${getHeatColor(hotspot.heat)}`}>
                  <Flame className="w-4 h-4" />
                  <span className="font-bold">{formatHeat(hotspot.heat)}</span>
                </div>
                
                {viewMode === 'list' && (
                  <span className="text-gray-500 text-sm">
                    {SOURCE_CONFIG[hotspot.source]?.icon} {hotspot.sourceName}
                  </span>
                )}
              </div>
              
              {/* 内容 */}
              <div className={`${viewMode === 'list' ? 'flex-1' : 'p-4'}`}>
                <h3 className="font-medium text-white mb-2 line-clamp-2 hover:text-blue-400 cursor-pointer"
                  onClick={() => window.open(hotspot.url, '_blank')}
                >
                  {hotspot.title}
                </h3>
                
                {viewMode === 'grid' && (
                  <>
                    <div className="flex items-center gap-2 mb-3">
                      <span 
                        className="text-xs px-2 py-1 rounded"
                        style={{ 
                          backgroundColor: SOURCE_CONFIG[hotspot.source]?.color + '20',
                          color: SOURCE_CONFIG[hotspot.source]?.color 
                        }}
                      >
                        {SOURCE_CONFIG[hotspot.source]?.icon} {hotspot.sourceName}
                      </span>
                      {hotspot.category && (
                        <span 
                          className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-400"
                        >
                          {CATEGORY_CONFIG[hotspot.category]?.name || hotspot.category}
                        </span>
                      )}
                    </div>
                    
                    {hotspot.summary && (
                      <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                        {hotspot.summary}
                      </p>
                    )}
                  </>
                )}
                
                {/* 关键词标签 */}
                {hotspot.keywords && hotspot.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {hotspot.keywords.slice(0, 3).map((kw, idx) => (
                      <span key={idx} className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              
              {/* 操作按钮 */}
              <div className={`${viewMode === 'list' ? 'flex items-center gap-2 ml-4' : 'px-4 pb-4'}`}>
                <div className={`flex gap-2 ${viewMode === 'grid' ? 'flex-col' : ''}`}>
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-gray-700 text-gray-300 hover:bg-gray-800"
                    onClick={() => window.open(hotspot.url, '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    查看
                  </Button>
                  
                  {hotspot.id && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-gray-700 text-gray-300 hover:bg-gray-800"
                      onClick={() => toggleExpand(hotspot.id!)}
                    >
                      <History className="w-4 h-4 mr-1" />
                      趋势
                    </Button>
                  )}
                  
                  <Button
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    onClick={() => handleGenerateOutline(hotspot)}
                    disabled={generatingOutline === hotspot.id}
                  >
                    {generatingOutline === hotspot.id ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Wand2 className="w-4 h-4 mr-1" />
                    )}
                    生成大纲
                  </Button>
                </div>
              </div>
              
              {/* 展开详情 */}
              {expandedHotspot === hotspot.id && hotspot.heat_history && (
                <div className="col-span-full px-4 pb-4 border-t border-gray-800 mt-4 pt-4">
                  <h4 className="text-sm font-medium text-gray-400 mb-3">热度趋势（24小时）</h4>
                  <div className="h-32 bg-gray-800 rounded-lg p-3">
                    {/* 这里可以集成图表库显示趋势 */}
                    <div className="flex items-end justify-between h-full gap-1">
                      {hotspot.heat_history.slice(-20).map((point, idx) => {
                        const maxHeat = Math.max(...hotspot.heat_history!.map(h => h.heat))
                        const height = maxHeat > 0 ? (point.heat / maxHeat) * 100 : 0
                        return (
                          <div
                            key={idx}
                            className="flex-1 bg-blue-500/50 rounded-t hover:bg-blue-500 transition-colors"
                            style={{ height: `${Math.max(height, 5)}%` }}
                            title={`${new Date(point.timestamp).toLocaleTimeString()}: ${formatHeat(point.heat)}`}
                          />
                        )
                      })}
                    </div>
                  </div>
                  
                  {/* 生成的大纲 */}
                  {generatedOutlines[hotspot.id] && (
                    <div className="mt-4 space-y-2">
                      <h4 className="text-sm font-medium text-gray-400">AI生成的大纲</h4>
                      {generatedOutlines[hotspot.id].map((outline, idx) => (
                        <div key={idx} className="bg-gray-800 rounded-lg p-3">
                          <h5 className="font-medium text-white mb-2">{outline.title}</h5>
                          <ul className="text-sm text-gray-400 space-y-1">
                            {outline.points?.map((point: string, pidx: number) => (
                              <li key={pidx}>• {point}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      {/* 加载更多 */}
      {!loading && hotspots.length > 0 && hasMore && (
        <div className="text-center mt-6">
          <Button
            variant="outline"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={handleLoadMore}
          >
            加载更多
          </Button>
        </div>
      )}
    </div>
  )
}

// 导入需要的组件
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
