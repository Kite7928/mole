'use client'

import { useState, useEffect } from 'react'
import {
  FileText,
  Plus,
  Search,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  Clock,
  TrendingUp,
  Calendar,
  Copy,
  Globe,
  Loader2,
  RefreshCw,
  LayoutGrid,
  List,
  Sparkles,
  Zap,
  Target,
  Award,
  ArrowUpRight,
  Flame,
  Send,
  FileEdit,
  MoreVertical,
  ChevronRight,
  BarChart2
} from 'lucide-react'
import Link from 'next/link'
import { API_URL, deleteArticle as deleteArticleAPI, copyArticle as copyArticleAPI } from '@/lib/api'
import MultiplatformPublishDialog from '@/components/multiplatform-publish-dialog'

export default function ArticlesPage() {
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [selectedQualityCheckStatus, setSelectedQualityCheckStatus] = useState<'all' | 'pass' | 'warning' | 'blocked' | 'unchecked'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
  const [selectedArticles, setSelectedArticles] = useState<number[]>([])
  const [batchMode, setBatchMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [articles, setArticles] = useState<any[]>([])
  const [showPublishDialog, setShowPublishDialog] = useState(false)
  const [publishingArticle, setPublishingArticle] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'table' | 'card'>('card')
  const [sortBy, setSortBy] = useState<'date' | 'read' | 'score'>('date')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery.trim())
    }, 350)

    return () => clearTimeout(timer)
  }, [searchQuery])

  useEffect(() => {
    fetchArticles(selectedQualityCheckStatus, debouncedSearchQuery)
  }, [selectedQualityCheckStatus, debouncedSearchQuery])

  const fetchArticles = async (
    qualityCheckStatus: 'all' | 'pass' | 'warning' | 'blocked' | 'unchecked' = selectedQualityCheckStatus,
    searchKeyword: string = debouncedSearchQuery
  ) => {
    try {
      setLoading(true)
      const query = new URLSearchParams()
      if (qualityCheckStatus !== 'all') {
        query.set('quality_check_status', qualityCheckStatus)
      }
      if (searchKeyword) {
        query.set('search', searchKeyword)
      }

      const queryString = query.toString()
      const response = await fetch(`${API_URL}/api/articles${queryString ? `?${queryString}` : ''}`)
      if (!response.ok) throw new Error('获取文章列表失败')
      const data = await response.json()
      
      const formattedArticles = data.map((article: any) => ({
        id: article.id,
        title: article.title,
        status: article.status,
        sourceName: article.source_topic || '原创',
        coverImage: article.cover_image_url,
        readCount: typeof article.view_count === 'number' ? article.view_count : 0,
        likeCount: typeof article.like_count === 'number' ? article.like_count : 0,
        qualityScore: typeof article.quality_score === 'number' ? article.quality_score : 0,
        qualityCheckStatus: article.quality_check_status || 'unchecked',
        qualityCheckedAt: article.quality_checked_at?.substring(0, 16).replace('T', ' ') || null,
        createdAt: article.created_at?.substring(0, 16).replace('T', ' ') || '',
        publishedAt: article.updated_at?.substring(0, 16).replace('T', ' ') || null,
        tags: article.tags || [],
        platforms: article.platforms || ['wechat'],
      }))
      
      setArticles(formattedArticles)
    } catch (err) {
      console.error('获取文章列表失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const statuses = [
    { id: 'all', name: '全部', icon: FileText },
    { id: 'published', name: '已发布', icon: Send },
    { id: 'draft', name: '草稿', icon: FileEdit },
  ]

  const qualityCheckStatuses = [
    { id: 'all', name: '全部质检' },
    { id: 'pass', name: '已通过' },
    { id: 'warning', name: '待优化' },
    { id: 'blocked', name: '未通过' },
    { id: 'unchecked', name: '未质检' },
  ]

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'published':
        return { 
          label: '已发布', 
          bg: 'bg-emerald-50', 
          text: 'text-emerald-600', 
          dot: 'bg-emerald-500',
          icon: CheckCircle
        }
      case 'draft':
        return { 
          label: '草稿', 
          bg: 'bg-amber-50', 
          text: 'text-amber-600', 
          dot: 'bg-amber-500',
          icon: Clock
        }
      default:
        return { 
          label: status, 
          bg: 'bg-gray-50', 
          text: 'text-gray-600', 
          dot: 'bg-gray-500',
          icon: FileText
        }
    }
  }

  const getQualityCheckConfig = (status: string) => {
    switch (status) {
      case 'pass':
        return {
          label: '已通过',
          bg: 'bg-emerald-50',
          text: 'text-emerald-600',
        }
      case 'warning':
        return {
          label: '待优化',
          bg: 'bg-amber-50',
          text: 'text-amber-600',
        }
      case 'blocked':
        return {
          label: '未通过',
          bg: 'bg-rose-50',
          text: 'text-rose-600',
        }
      default:
        return {
          label: '未质检',
          bg: 'bg-slate-100',
          text: 'text-slate-600',
        }
    }
  }

  const handleMultiplatformPublish = (article: any) => {
    setPublishingArticle(article)
    setShowPublishDialog(true)
  }

  const handleSelectArticle = (id: number) => {
    if (selectedArticles.includes(id)) {
      setSelectedArticles(selectedArticles.filter(a => a !== id))
    } else {
      setSelectedArticles([...selectedArticles, id])
    }
  }

  const handleSelectAll = () => {
    if (selectedArticles.length === filteredArticles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(filteredArticles.map(a => a.id))
    }
  }

  const handleDelete = async (article: any) => {
    if (!confirm(`确定要删除"${article.title}"吗？`)) return
    try {
      await deleteArticleAPI(article.id)
      setArticles(articles.filter(a => a.id !== article.id))
    } catch (error) {
      alert('删除失败')
    }
  }

  const handleCopy = async (article: any) => {
    try {
      await copyArticleAPI(article.id)
      await fetchArticles(selectedQualityCheckStatus, debouncedSearchQuery)
      alert('复制成功')
    } catch (error) {
      alert('复制失败')
    }
  }

  const filteredArticles = articles.filter(article => {
    const matchesStatus = selectedStatus === 'all' || article.status === selectedStatus
    return matchesStatus
  }).sort((a, b) => {
    if (sortBy === 'read') return b.readCount - a.readCount
    if (sortBy === 'score') return b.qualityScore - a.qualityScore
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  })

  // 核心数据指标
  const totalReads = articles.reduce((sum, a) => sum + a.readCount, 0)
  const totalLikes = articles.reduce((sum, a) => sum + a.likeCount, 0)
  const avgScore = articles.length > 0 
    ? (articles.reduce((sum, a) => sum + a.qualityScore, 0) / articles.length).toFixed(0) 
    : '0'
  const publishRate = articles.length > 0 
    ? Math.round((articles.filter(a => a.status === 'published').length / articles.length) * 100)
    : 0
  const checkedArticlesCount = articles.filter(a => a.qualityCheckStatus !== 'unchecked').length
  const passedArticlesCount = articles.filter(a => a.qualityCheckStatus === 'pass').length
  const qualityPassRate = checkedArticlesCount > 0
    ? Math.round((passedArticlesCount / checkedArticlesCount) * 100)
    : 0
  const qualityStatusDistribution = [
    { key: 'pass', label: '已通过', count: articles.filter(a => a.qualityCheckStatus === 'pass').length, barColor: 'bg-emerald-500' },
    { key: 'warning', label: '待优化', count: articles.filter(a => a.qualityCheckStatus === 'warning').length, barColor: 'bg-amber-500' },
    { key: 'blocked', label: '未通过', count: articles.filter(a => a.qualityCheckStatus === 'blocked').length, barColor: 'bg-rose-500' },
    { key: 'unchecked', label: '未质检', count: articles.filter(a => a.qualityCheckStatus === 'unchecked').length, barColor: 'bg-slate-400' },
  ]
  const qualityStatusTotal = qualityStatusDistribution.reduce((sum, item) => sum + item.count, 0)

  // 爆款文章（阅读量前3）
  const topArticles = [...articles].sort((a, b) => b.readCount - a.readCount).slice(0, 3)

  // 热门文章（最近发布且表现好）
  const hotArticles = articles
    .filter(a => a.status === 'published')
    .sort((a, b) => (b.readCount * 0.6 + b.likeCount * 10 * 0.4) - (a.readCount * 0.6 + a.likeCount * 10 * 0.4))
    .slice(0, 3)

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 自媒体创作者专属头部 */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto">
          {/* 主标题区 */}
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">内容中心</h1>
                <p className="text-sm text-slate-500">管理您的所有创作内容</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* 快速创作入口 */}
              <Link
                href="/hotspots"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors"
              >
                <Flame className="w-4 h-4 text-orange-500" />
                热点选题
              </Link>
              <Link
                href="/articles/create"
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:from-violet-600 hover:to-purple-700 transition-colors shadow-lg shadow-purple-500/20"
              >
                <Sparkles className="w-4 h-4" />
                AI创作
              </Link>
            </div>
          </div>

          {/* 数据指标条 - 核心KPI一目了然 */}
          <div className="px-6 pb-4">
            <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
              <div className="bg-slate-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <FileText className="w-4 h-4 text-slate-400" />
                  <span className="text-xs text-slate-500">总作品</span>
                </div>
                <p className="text-2xl font-semibold text-slate-900">{articles.length}</p>
              </div>
              <div className="bg-emerald-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <Send className="w-4 h-4 text-emerald-500" />
                  <span className="text-xs text-emerald-600">已发布</span>
                </div>
                <p className="text-2xl font-semibold text-emerald-700">{articles.filter(a => a.status === 'published').length}</p>
              </div>
              <div className="bg-blue-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <Eye className="w-4 h-4 text-blue-500" />
                  <span className="text-xs text-blue-600">总阅读</span>
                </div>
                <p className="text-2xl font-semibold text-blue-700">{(totalReads / 1000).toFixed(1)}k</p>
              </div>
              <div className="bg-pink-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp className="w-4 h-4 text-pink-500" />
                  <span className="text-xs text-pink-600">互动量</span>
                </div>
                <p className="text-2xl font-semibold text-pink-700">{totalLikes.toLocaleString()}</p>
              </div>
              <div className="bg-violet-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <Target className="w-4 h-4 text-violet-500" />
                  <span className="text-xs text-violet-600">平均分</span>
                </div>
                <p className="text-2xl font-semibold text-violet-700">{avgScore}</p>
              </div>
              <div className="bg-emerald-50 rounded-xl px-4 py-3">
                <div className="flex items-center gap-2 mb-1">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  <span className="text-xs text-emerald-600">质检通过率</span>
                </div>
                <p className="text-2xl font-semibold text-emerald-700">{qualityPassRate}%</p>
                <p className="text-[11px] text-emerald-600/80">{passedArticlesCount}/{checkedArticlesCount} 已通过</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex gap-6">
          {/* 左侧主列表 */}
          <div className="flex-1 min-w-0">
            {/* 工具栏 */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              {/* 搜索 */}
              <div className="relative flex-1 min-w-[200px] max-w-sm">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="搜索文章标题..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 rounded-xl bg-white border border-slate-200 text-sm focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                />
              </div>

              {/* 状态筛选 */}
              <div className="flex bg-white border border-slate-200 rounded-xl p-1">
                {statuses.map((status) => {
                  const count = status.id === 'all' 
                    ? articles.length 
                    : articles.filter(a => a.status === status.id).length
                  return (
                    <button
                      key={status.id}
                      onClick={() => setSelectedStatus(status.id)}
                      className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                        selectedStatus === status.id
                          ? 'bg-violet-500 text-white'
                          : 'text-slate-600 hover:bg-slate-100'
                      }`}
                    >
                      <status.icon className="w-4 h-4" />
                      {status.name}
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        selectedStatus === status.id ? 'bg-white/20' : 'bg-slate-100'
                      }`}>
                        {count}
                      </span>
                    </button>
                  )
                })}
              </div>

              {/* 排序 & 视图 */}
              <div className="flex items-center gap-2">
                <select
                  value={selectedQualityCheckStatus}
                  onChange={(e) => setSelectedQualityCheckStatus(e.target.value as any)}
                  className="px-3 py-2 rounded-xl bg-white border border-slate-200 text-sm text-slate-600 focus:outline-none"
                >
                  {qualityCheckStatuses.map((item) => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-2 rounded-xl bg-white border border-slate-200 text-sm text-slate-600 focus:outline-none"
                >
                  <option value="date">最新优先</option>
                  <option value="read">阅读最高</option>
                  <option value="score">评分最高</option>
                </select>
                
                <div className="flex bg-white border border-slate-200 rounded-xl p-1">
                  <button
                    onClick={() => setViewMode('card')}
                    className={`p-1.5 rounded-lg ${viewMode === 'card' ? 'bg-slate-100' : ''}`}
                  >
                    <LayoutGrid className="w-4 h-4 text-slate-600" />
                  </button>
                  <button
                    onClick={() => setViewMode('table')}
                    className={`p-1.5 rounded-lg ${viewMode === 'table' ? 'bg-slate-100' : ''}`}
                  >
                    <List className="w-4 h-4 text-slate-600" />
                  </button>
                </div>
                
                <button
                  onClick={() => fetchArticles(selectedQualityCheckStatus, debouncedSearchQuery)}
                  className="p-2 rounded-xl bg-white border border-slate-200 text-slate-500 hover:bg-slate-50"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>

            {/* 批量操作栏 */}
            {batchMode && selectedArticles.length > 0 && (
              <div className="mb-4 bg-violet-50 border border-violet-200 rounded-xl px-4 py-3 flex items-center justify-between">
                <span className="text-sm text-violet-700">
                  已选择 <strong>{selectedArticles.length}</strong> 篇文章
                </span>
                <div className="flex items-center gap-2">
                  <button onClick={() => setSelectedArticles([])} className="px-3 py-1 rounded-lg text-sm text-violet-600 hover:bg-violet-100">
                    取消
                  </button>
                  <button className="px-3 py-1 rounded-lg text-sm bg-red-500 text-white hover:bg-red-600">
                    批量删除
                  </button>
                </div>
              </div>
            )}

            {/* 文章列表 */}
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
              </div>
            ) : filteredArticles.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
                <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-8 h-8 text-slate-300" />
                </div>
                <p className="text-slate-500 mb-4">暂无文章，开始您的创作之旅</p>
                <Link href="/articles/create">
                  <button className="px-5 py-2 bg-violet-500 text-white rounded-xl text-sm font-medium hover:bg-violet-600">
                    创建第一篇文章
                  </button>
                </Link>
              </div>
            ) : viewMode === 'card' ? (
              /* 卡片视图 - 自媒体友好 */
              <div className="space-y-3">
                {filteredArticles.map((article, index) => {
                  const statusConfig = getStatusConfig(article.status)
                  const qualityCheckConfig = getQualityCheckConfig(article.qualityCheckStatus)
                  const isHot = article.readCount > 2000 || article.likeCount > 100
                  
                  return (
                    <div
                      key={article.id}
                      className="group bg-white rounded-2xl border border-slate-200 hover:border-violet-200 hover:shadow-lg transition-all duration-200 overflow-hidden"
                    >
                      <div className="flex p-4 gap-4">
                        {/* 封面 */}
                        <div className="w-28 h-20 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0">
                          {article.coverImage ? (
                            <img src={article.coverImage} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <FileText className="w-8 h-8 text-slate-200" />
                            </div>
                          )}
                        </div>

                        {/* 内容 */}
                        <div className="flex-1 min-w-0 flex flex-col justify-between">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-medium text-slate-900 truncate group-hover:text-violet-600 transition-colors">
                                {article.title}
                              </h3>
                              {isHot && (
                                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-50 text-orange-600 text-xs font-medium">
                                  <Flame className="w-3 h-3" /> 热门
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-4 text-xs text-slate-500">
                              <span className="flex items-center gap-1">
                                <statusConfig.icon className="w-3 h-3" />
                                {statusConfig.label}
                              </span>
                              <span className={`px-2 py-0.5 rounded ${qualityCheckConfig.bg} ${qualityCheckConfig.text}`}>
                                {qualityCheckConfig.label}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {article.createdAt}
                              </span>
                              {article.qualityCheckedAt && (
                                <span>质检于 {article.qualityCheckedAt}</span>
                              )}
                              <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                                {article.sourceName}
                              </span>
                            </div>
                          </div>
                          
                          {/* 数据指标 */}
                          <div className="flex items-center gap-4">
                            <span className="flex items-center gap-1 text-sm">
                              <Eye className="w-4 h-4 text-blue-500" />
                              <span className="font-medium text-slate-700">{article.readCount.toLocaleString()}</span>
                            </span>
                            <span className="flex items-center gap-1 text-sm">
                              <TrendingUp className="w-4 h-4 text-pink-500" />
                              <span className="font-medium text-slate-700">{article.likeCount}</span>
                            </span>
                            <span className={`flex items-center gap-1 text-sm ${
                              article.qualityScore >= 80 ? 'text-emerald-600' :
                              article.qualityScore >= 60 ? 'text-amber-600' : 'text-slate-500'
                            }`}>
                              <Award className="w-4 h-4" />
                              <span className="font-medium">{article.qualityScore}</span>
                            </span>
                          </div>
                        </div>

                        {/* 操作 */}
                        <div className="flex flex-col justify-center gap-1">
                          <button
                            onClick={() => handleMultiplatformPublish(article)}
                            className="p-2 rounded-lg hover:bg-violet-50 text-slate-400 hover:text-violet-500 transition-colors"
                            title="发布"
                          >
                            <Globe className="w-4 h-4" />
                          </button>
                          <Link
                            href={`/articles/create?editId=${article.id}`}
                            className="p-2 rounded-lg hover:bg-blue-50 text-slate-400 hover:text-blue-500 transition-colors"
                            title="编辑"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(article)}
                            className="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
                            title="删除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              /* 表格视图 - 高效管理 */
              <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-slate-500">文章</th>
                      <th className="text-center px-3 py-3 font-medium text-slate-500 w-20">状态</th>
                      <th className="text-center px-3 py-3 font-medium text-slate-500 w-24">质检</th>
                      <th className="text-right px-3 py-3 font-medium text-slate-500 w-24">阅读</th>
                      <th className="text-right px-3 py-3 font-medium text-slate-500 w-20">互动</th>
                      <th className="text-right px-3 py-3 font-medium text-slate-500 w-16">评分</th>
                      <th className="text-left px-3 py-3 font-medium text-slate-500 w-36">时间</th>
                      <th className="text-center px-3 py-3 font-medium text-slate-500 w-28">操作</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredArticles.map((article) => {
                      const statusConfig = getStatusConfig(article.status)
                      const qualityCheckConfig = getQualityCheckConfig(article.qualityCheckStatus)
                      return (
                        <tr key={article.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-3">
                              <div className="w-12 h-9 rounded-lg bg-slate-100 flex-shrink-0 overflow-hidden">
                                {article.coverImage ? (
                                  <img src={article.coverImage} alt="" className="w-full h-full object-cover" />
                                ) : (
                                  <div className="w-full h-full flex items-center justify-center">
                                    <FileText className="w-4 h-4 text-slate-300" />
                                  </div>
                                )}
                              </div>
                              <span className="font-medium text-slate-900 truncate max-w-[300px]">
                                {article.title}
                              </span>
                            </div>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium ${statusConfig.bg} ${statusConfig.text}`}>
                              {statusConfig.label}
                            </span>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className={`inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium ${qualityCheckConfig.bg} ${qualityCheckConfig.text}`}>
                              {qualityCheckConfig.label}
                            </span>
                          </td>
                          <td className="px-3 py-3 text-right font-mono text-slate-600">
                            {article.readCount.toLocaleString()}
                          </td>
                          <td className="px-3 py-3 text-right font-mono text-slate-600">
                            {article.likeCount}
                          </td>
                          <td className="px-3 py-3 text-right">
                            <span className={`font-mono font-medium ${
                              article.qualityScore >= 80 ? 'text-emerald-600' :
                              article.qualityScore >= 60 ? 'text-amber-600' : 'text-slate-500'
                            }`}>
                              {article.qualityScore}
                            </span>
                          </td>
                          <td className="px-3 py-3 text-slate-500 text-xs">
                            {article.createdAt}
                          </td>
                          <td className="px-3 py-3">
                            <div className="flex items-center justify-center gap-1">
                              <button onClick={() => handleMultiplatformPublish(article)} className="p-1.5 rounded-lg hover:bg-violet-50 text-slate-400 hover:text-violet-500">
                                <Globe className="w-4 h-4" />
                              </button>
                              <Link href={`/articles/create?editId=${article.id}`} className="p-1.5 rounded-lg hover:bg-blue-50 text-slate-400 hover:text-blue-500">
                                <Edit className="w-4 h-4" />
                              </Link>
                              <button onClick={() => handleCopy(article)} className="p-1.5 rounded-lg hover:bg-green-50 text-slate-400 hover:text-green-500">
                                <Copy className="w-4 h-4" />
                              </button>
                              <button onClick={() => handleDelete(article)} className="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500">
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* 底部信息 */}
            {filteredArticles.length > 0 && (
              <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
                <span>共 {filteredArticles.length} 篇文章</span>
                <button
                  onClick={() => setBatchMode(!batchMode)}
                  className={`px-3 py-1.5 rounded-lg text-sm ${
                    batchMode ? 'bg-violet-500 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {batchMode ? '完成' : '批量管理'}
                </button>
              </div>
            )}
          </div>

          {/* 右侧边栏 - 数据洞察 */}
          <div className="hidden xl:block w-72 flex-shrink-0 space-y-4">
            {/* 爆款文章 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="w-4 h-4 text-orange-500" />
                <span className="font-medium text-slate-900 text-sm">爆款文章</span>
              </div>
              <div className="space-y-2">
                {topArticles.map((article, idx) => (
                  <div key={article.id} className="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer">
                    <span className={`w-5 h-5 rounded-lg flex items-center justify-center text-xs font-bold ${
                      idx === 0 ? 'bg-yellow-100 text-yellow-600' :
                      idx === 1 ? 'bg-slate-100 text-slate-500' :
                      'bg-orange-50 text-orange-500'
                    }`}>
                      {idx + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-700 truncate">{article.title}</p>
                      <p className="text-xs text-slate-400">{article.readCount.toLocaleString()} 阅读</p>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-slate-300" />
                  </div>
                ))}
                {topArticles.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-4">暂无数据</p>
                )}
              </div>
            </div>

            {/* 质检状态分布 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <Target className="w-4 h-4 text-emerald-500" />
                <span className="font-medium text-slate-900 text-sm">质检状态分布</span>
              </div>
              <div className="space-y-3">
                {qualityStatusDistribution.map((item) => {
                  const percent = qualityStatusTotal > 0
                    ? Math.round((item.count / qualityStatusTotal) * 100)
                    : 0

                  return (
                    <div key={item.key} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-600">{item.label}</span>
                        <span className="text-slate-500">{item.count} · {percent}%</span>
                      </div>
                      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${item.barColor}`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 创作建议 */}
            <div className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-4 text-white">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4" />
                <span className="font-medium text-sm">创作建议</span>
              </div>
              <div className="space-y-2 text-sm text-white/90">
                <p>📊 发布率 <strong>{publishRate}%</strong>，{publishRate < 50 ? '建议加快发布节奏' : '保持良好！'}</p>
                <p>📝 草稿 <strong>{articles.filter(a => a.status === 'draft').length}</strong> 篇待发布</p>
                <p>🎯 平均评分 <strong>{avgScore}</strong> 分</p>
              </div>
              <Link href="/hotspots" className="mt-3 flex items-center gap-1 text-sm text-white/80 hover:text-white">
                查看热点选题 <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            {/* 快捷操作 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-4">
              <div className="flex items-center gap-2 mb-3">
                <BarChart2 className="w-4 h-4 text-slate-400" />
                <span className="font-medium text-slate-900 text-sm">快捷操作</span>
              </div>
              <div className="space-y-2">
                <Link href="/articles/create" className="flex items-center gap-2 p-2 rounded-xl hover:bg-slate-50 text-slate-600 text-sm transition-colors">
                  <Plus className="w-4 h-4 text-violet-500" />
                  新建文章
                </Link>
                <Link href="/hotspots" className="flex items-center gap-2 p-2 rounded-xl hover:bg-slate-50 text-slate-600 text-sm transition-colors">
                  <Flame className="w-4 h-4 text-orange-500" />
                  热点选题
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 发布对话框 */}
      {showPublishDialog && publishingArticle && (
        <MultiplatformPublishDialog
          isOpen={showPublishDialog}
          onClose={() => {
            setShowPublishDialog(false)
            setPublishingArticle(null)
          }}
          articleId={publishingArticle.id}
          articleTitle={publishingArticle.title}
        />
      )}
    </div>
  )
}
