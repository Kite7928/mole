'use client'

import { useState, useEffect } from 'react'
import {
  FileText,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  Clock,
  TrendingUp,
  Calendar,
  ArrowRight,
  GripVertical,
  ChevronDown,
  ChevronUp,
  Move,
  Archive,
  Copy,
  Share2,
  Globe,
  Loader2,
  X,
  Download
} from 'lucide-react'
import Link from 'next/link'
import { API_URL, deleteArticle as deleteArticleAPI, copyArticle as copyArticleAPI } from '@/lib/api'
import MultiplatformPublishDialog from '@/components/multiplatform-publish-dialog'
import ArticleCardSkeletonList from '@/components/skeletons/article-card-skeleton'

export default function ArticlesPage() {
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [selectedSource, setSelectedSource] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedStats, setExpandedStats] = useState(true)
  const [selectedArticles, setSelectedArticles] = useState<number[]>([])
  const [batchMode, setBatchMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 多平台发布相关状态
  const [showPublishDialog, setShowPublishDialog] = useState(false)
  const [publishingArticle, setPublishingArticle] = useState<any>(null)

  // 编辑相关状态
  const [editingArticle, setEditingArticle] = useState<any>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')
  const [showEditDialog, setShowEditDialog] = useState(false)

  // 预览相关状态
  const [previewingArticle, setPreviewingArticle] = useState<any>(null)
  const [showPreviewDialog, setShowPreviewDialog] = useState(false)

  // 更多操作相关状态
  const [moreActionArticle, setMoreActionArticle] = useState<any>(null)
  const [showMoreMenu, setShowMoreMenu] = useState(false)

  // 从后端 API 加载文章列表
  useEffect(() => {
    fetchArticles()
  }, [])

  const fetchArticles = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/articles`)
      if (!response.ok) {
        throw new Error('获取文章列表失败')
      }
      const data = await response.json()
      
      // 转换数据格式以匹配前端界面
      const formattedArticles = data.map((article: any) => ({
        id: article.id,
        title: article.title,
        status: article.status,
        source: article.source_topic ? 'ai_hotspot' : 'manual',
        sourceName: article.source_topic || '手动创建',
        aiModel: 'AI',
        coverImage: article.cover_image_url || null,
        readCount: article.view_count || 0,
        likeCount: article.like_count || 0,
        shareCount: 0,
        qualityScore: article.quality_score || 0,
        predictedClickRate: Math.floor(Math.random() * 30 + 60), // 模拟预测点击率
        createdAt: article.created_at?.substring(0, 16).replace('T', ' ') || '',
        publishedAt: article.updated_at?.substring(0, 16).replace('T', ' ') || null,
        tags: article.tags || [],
      }))
      
      setArticles(formattedArticles)
    } catch (err: any) {
      console.error('获取文章列表失败:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const statuses = [
    { id: 'all', name: '全部状态', count: 5 },
    { id: 'published', name: '已发布', count: 3 },
    { id: 'draft', name: '草稿', count: 1 },
    { id: 'generating', name: '生成中', count: 1 },
  ]

  const sources = [
    { id: 'all', name: '全部来源' },
    { id: 'ai_hotspot', name: 'AI热点' },
    { id: 'baidu_search', name: '百度搜索' },
    { id: 'manual', name: '手动创建' },
  ]

  const [articles, setArticles] = useState([
    {
      id: 1,
      title: 'GPT-4o发布：AI推理能力的新突破',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect width="200" height="150" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="14" fill="%239ca3af"%3EGPT-4o%3C/text%3E%3C/svg%3E',
      readCount: 25680,
      likeCount: 890,
      shareCount: 320,
      qualityScore: 87,
      predictedClickRate: 85,
      createdAt: '2026-01-09 10:00',
      publishedAt: '2026-01-09 10:00',
      tags: ['AI', 'GPT-4', '技术'],
    },
    {
      id: 2,
      title: 'DeepSeek-V3：开源模型的新里程碑',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect width="200" height="150" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="14" fill="%239ca3af"%3EDeepSeek-V3%3C/text%3E%3C/svg%3E',
      readCount: 18450,
      likeCount: 654,
      shareCount: 210,
      qualityScore: 82,
      predictedClickRate: 78,
      createdAt: '2026-01-09 09:30',
      publishedAt: '2026-01-09 09:30',
      tags: ['AI', 'DeepSeek', '开源'],
    },
    {
      id: 3,
      title: 'Claude 3.5 Sonnet：长文本处理的王者',
      status: 'draft',
      source: 'baidu_search',
      sourceName: '百度搜索',
      aiModel: 'Claude 3.5',
      coverImage: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect width="200" height="150" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="14" fill="%239ca3af"%3EClaude 3.5%3C/text%3E%3C/svg%3E',
      readCount: 0,
      likeCount: 0,
      shareCount: 0,
      qualityScore: 85,
      predictedClickRate: 72,
      createdAt: '2026-01-09 08:00',
      publishedAt: null,
      tags: ['AI', 'Claude', '长文本'],
    },
    {
      id: 4,
      title: 'Gemini Pro：谷歌AI的最新答卷',
      status: 'generating',
      source: 'manual',
      sourceName: '手动创建',
      aiModel: 'Gemini Pro',
      coverImage: null,
      readCount: 0,
      likeCount: 0,
      shareCount: 0,
      qualityScore: 0,
      predictedClickRate: 68,
      createdAt: '2026-01-09 07:30',
      publishedAt: null,
      tags: ['AI', 'Gemini', 'Google'],
    },
    {
      id: 5,
      title: '2024年AI大模型发展报告',
      status: 'published',
      source: 'ai_hotspot',
      sourceName: 'AI热点',
      aiModel: 'GPT-4',
      coverImage: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="150"%3E%3Crect width="200" height="150" fill="%23f3f4f6"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="system-ui" font-size="14" fill="%239ca3af"%3E2024报告%3C/text%3E%3C/svg%3E',
      readCount: 10560,
      likeCount: 380,
      shareCount: 120,
      qualityScore: 90,
      predictedClickRate: 65,
      createdAt: '2026-01-08 15:00',
      publishedAt: '2026-01-08 15:00',
      tags: ['AI', '报告', '趋势'],
    },
  ])

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      published: { label: '已发布', className: 'bg-green-100 text-green-700 border-green-200' },
      draft: { label: '草稿', className: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
      generating: { label: '生成中', className: 'bg-blue-100 text-blue-700 border-blue-200' },
    }
    const config = statusConfig[status as keyof typeof statusConfig]
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${config?.className}`}>
        {config?.label}
      </span>
    )
  }

  const getQualityScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-gray-500'
  }

  // 处理多平台发布
  const handleMultiplatformPublish = (article: any) => {
    console.log('多平台发布:', article.id)
    setPublishingArticle(article)
    setShowPublishDialog(true)
  }

  const handleSelectAll = () => {
    if (selectedArticles.length === articles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(articles.map(a => a.id))
    }
  }

  const handleSelectArticle = (id: number) => {
    if (selectedArticles.includes(id)) {
      setSelectedArticles(selectedArticles.filter(a => a !== id))
    } else {
      setSelectedArticles([...selectedArticles, id])
    }
  }

  const handleBatchDelete = () => {
    console.log('Batch delete:', selectedArticles)
    setSelectedArticles([])
    setBatchMode(false)
  }

  const handleBatchPublish = () => {
    console.log('Batch publish:', selectedArticles)
    setSelectedArticles([])
    setBatchMode(false)
  }

  // 处理单个文章操作
  const handlePreview = (article: any) => {
    console.log('预览文章:', article.id)
    setPreviewingArticle(article)
    setShowPreviewDialog(true)
  }

  const handleEdit = (article: any) => {
    console.log('编辑文章:', article.id)
    // 打开编辑对话框
    setEditingArticle(article)
    setEditTitle(article.title)
    setEditContent(article.content || '')
    setShowEditDialog(true)
  }

  const handleSaveEdit = async () => {
    if (!editingArticle) return

    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/articles/${editingArticle.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: editTitle,
          content: editContent,
        }),
      })

      if (!response.ok) {
        throw new Error('更新文章失败')
      }

      // 更新本地文章列表
      setArticles(articles.map(a => 
        a.id === editingArticle.id 
          ? { ...a, title: editTitle, content: editContent }
          : a
      ))

      setShowEditDialog(false)
      setEditingArticle(null)
      alert('文章更新成功！')
    } catch (err: any) {
      console.error('更新文章失败:', err)
      alert(`更新失败: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCancelEdit = () => {
    setShowEditDialog(false)
    setEditingArticle(null)
    setEditTitle('')
    setEditContent('')
  }

  const handleCopy = async (article: any) => {
    try {
      setLoading(true)
      console.log('复制文章:', article.id)
      const result = await copyArticleAPI(article.id)
      console.log('复制成功:', result)
      alert('文章复制成功！')
      // 重新加载文章列表
      await fetchArticles()
    } catch (error: any) {
      console.error('复制文章失败:', error)
      alert(`复制失败: ${error.message}`)
      setLoading(false)
    }
  }

  const handleDelete = async (article: any) => {
    if (!confirm(`确定要删除文章"${article.title}"吗？此操作不可恢复。`)) {
      return
    }

    try {
      setLoading(true)
      console.log('删除文章:', article.id)
      await deleteArticleAPI(article.id)
      console.log('删除成功')
      alert('文章删除成功！')
      // 从列表中移除已删除的文章
      setArticles(articles.filter(a => a.id !== article.id))
      setLoading(false)
    } catch (error: any) {
      console.error('删除文章失败:', error)
      alert(`删除失败: ${error.message}`)
      setLoading(false)
    }
  }

  const handleMore = (article: any) => {
    console.log('更多操作:', article.id)
    setMoreActionArticle(article)
    setShowMoreMenu(true)
  }

  const handleMoreAction = async (action: string) => {
    if (!moreActionArticle) return

    try {
      setLoading(true)
      switch (action) {
        case 'export':
          // 导出功能
          alert('导出功能开发中...')
          break
        case 'archive':
          // 归档功能
          await fetch(`${API_URL}/api/articles/${moreActionArticle.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'draft' })
          })
          alert('文章已归档')
          await fetchArticles()
          break
        case 'share':
          // 分享功能
          const shareUrl = `${window.location.origin}/articles/${moreActionArticle.id}`
          navigator.clipboard.writeText(shareUrl)
          alert('分享链接已复制到剪贴板')
          break
      }
      setShowMoreMenu(false)
      setMoreActionArticle(null)
    } catch (error: any) {
      console.error('操作失败:', error)
      alert(`操作失败: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">文章管理</h1>
          <p className="text-muted-foreground mt-1">管理和发布您的文章内容</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setBatchMode(!batchMode)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              batchMode 
                ? 'bg-[#5a6e5c] text-white border-[#5a6e5c]' 
                : 'border-gray-300 text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Archive size={20} />
            批量操作
          </button>
          <Link
            href="/articles/create"
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300 font-medium"
          >
            <Plus size={20} />
            创建文章
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 bg-white/50 backdrop-blur-sm rounded-2xl p-4 border border-gray-200">
        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter size={20} className="text-muted-foreground" />
          <span className="text-sm font-medium">状态:</span>
          <div className="flex gap-2">
            {statuses.map((status) => (
              <button
                key={status.id}
                onClick={() => setSelectedStatus(status.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedStatus === status.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {status.name}
                {status.count > 0 && (
                  <span className="ml-1.5 px-2 py-0.5 rounded-full bg-gray-200 text-gray-700 text-xs">
                    {status.count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Source Filter */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">来源:</span>
          <div className="flex gap-2">
            {sources.map((source) => (
              <button
                key={source.id}
                onClick={() => setSelectedSource(source.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                  selectedSource === source.id
                    ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                    : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
                }`}
              >
                {source.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" size={20} />
        <input
          type="text"
          placeholder="搜索文章标题、标签..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/80 backdrop-blur-sm border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all"
        />
      </div>

      {/* Collapsible Stats */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 overflow-hidden">
        <button
          onClick={() => setExpandedStats(!expandedStats)}
          className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <FileText size={20} className="text-[#5a6e5c]" />
            <span className="font-semibold text-gray-900">统计概览</span>
            <span className="text-sm text-gray-500">共 {articles.length} 篇文章</span>
          </div>
          {expandedStats ? <ChevronUp size={20} className="text-gray-500" /> : <ChevronDown size={20} className="text-gray-500" />}
        </button>
        
        {expandedStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 px-6 pb-6">
            <StatCard
              title="总文章数"
              value={articles.length}
              icon={<FileText size={24} />}
              color="from-blue-500 to-blue-600"
              bg="bg-blue-100"
              textColor="text-blue-600"
              onClick={() => setSelectedStatus('all')}
            />
            <StatCard
              title="已发布"
              value={articles.filter(a => a.status === 'published').length}
              icon={<CheckCircle size={24} />}
              color="from-green-500 to-green-600"
              bg="bg-green-100"
              textColor="text-green-600"
              onClick={() => setSelectedStatus('published')}
            />
            <StatCard
              title="草稿"
              value={articles.filter(a => a.status === 'draft').length}
              icon={<Clock size={24} />}
              color="from-yellow-500 to-yellow-600"
              bg="bg-yellow-100"
              textColor="text-yellow-600"
              onClick={() => setSelectedStatus('draft')}
            />
            <StatCard
              title="总阅读量"
              value={articles.reduce((sum, a) => sum + a.readCount, 0).toLocaleString()}
              icon={<TrendingUp size={24} />}
              color="from-purple-500 to-purple-600"
              bg="bg-purple-100"
              textColor="text-purple-600"
              onClick={() => {}}
            />
          </div>
        )}
      </div>

      {/* Batch Actions */}
      {batchMode && selectedArticles.length > 0 && (
        <div className="bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl px-6 py-4 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-3">
            <span className="font-medium">已选择 {selectedArticles.length} 篇文章</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleBatchPublish}
              className="flex items-center gap-2 px-4 py-2 bg-white text-[#5a6e5c] rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              <CheckCircle size={18} />
              批量发布
            </button>
            <button
              onClick={handleBatchDelete}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
            >
              <Trash2 size={18} />
              批量删除
            </button>
            <button
              onClick={() => setSelectedArticles([])}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors"
            >
              取消选择
            </button>
          </div>
        </div>
      )}

      {/* Articles List */}
      <div className="space-y-3">
        {loading ? (
          <ArticleCardSkeletonList count={5} />
        ) : articles.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
            <FileText size={48} className="mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-700 mb-2">暂无文章</h3>
            <p className="text-gray-500 mb-4">您还没有创建任何文章，开始创作您的第一篇文章吧！</p>
            <Link href="/articles/create">
              <button className="px-6 py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-lg hover:shadow-lg transition-all">
                创建文章
              </button>
            </Link>
          </div>
        ) : (
          articles.map((article, index) => (
          <div
            key={article.id}
            className="bg-white/90 backdrop-blur-sm rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:shadow-gray-500/10 transition-all duration-300 hover:border-[#5a6e5c]/30 group"
          >
            <div className="flex items-start gap-4">
              {/* Drag Handle */}
              <div className="flex items-center gap-2 pt-1">
                {batchMode && (
                  <input
                    type="checkbox"
                    checked={selectedArticles.includes(article.id)}
                    onChange={() => handleSelectArticle(article.id)}
                    className="w-4 h-4 rounded border-gray-300 text-[#5a6e5c] focus:ring-[#5a6e5c]"
                  />
                )}
                <button className="p-1 hover:bg-gray-100 rounded transition-colors cursor-grab">
                  <GripVertical size={20} className="text-gray-400" />
                </button>
              </div>

              {/* Thumbnail */}
              <div className="w-32 h-20 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-gray-100 to-gray-200">
                {article.coverImage ? (
                  <img
                    src={article.coverImage}
                    alt={article.title}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <FileText size={32} />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Title Row */}
                <div className="flex items-start gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1 line-clamp-1 group-hover:text-[#5a6e5c] transition-colors">
                    {article.title}
                  </h3>
                  {getStatusBadge(article.status)}
                </div>

                {/* Tags */}
                <div className="flex items-center gap-2 mb-2">
                  {article.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2.5 py-1 rounded-full bg-[#5a6e5c]/10 text-[#5a6e5c] text-xs font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                  <span className="text-xs text-gray-500">• {article.sourceName}</span>
                  <span className="text-xs text-gray-500">• {article.aiModel}</span>
                </div>

                {/* Stats Row */}
                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-1.5">
                    <Eye size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.readCount.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <CheckCircle size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.likeCount}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Share2 size={16} className="text-gray-400" />
                    <span className="font-medium text-gray-900">{article.shareCount}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className={`font-semibold ${getQualityScoreColor(article.qualityScore)}`}>
                      {article.qualityScore}
                    </span>
                    <span className="text-xs text-gray-500">质量分</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-yellow-600">
                      {article.predictedClickRate}%
                    </span>
                    <span className="text-xs text-gray-500">预测点击率</span>
                  </div>
                </div>
              </div>

              {/* Time */}
              <div className="flex flex-col items-end gap-1 text-sm text-gray-500">
                <div className="flex items-center gap-1.5">
                  <Calendar size={16} />
                  {article.createdAt}
                </div>
                {article.publishedAt && (
                  <div className="flex items-center gap-1.5 text-xs">
                    <Clock size={14} />
                    发布于 {article.publishedAt}
                  </div>
                )}
              </div>

              {/* Actions - Hover */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleMultiplatformPublish(article)}
                  className="p-2 rounded-lg hover:bg-purple-100 text-gray-600 hover:text-purple-600 transition-colors"
                  title="多平台发布"
                >
                  <Globe size={18} />
                </button>
                <button
                  onClick={() => handlePreview(article)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="预览"
                >
                  <Eye size={18} />
                </button>
                <button
                  onClick={() => handleEdit(article)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="编辑"
                >
                  <Edit size={18} />
                </button>
                <button
                  onClick={() => handleCopy(article)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="复制"
                >
                  <Copy size={18} />
                </button>
                <button
                  onClick={() => handleDelete(article)}
                  className="p-2 rounded-lg hover:bg-red-100 text-gray-600 hover:text-red-600 transition-colors"
                  title="删除"
                >
                  <Trash2 size={18} />
                </button>
                <button
                  onClick={() => handleMore(article)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600 hover:text-[#5a6e5c] transition-colors"
                  title="更多"
                >
                  <MoreVertical size={18} />
                </button>
              </div>
            </div>
          </div>
        )))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          显示 1-{articles.length} 条，共 {articles.length} 条
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm disabled:opacity-50 font-medium">
            上一页
          </button>
          <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white text-sm font-medium">
            1
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            2
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            3
          </button>
          <button className="px-4 py-2 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors text-sm">
            下一页 <ArrowRight size={14} className="inline ml-1" />
          </button>
        </div>
      </div>

      {/* 多平台发布对话框 */}
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

      {/* 编辑文章对话框 */}
      {showEditDialog && editingArticle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* 标题栏 */}
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">编辑文章</h2>
              <button
                onClick={handleCancelEdit}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <MoreVertical size={20} className="text-gray-500" />
              </button>
            </div>

            {/* 内容区 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">标题</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all"
                  placeholder="请输入文章标题"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">内容</label>
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={15}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all resize-none"
                  placeholder="请输入文章内容（支持 Markdown 格式）"
                />
              </div>
            </div>

            {/* 操作栏 */}
            <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
              <button
                onClick={handleCancelEdit}
                className="px-6 py-3 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-100 transition-colors font-medium"
              >
                取消
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={loading || !editTitle.trim()}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '保存中...' : '保存修改'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 预览对话框 */}
      {showPreviewDialog && previewingArticle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* 标题栏 */}
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">文章预览</h2>
              <button
                onClick={() => setShowPreviewDialog(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X size={24} className="text-gray-500" />
              </button>
            </div>

            {/* 内容区域 */}
            <div className="flex-1 overflow-y-auto p-6">
              <article className="prose prose-lg max-w-none">
                <h1 className="text-3xl font-bold mb-4">{previewingArticle.title}</h1>
                <div className="flex items-center gap-4 mb-6 text-sm text-gray-500">
                  <span>创建于 {previewingArticle.createdAt}</span>
                  <span>•</span>
                  <span>{previewingArticle.sourceName}</span>
                </div>
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {previewingArticle.content}
                </div>
              </article>
            </div>

            {/* 操作栏 */}
            <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
              <button
                onClick={() => setShowPreviewDialog(false)}
                className="px-6 py-3 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-100 transition-colors font-medium"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 更多操作菜单 */}
      {showMoreMenu && moreActionArticle && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowMoreMenu(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">更多操作</h3>
              <p className="text-sm text-gray-500 mt-1">{moreActionArticle.title}</p>
            </div>
            <div className="p-2">
              <button
                onClick={() => handleMoreAction('share')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors text-left"
              >
                <Share2 size={20} className="text-gray-500" />
                <span className="font-medium text-gray-700">分享链接</span>
              </button>
              <button
                onClick={() => handleMoreAction('export')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors text-left"
              >
                <Download size={20} className="text-gray-500" />
                <span className="font-medium text-gray-700">导出文章</span>
              </button>
              <button
                onClick={() => handleMoreAction('archive')}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors text-left"
              >
                <Archive size={20} className="text-gray-500" />
                <span className="font-medium text-gray-700">归档文章</span>
              </button>
            </div>
            <div className="p-2 border-t">
              <button
                onClick={() => {
                  setShowMoreMenu(false)
                  setMoreActionArticle(null)
                }}
                className="w-full flex items-center justify-center px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors font-medium text-gray-600"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  icon,
  color,
  bg,
  textColor,
  onClick
}: { 
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
  bg: string
  textColor: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full p-4 rounded-xl bg-gradient-to-br ${bg} hover:shadow-lg hover:shadow-gray-500/10 transition-all duration-300 hover:-translate-y-1 text-left`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${color} text-white`}>
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className={`text-sm font-medium ${textColor}`}>{title}</p>
        </div>
      </div>
    </button>
  )
}