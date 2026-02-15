'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Calendar,
  Clock,
  FileText,
  Eye,
  ThumbsUp,
  Target,
  Award,
  Download,
  RefreshCw,
  ChevronDown,
  Zap,
  Flame,
  BarChart2,
  PieChart,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts'

// 数据类型定义
interface DashboardOverview {
  total_articles: number
  total_views: number
  total_likes: number
  avg_quality_score: number
  published_count: number
  draft_count: number
  views_growth: number
  likes_growth: number
  top_performing_article: {
    id: number
    title: string
    views: number
    likes: number
    quality_score: number
  } | null
  recent_7days_stats: {
    daily: Array<{
      date: string
      articles: number
      views: number
      likes: number
    }>
    total_views: number
    total_likes: number
  }
}

interface TrendData {
  date: string
  views: number
  likes: number
  articles: number
}

interface BestPublishTime {
  hourly_stats: Array<{
    hour: number
    article_count: number
    avg_views: number
    avg_likes: number
    engagement_rate: number
  }>
  weekday_stats: Array<{
    weekday: number
    weekday_name: string
    article_count: number
    avg_views: number
    avg_likes: number
    engagement_rate: number
  }>
  recommendations: {
    best_hour: number
    best_weekday: string
    best_hour_views: number
    best_weekday_views: number
  }
}

interface TopicPerformance {
  topic: string
  article_count: number
  total_views: number
  total_likes: number
  avg_views: number
  avg_quality: number
  trend: string
}

