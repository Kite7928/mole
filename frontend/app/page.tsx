'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Sparkles,
  TrendingUp,
  FileText,
  Settings,
  ArrowRight,
  Plus,
  Clock,
  BarChart3,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Edit3,
  Trash2,
  Eye,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { API_URL } from '@/lib/api'
import DataChart from '@/components/charts/data-chart'
import { fetchWithErrorHandling, formatErrorMessage } from '@/lib/error-handler'

interface Article {
  id: number
  title: string
  status: string
  created_at: string
  updated_at?: string
  like_count: number
  view_count: number
}

interface Stats {
  total: number
  published: number
  draft: number
}

interface Hotspot {
  rank: number
  title: string
  url?: string
  source: string
  category?: string
  heat: number
  created_at: string
}

interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'area'
  title: string
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
    borderWidth?: number
    fill?: boolean
    tension?: number
  }[]
}

export default function HomePage() {
  const router = useRouter()
  const [recentArticles, setRecentArticles] = useState<Article[]>([])
  const [stats, setStats] = useState<Stats>({ total: 0, published: 0, draft: 0 })
  const [loading, setLoading] = useState(true)
  const [showHotspots, setShowHotspots] = useState(false)
  const [hasCompletedSetup, setHasCompletedSetup] = useState(false)
  const [hotspots, setHotspots] = useState<Hotspot[]>([])
  const [hotspotsLoading, setHotspotsLoading] = useState(false)
  const [trendChart, setTrendChart] = useState<ChartData | null>(null)
  const [platformChart, setPlatformChart] = useState<ChartData | null>(null)
  const [categoryChart, setCategoryChart] = useState<ChartData | null>(null)

  useEffect(() => {
    fetchDashboardData()
    checkSetupStatus()
    fetchHotspots()
    fetchTrendData()
    fetchPlatformData()
    fetchCategoryData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/articles?limit=5&sort_field=created_at&sort_order=desc`)
      if (response.ok) {
        const data = await response.json()
        const articles = data.articles || data || []
        setRecentArticles(articles)

        setStats({
          total: articles.length,
          published: articles.filter((a: Article) => a.status === 'published').length,
          draft: articles.filter((a: Article) => a.status === 'draft').length
        })
      } else {
        console.error('获取仪表盘数据失败:', response.status)
      }
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
      setStats({ total: 0, published: 0, draft: 0 })
    } finally {
      setLoading(false)
    }
  }

  const checkSetupStatus = async () => {
    try {
      const configRes = await fetch(`${API_URL}/api/config`)
      if (configRes.ok) {
        const config = await configRes.json()
        const hasAI = !!(config.openai_api_key || config.gemini_api_key || config.deepseek_api_key)
        setHasCompletedSetup(hasAI)
      } else {
        console.error('检查配置状态失败:', configRes.status)
      }
    } catch (error) {
      console.error('检查配置状态失败:', error)
      setHasCompletedSetup(false)
    }
  }

  const fetchHotspots = async () => {
    try {
      setHotspotsLoading(true)
      const response = await fetch(`${API_URL}/api/hotspots?limit=10`)
      if (response.ok) {
        const data = await response.json()
        setHotspots(data.items || [])
      } else {
        console.error('获取热点数据失败:', response.status)
        setHotspots([])
      }
    } catch (error) {
      console.error('获取热点数据失败:', error)
      setHotspots([])
    } finally {
      setHotspotsLoading(false)
    }
  }

  const fetchTrendData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/articles/stats/trend?days=7`)
      if (response.ok) {
        const data = await response.json()
        setTrendChart(data)
      } else {
        console.error('获取趋势数据失败:', response.status)
      }
    } catch (error) {
      console.error('获取趋势数据失败:', error)
    }
  }

  const fetchPlatformData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/articles/stats/platform`)
      if (response.ok) {
        const data = await response.json()
        setPlatformChart(data)
      } else {
        console.error('获取平台数据失败:', response.status)
      }
    } catch (error) {
      console.error('获取平台数据失败:', error)
    }
  }

  const fetchCategoryData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/articles/stats/category`)
      if (response.ok) {
        const data = await response.json()
        setCategoryChart(data)
      } else {
        console.error('获取分类数据失败:', response.status)
      }
    } catch (error) {
      console.error('获取分类数据失败:', error)
    }
  }

  const formatHeat = (heat: number) => {
    if (heat >= 100000000) {
      return `${(heat / 100000000).toFixed(1)}亿`
    } else if (heat >= 10000) {
      return `${(heat / 10000).toFixed(1)}万`
    }
    return heat.toString()
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    const styles = {
      published: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      generating: 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    }
    const labels = {
      published: '已发布',
      draft: '草稿',
      generating: '生成中'
    }
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs border ${styles[status as keyof typeof styles] || styles.draft}`}>
        {labels[status as keyof typeof labels] || status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1117] text-white p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-800 rounded w-1/3"></div>
          <div className="h-4 bg-gray-800 rounded w-1/2"></div>
          <div className="grid grid-cols-3 gap-4 mt-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-800 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#0F1117] text-white p-6">
      {/* Header - 简洁的价值主张 + 快捷操作 */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">AI公众号写作助手</h1>
          <p className="text-gray-500 text-sm mt-1">
            已生成 {stats.total} 篇文章 · {new Date().toLocaleDateString('zh-CN')}
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            className="bg-blue-600 hover:bg-blue-700 text-white"
            onClick={() => router.push('/articles/create')}
          >
            <Sparkles className="w-4 h-4 mr-2" />
            AI写作
          </Button>
          <Button 
            variant="outline" 
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={() => router.push('/hotspots')}
          >
            <TrendingUp className="w-4 h-4 mr-2" />
            热点
          </Button>
          <Button 
            variant="outline" 
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={() => router.push('/articles')}
          >
            <FileText className="w-4 h-4 mr-2" />
            文章
          </Button>
        </div>
      </div>

      {/* 新手提示条（仅在未完成设置时显示） */}
      {!hasCompletedSetup && (
        <div className="mb-6 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-blue-400" />
            <span className="text-gray-300">完成AI配置，开始创作你的第一篇文章</span>
          </div>
          <Button 
            size="sm" 
            variant="ghost" 
            className="text-blue-400 hover:text-blue-300"
            onClick={() => router.push('/settings')}
          >
            去配置
            <ArrowRight className="w-3 h-3 ml-1" />
          </Button>
        </div>
      )}

      {/* 统计卡片 - 统一配色 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="bg-[#1A1D24] border-gray-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-500 text-sm">总文章</span>
              <FileText className="w-4 h-4 text-gray-600" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
            <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
              <span>累计创作</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#1A1D24] border-gray-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-500 text-sm">已发布</span>
              <CheckCircle2 className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-blue-400">{stats.published}</div>
            <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
              <span className="text-blue-400">↑</span>
              <span>本周 +2</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[#1A1D24] border-gray-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-500 text-sm">草稿箱</span>
              <Clock className="w-4 h-4 text-gray-600" />
            </div>
            <div className="text-2xl font-bold text-gray-300">{stats.draft}</div>
            <div className="flex items-center gap-1 mt-1 text-xs text-gray-500">
              <span>待完善</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 数据图表 - 趋势和平台对比 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {trendChart && (
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-3">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-blue-400" />
                <CardTitle className="text-sm font-medium text-gray-300">发布趋势</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <DataChart data={trendChart} height={200} />
            </CardContent>
          </Card>
        )}

        {platformChart && (
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-3">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-purple-400" />
                <CardTitle className="text-sm font-medium text-gray-300">跨平台数据</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <DataChart data={platformChart} height={200} />
            </CardContent>
          </Card>
        )}
      </div>

      {/* 分类统计 - 饼图 */}
      {categoryChart && (
        <Card className="bg-[#1A1D24] border-gray-800 mb-6">
          <CardHeader className="py-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-green-400" />
              <CardTitle className="text-sm font-medium text-gray-300">文章分类分布</CardTitle>
              {categoryChart.summary && (
                <span className="text-xs text-gray-500">
                  共 {categoryChart.summary.total_categories} 个分类
                </span>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <DataChart data={categoryChart} height={250} />
          </CardContent>
        </Card>
      )}

      {/* 热点快讯 - 可折叠 */}
      <Card className="bg-[#1A1D24] border-gray-800 mb-6">
        <CardHeader 
          className="py-3 cursor-pointer hover:bg-white/5 transition-colors"
          onClick={() => setShowHotspots(!showHotspots)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <CardTitle className="text-sm font-medium text-gray-300">今日热点</CardTitle>
              <span className="text-xs text-gray-600">实时追踪</span>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-xs text-blue-400 hover:text-blue-300 h-7"
                onClick={(e) => {
                  e.stopPropagation()
                  router.push('/hotspots')
                }}
              >
                查看全部
              </Button>
              {showHotspots ? (
                <ChevronUp className="w-4 h-4 text-gray-500" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-500" />
              )}
            </div>
          </div>
        </CardHeader>
        {showHotspots && (
          <CardContent className="pt-0 pb-3">
            {hotspotsLoading ? (
              <div className="text-center py-4 text-sm text-gray-500">加载中...</div>
            ) : hotspots.length > 0 ? (
              <div className="space-y-2">
                {hotspots.map((hotspot, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                    onClick={() => router.push('/hotspots')}
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <span className="text-xs text-gray-500 font-medium w-6 text-center">{hotspot.rank}</span>
                      <span className="text-sm text-gray-300 truncate group-hover:text-white transition-colors">
                        {hotspot.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className="text-gray-600">{formatHeat(hotspot.heat)}</span>
                      <span className="text-blue-400">{hotspot.source}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-sm text-gray-500">暂无热点数据</div>
            )}
          </CardContent>
        )}
      </Card>

      {/* 最近文章 - 全宽显示 */}
      <Card className="bg-[#1A1D24] border-gray-800">
        <CardHeader className="flex flex-row items-center justify-between py-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <CardTitle className="text-sm font-medium text-gray-300">最近文章</CardTitle>
          </div>
          <Button 
            size="sm" 
            className="bg-blue-600 hover:bg-blue-700 h-7 text-xs"
            onClick={() => router.push('/articles/create')}
          >
            <Plus className="w-3 h-3 mr-1" />
            新建
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {recentArticles.length > 0 ? (
            <div className="divide-y divide-gray-800">
              {recentArticles.map((article) => (
                <div
                  key={article.id}
                  className="flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors group"
                >
                  <div className="flex-1 min-w-0 mr-4">
                    <h4 className="text-sm text-gray-300 truncate group-hover:text-white transition-colors">
                      {article.title}
                    </h4>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{formatDate(article.created_at)}</span>
                      {getStatusBadge(article.status)}
                      <span>👁 {article.view_count || 0}</span>
                      <span>👍 {article.like_count || 0}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      className="h-7 w-7 p-0 text-gray-500 hover:text-white"
                      onClick={() => router.push('/articles')}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      className="h-7 w-7 p-0 text-gray-500 hover:text-white"
                      onClick={() => router.push('/articles')}
                    >
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      className="h-7 w-7 p-0 text-gray-500 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6 text-gray-600" />
              </div>
              <h3 className="text-sm font-medium text-gray-400 mb-1">还没有文章</h3>
              <p className="text-xs text-gray-600 mb-3">创建你的第一篇文章</p>
              <Button 
                size="sm"
                onClick={() => router.push('/articles/create')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-3 h-3 mr-1" />
                立即创建
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