const COLORS = ['#8b5cf6', '#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function AnalyticsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview')
  const [timeRange, setTimeRange] = useState('week')
  const [loading, setLoading] = useState(true)
  
  // 数据状态
  const [overview, setOverview] = useState<DashboardOverview | null>(null)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [bestTime, setBestTime] = useState<BestPublishTime | null>(null)
  const [topics, setTopics] = useState<TopicPerformance[]>([])
  const [contentAnalysis, setContentAnalysis] = useState<any>(null)

  useEffect(() => {
    fetchAllData()
  }, [timeRange])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      await Promise.all([
        fetchOverview(),
        fetchTrends(),
        fetchBestTime(),
        fetchTopics(),
        fetchContentAnalysis()
      ])
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchOverview = async () => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/overview`)
      if (response.ok) {
        const data = await response.json()
        setOverview(data)
      }
    } catch (error) {
      console.error('获取概览数据失败:', error)
    }
  }

  const fetchTrends = async () => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/trends?period=${timeRange}`)
      if (response.ok) {
        const data = await response.json()
        setTrends(data)
      }
    } catch (error) {
      console.error('获取趋势数据失败:', error)
    }
  }

  const fetchBestTime = async () => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/best-publish-time`)
      if (response.ok) {
        const data = await response.json()
        setBestTime(data)
      }
    } catch (error) {
      console.error('获取最佳发布时间失败:', error)
    }
  }

  const fetchTopics = async () => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/topic-performance?limit=10`)
      if (response.ok) {
        const data = await response.json()
        setTopics(data)
      }
    } catch (error) {
      console.error('获取话题表现失败:', error)
    }
  }

  const fetchContentAnalysis = async () => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/content-type-analysis`)
      if (response.ok) {
        const data = await response.json()
        setContentAnalysis(data)
      }
    } catch (error) {
      console.error('获取内容分析失败:', error)
    }
  }

  const handleExport = async (format: string) => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/export?format=${format}`)
      if (response.ok) {
        const data = await response.json()
        // 创建下载
        const blob = new Blob([format === 'csv' ? data.data : JSON.stringify(data.data, null, 2)], {
          type: format === 'csv' ? 'text/csv' : 'application/json'
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.filename || `analytics_export_${new Date().toISOString().split('T')[0]}.${format}`
        a.click()
      }
    } catch (error) {
      console.error('导出失败:', error)
      alert('导出失败')
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return (num / 10000).toFixed(1) + '万'
    }
    return num.toLocaleString()
  }

  const getGrowthIcon = (value: number) => {
    if (value > 0) return <ArrowUpRight className="w-4 h-4 text-emerald-500" />
    if (value < 0) return <ArrowDownRight className="w-4 h-4 text-red-500" />
    return <Minus className="w-4 h-4 text-slate-400" />
  }

  const getGrowthColor = (value: number) => {
    if (value > 0) return 'text-emerald-600'
    if (value < 0) return 'text-red-600'
    return 'text-slate-500'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 animate-pulse" />
          <p className="text-slate-400 text-sm">加载数据中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">数据洞察中心</h1>
                <p className="text-sm text-slate-500">深度分析内容表现，优化创作策略</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* 时间范围选择 */}
              <div className="flex bg-slate-100 rounded-xl p-1">
                {[
                  { id: 'day', label: '近30天' },
                  { id: 'week', label: '近12周' },
                  { id: 'month', label: '近12月' }
                ].map((range) => (
                  <button
                    key={range.id}
                    onClick={() => setTimeRange(range.id)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      timeRange === range.id
                        ? 'bg-white text-violet-600 shadow-sm'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {range.label}
                  </button>
                ))}
              </div>
              
              {/* 导出按钮 */}
              <div className="relative group">
                <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors">
                  <Download className="w-4 h-4" />
                  导出
                  <ChevronDown className="w-4 h-4" />
                </button>
                <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-xl shadow-lg border border-slate-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <button
                    onClick={() => handleExport('json')}
                    className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 first:rounded-t-xl"
                  >
                    导出 JSON
                  </button>
                  <button
                    onClick={() => handleExport('csv')}
                    className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 last:rounded-b-xl"
                  >
                    导出 CSV
                  </button>
                </div>
              </div>
              
              <button
                onClick={fetchAllData}
                className="p-2 rounded-xl bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Tab导航 */}
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 border-b border-slate-200">
            {[
              { id: 'overview', label: '数据概览', icon: Activity },
              { id: 'trends', label: '趋势分析', icon: TrendingUp },
              { id: 'timing', label: '发布时机', icon: Clock },
              { id: 'topics', label: '话题表现', icon: Flame },
              { id: 'content', label: '内容分析', icon: FileText }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-violet-500 text-violet-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* 数据概览 Tab */}
        {activeTab === 'overview' && overview && (
          <div className="space-y-6">
            {/* 核心指标卡片 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-2xl p-5 border border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <FileText className="w-4 h-4" />
                    总文章数
                  </div>
                  {getGrowthIcon(overview.views_growth)}
                </div>
                <p className="text-3xl font-bold text-slate-900">{overview.total_articles}</p>
                <div className="flex items-center gap-2 mt-2 text-xs">
                  <span className="px-2 py-1 rounded-full bg-emerald-50 text-emerald-600">
                    {overview.published_count} 已发布
                  </span>
                  <span className="px-2 py-1 rounded-full bg-amber-50 text-amber-600">
                    {overview.draft_count} 草稿
                  </span>
                </div>
              </div>
              
              <div className="bg-white rounded-2xl p-5 border border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <Eye className="w-4 h-4" />
                    总阅读量
                  </div>
                  {getGrowthIcon(overview.views_growth)}
                </div>
                <p className="text-3xl font-bold text-slate-900">{formatNumber(overview.total_views)}</p>
                <p className={`text-xs mt-2 flex items-center gap-1 ${getGrowthColor(overview.views_growth)}`}>
                  {getGrowthIcon(overview.views_growth)}
                  较上周 {overview.views_growth > 0 ? '+' : ''}{overview.views_growth}%
                </p>
              </div>
              
              <div className="bg-white rounded-2xl p-5 border border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <ThumbsUp className="w-4 h-4" />
                    总点赞数
                  </div>
                  {getGrowthIcon(overview.likes_growth)}
                </div>
                <p className="text-3xl font-bold text-slate-900">{formatNumber(overview.total_likes)}</p>
                <p className={`text-xs mt-2 flex items-center gap-1 ${getGrowthColor(overview.likes_growth)}`}>
                  {getGrowthIcon(overview.likes_growth)}
                  较上周 {overview.likes_growth > 0 ? '+' : ''}{overview.likes_growth}%
                </p>
              </div>
              
              <div className="bg-white rounded-2xl p-5 border border-slate-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 text-slate-500 text-sm">
                    <Award className="w-4 h-4" />
                    平均质量分
                  </div>
                  <Target className="w-4 h-4 text-violet-500" />
                </div>
                <p className="text-3xl font-bold text-slate-900">{overview.avg_quality_score}</p>
                <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"
                    style={{ width: `${overview.avg_quality_score}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 最近7天趋势 + 最佳文章 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* 趋势图表 */}
              <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="font-semibold text-slate-900">近7天数据趋势</h3>
                    <p className="text-sm text-slate-500">阅读量和点赞数变化</p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-violet-500" />
                      <span className="text-slate-600">阅读量</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-pink-500" />
                      <span className="text-slate-600">点赞数</span>
                    </div>
                  </div>
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={overview.recent_7days_stats.daily}>
                      <defs>
                        <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorLikes" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#ec4899" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                      <YAxis stroke="#94a3b8" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e2e8f0',
                          borderRadius: '12px',
                          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="views"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorViews)"
                      />
                      <Area
                        type="monotone"
                        dataKey="likes"
                        stroke="#ec4899"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorLikes)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* 最佳表现文章 */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200">
                <div className="flex items-center gap-2 mb-6">
                  <Zap className="w-5 h-5 text-amber-500" />
                  <h3 className="font-semibold text-slate-900">最佳表现文章</h3>
                </div>
                
                {overview.top_performing_article ? (
                  <div className="space-y-4">
                    <div
                      className="p-4 rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 border border-violet-100 cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => router.push(`/articles/create?editId=${overview.top_performing_article!.id}`)}
                    >
                      <h4 className="font-medium text-slate-900 line-clamp-2 mb-3">
                        {overview.top_performing_article.title}
                      </h4>
                      <div className="grid grid-cols-3 gap-3 text-center">
                        <div>
                          <p className="text-lg font-bold text-violet-600">
                            {formatNumber(overview.top_performing_article.views)}
                          </p>
                          <p className="text-xs text-slate-500">阅读</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-pink-600">
                            {formatNumber(overview.top_performing_article.likes)}
                          </p>
                          <p className="text-xs text-slate-500">点赞</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-emerald-600">
                            {overview.top_performing_article.quality_score}
                          </p>
                          <p className="text-xs text-slate-500">质量分</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4 rounded-xl bg-slate-50">
                      <p className="text-sm text-slate-600 mb-2">💡 成功要素分析</p>
                      <ul className="text-xs text-slate-500 space-y-1">
                        <li>• 标题吸引力强，点击率高</li>
                        <li>• 内容质量优秀，读者留存好</li>
                        <li>• 话题热度把握准确</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-slate-400">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>暂无数据</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 趋势分析 Tab */}
        {activeTab === 'trends' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="font-semibold text-slate-900">阅读趋势分析</h3>
                  <p className="text-sm text-slate-500">不同时间周期的阅读量变化</p>
                </div>
              </div>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="views"
                      name="阅读量"
                      stroke="#8b5cf6"
                      strokeWidth={3}
                      dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#8b5cf6', strokeWidth: 2 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="likes"
                      name="点赞数"
                      stroke="#ec4899"
                      strokeWidth={3}
                      dot={{ fill: '#ec4899', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#ec4899', strokeWidth: 2 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 文章发布频率 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-6">文章发布频率</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px'
                      }}
                    />
                    <Bar
                      dataKey="articles"
                      name="发布文章数"
                      fill="#3b82f6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* 发布时机 Tab */}
        {activeTab === 'timing' && bestTime && (
          <div className="space-y-6">
            {/* 推荐结论 */}
            <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <Clock className="w-6 h-6" />
                <h3 className="text-lg font-semibold">最佳发布时机建议</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/10 rounded-xl p-4">
                  <p className="text-white/80 text-sm mb-1">最佳发布时段</p>
                  <p className="text-2xl font-bold">{bestTime.recommendations.best_hour}:00</p>
                  <p className="text-white/60 text-sm mt-1">
                    平均阅读量 {formatNumber(bestTime.recommendations.best_hour_views)}
                  </p>
                </div>
                <div className="bg-white/10 rounded-xl p-4">
                  <p className="text-white/80 text-sm mb-1">最佳发布星期</p>
                  <p className="text-2xl font-bold">{bestTime.recommendations.best_weekday}</p>
                  <p className="text-white/60 text-sm mt-1">
                    平均阅读量 {formatNumber(bestTime.recommendations.best_weekday_views)}
                  </p>
                </div>
              </div>
            </div>

            {/* 24小时分布 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-6">24小时阅读分布</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={bestTime.hourly_stats}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis
                      dataKey="hour"
                      stroke="#94a3b8"
                      fontSize={12}
                      tickFormatter={(value) => `${value}时`}
                    />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px'
                      }}
                      formatter={(value: number) => [Math.round(value), '']}
                      labelFormatter={(label) => `${label}:00`}
                    />
                    <Bar
                      dataKey="avg_views"
                      name="平均阅读量"
                      fill="#8b5cf6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 星期分布 */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h3 className="font-semibold text-slate-900 mb-6">星期阅读分布</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={bestTime.weekday_stats}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="weekday_name" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px'
                      }}
                    />
                    <Bar
                      dataKey="avg_views"
                      name="平均阅读量"
                      fill="#10b981"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* 话题表现 Tab */}
        {activeTab === 'topics' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h3 className="font-semibold text-slate-900">热门话题表现排行</h3>
                <p className="text-sm text-slate-500">基于标签和话题的阅读量分析</p>
              </div>
              <div className="divide-y divide-slate-100">
                {topics.length > 0 ? (
                  topics.map((topic, index) => (
                    <div
                      key={topic.topic}
                      className="px-6 py-4 flex items-center gap-4 hover:bg-slate-50 transition-colors"
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold ${
                        index < 3
                          ? 'bg-gradient-to-br from-violet-500 to-purple-600 text-white'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-slate-900">{topic.topic}</h4>
                        <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                          <span>{topic.article_count} 篇文章</span>
                          <span>平均质量分 {topic.avg_quality}</span>
                          {topic.trend === 'up' && (
                            <span className="text-emerald-600 flex items-center gap-1">
                              <TrendingUp className="w-3 h-3" />
                              热度上升
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-violet-600">
                          {formatNumber(topic.avg_views)}
                        </p>
                        <p className="text-xs text-slate-400">平均阅读</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="px-6 py-12 text-center text-slate-400">
                    <Flame className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>暂无话题数据</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 内容分析 Tab */}
        {activeTab === 'content' && contentAnalysis && (
          <div className="space-y-6">
            {/* 质量分析 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl p-6 border border-slate-200">
                <h3 className="font-semibold text-slate-900 mb-6">文章质量分布</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RePieChart>
                      <Pie
                        data={Object.entries(contentAnalysis.by_quality).map(([key, value]: [string, any]) => ({
                          name: key,
                          value: value.count
                        }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {Object.entries(contentAnalysis.by_quality).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </RePieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 border border-slate-200">
                <h3 className="font-semibold text-slate-900 mb-6">文章长度分布</h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RePieChart>
                      <Pie
                        data={Object.entries(contentAnalysis.by_length).map(([key, value]: [string, any]) => ({
                          name: key,
                          value: value.count
                        }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {Object.entries(contentAnalysis.by_length).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </RePieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* 优化建议 */}
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 border border-amber-200">
              <div className="flex items-center gap-3 mb-4">
                <Award className="w-6 h-6 text-amber-600" />
                <h3 className="font-semibold text-amber-900">内容优化建议</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white/60 rounded-xl p-4">
                  <p className="text-sm text-amber-800 font-medium mb-2">最佳质量区间</p>
                  <p className="text-2xl font-bold text-amber-600">
                    {contentAnalysis.recommendations.optimal_quality_range}
                  </p>
                </div>
                <div className="bg-white/60 rounded-xl p-4">
                  <p className="text-sm text-amber-800 font-medium mb-2">最佳长度区间</p>
                  <p className="text-2xl font-bold text-amber-600">
                    {contentAnalysis.recommendations.optimal_length_range}
                  </p>
                </div>
                <div className="bg-white/60 rounded-xl p-4">
                  <p className="text-sm text-amber-800 font-medium mb-2">综合建议</p>
                  <p className="text-sm text-amber-700">
                    {contentAnalysis.recommendations.suggestion}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
