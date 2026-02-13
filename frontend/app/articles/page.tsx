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
  GripVertical,
  Copy,
  Share2,
  Globe,
  Loader2,
  ChevronDown,
  ChevronUp,
  Archive
} from 'lucide-react'
import Link from 'next/link'
import { API_URL, deleteArticle as deleteArticleAPI, copyArticle as copyArticleAPI } from '@/lib/api'
import MultiplatformPublishDialog from '@/components/multiplatform-publish-dialog'

export default function ArticlesPage() {
  const [selectedStatus, setSelectedStatus] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedStats, setExpandedStats] = useState(true)
  const [selectedArticles, setSelectedArticles] = useState<number[]>([])
  const [batchMode, setBatchMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [articles, setArticles] = useState<any[]>([])
  const [showPublishDialog, setShowPublishDialog] = useState(false)
  const [publishingArticle, setPublishingArticle] = useState<any>(null)

  useEffect(() => {
    fetchArticles()
  }, [])

  const fetchArticles = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/articles`)
      if (!response.ok) throw new Error('获取文章列表失败')
      const data = await response.json()
      
      const formattedArticles = data.map((article: any) => ({
        id: article.id,
        title: article.title,
        status: article.status,
        sourceName: article.source_topic || '手动创建',
        coverImage: article.cover_image_url,
        readCount: article.view_count || 0,
        likeCount: article.like_count || 0,
        qualityScore: article.quality_score || 0,
        createdAt: article.created_at?.substring(0, 16).replace('T', ' ') || '',
        publishedAt: article.updated_at?.substring(0, 16).replace('T', ' ') || null,
        tags: article.tags || [],
      }))
      
      setArticles(formattedArticles)
    } catch (err) {
      console.error('获取文章列表失败:', err)
    } finally {
      setLoading(false)
    }
  }

  const statuses = [
    { id: 'all', name: '全部' },
    { id: 'published', name: '已发布' },
    { id: 'draft', name: '草稿' },
  ]

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-700'
      case 'draft':
        return 'bg-amber-100 text-amber-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'published': return '已发布'
      case 'draft': return '草稿'
      default: return status
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
    if (selectedArticles.length === articles.length) {
      setSelectedArticles([])
    } else {
      setSelectedArticles(articles.map(a => a.id))
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
      await fetchArticles()
      alert('复制成功')
    } catch (error) {
      alert('复制失败')
    }
  }

  const filteredArticles = articles.filter(article => {
    const matchesSearch = !searchQuery || 
      article.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = selectedStatus === 'all' || article.status === selectedStatus
    return matchesSearch && matchesStatus
  })

  return (
    <div className="min-h-screen bg-[#F5F5F7]">
      {/* Header - 现代渐变风格 */}
      <div className="sticky top-0 z-30">
        {/* 渐变背景条 */}
        <div className="h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
        
        <div className="bg-white/80 backdrop-blur-xl border-b border-gray-200/60">
          <div className="max-w-7xl mx-auto px-6 py-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                {/* 3D 风格图标容器 */}
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
                  <div className="relative w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 via-purple-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                    <FileText className="w-6 h-6 text-white" strokeWidth={1.5} />
                  </div>
                </div>
                
                {/* 标题区域 */}
                <div className="flex flex-col">
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-600 bg-clip-text text-transparent">
                    文章管理
                  </h1>
                  <p className="text-sm text-gray-500 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                    创建、编辑和发布您的内容
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {/* 批量操作按钮 */}
                <button
                  onClick={() => setBatchMode(!batchMode)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    batchMode 
                      ? 'bg-gray-900 text-white shadow-lg shadow-gray-900/25' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:scale-105'
                  }`}
                >
                  {batchMode ? '完成' : '批量'}
                </button>
                
                {/* 创建文章按钮 - 渐变风格 */}
                <Link
                  href="/articles/create"
                  className="group flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30 hover:scale-105"
                >
                  <Plus className="w-4 h-4 transition-transform group-hover:rotate-90" />
                  创建文章
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Stats Card */}
        <div className="bg-white rounded-3xl overflow-hidden shadow-sm">
          <button
            onClick={() => setExpandedStats(!expandedStats)}
            className="w-full flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-gray-500" />
              <span className="font-semibold text-gray-900">统计概览</span>
              <span className="text-sm text-gray-500">共 {articles.length} 篇</span>
            </div>
            {expandedStats ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </button>
          
          {expandedStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 pb-6">
              {[
                { label: '总文章', value: articles.length, icon: FileText, color: 'blue' },
                { label: '已发布', value: articles.filter(a => a.status === 'published').length, icon: CheckCircle, color: 'green' },
                { label: '草稿', value: articles.filter(a => a.status === 'draft').length, icon: Clock, color: 'amber' },
                { label: '总阅读', value: articles.reduce((sum, a) => sum + a.readCount, 0).toLocaleString(), icon: Eye, color: 'purple' },
              ].map((stat, idx) => (
                <div key={idx} className="bg-gray-50 rounded-2xl p-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl bg-${stat.color}-100 flex items-center justify-center`}>
                      <stat.icon className={`w-5 h-5 text-${stat.color}-500`} />
                    </div>
                    <div>
                      <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                      <p className="text-xs text-gray-500">{stat.label}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索文章..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-2xl bg-white border-0 shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>
          <div className="flex gap-2">
            {statuses.map((status) => (
              <button
                key={status.id}
                onClick={() => setSelectedStatus(status.id)}
                className={`px-5 py-3 rounded-full text-sm font-medium transition-colors ${
                  selectedStatus === status.id
                    ? 'bg-gray-900 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {status.name}
              </button>
            ))}
          </div>
        </div>

        {/* Batch Actions */}
        {batchMode && selectedArticles.length > 0 && (
          <div className="bg-gray-900 text-white rounded-2xl px-6 py-4 flex items-center justify-between">
            <span className="font-medium">已选择 {selectedArticles.length} 篇文章</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSelectedArticles([])}
                className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors text-sm"
              >
                取消
              </button>
              <button
                onClick={() => {
                  setArticles(articles.filter(a => !selectedArticles.includes(a.id)))
                  setSelectedArticles([])
                  setBatchMode(false)
                }}
                className="px-4 py-2 rounded-full bg-red-500 hover:bg-red-600 transition-colors text-sm"
              >
                删除
              </button>
            </div>
          </div>
        )}

        {/* Articles List */}
        <div className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : filteredArticles.length === 0 ? (
            <div className="bg-white rounded-3xl p-12 text-center">
              <div className="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
                <FileText className="w-10 h-10 text-gray-300" />
              </div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">暂无文章</h3>
              <p className="text-gray-500 mb-4">开始创作您的第一篇文章</p>
              <Link href="/articles/create">
                <button className="px-6 py-3 rounded-full bg-blue-500 text-white font-medium hover:bg-blue-600 transition-colors">
                  创建文章
                </button>
              </Link>
            </div>
          ) : (
            filteredArticles.map((article) => (
              <div
                key={article.id}
                className="bg-white rounded-2xl p-5 hover:shadow-lg transition-all duration-300 group"
              >
                <div className="flex items-start gap-4">
                  {batchMode && (
                    <input
                      type="checkbox"
                      checked={selectedArticles.includes(article.id)}
                      onChange={() => handleSelectArticle(article.id)}
                      className="mt-1 w-5 h-5 rounded-lg border-gray-300 text-blue-500 focus:ring-blue-500"
                    />
                  )}
                  
                  {/* Cover */}
                  <div className="w-24 h-16 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center flex-shrink-0 overflow-hidden">
                    {article.coverImage ? (
                      <img src={article.coverImage} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <FileText className="w-6 h-6 text-gray-400" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                        {article.title}
                      </h3>
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusStyle(article.status)}`}>
                        {getStatusLabel(article.status)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {article.createdAt}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {article.readCount.toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        {article.qualityScore || '--'}分
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleMultiplatformPublish(article)}
                      className="p-2 rounded-xl hover:bg-purple-50 text-gray-400 hover:text-purple-500 transition-colors"
                      title="发布"
                    >
                      <Globe className="w-5 h-5" />
                    </button>
                    <Link
                      href={`/articles/create?editId=${article.id}`}
                      className="p-2 rounded-xl hover:bg-blue-50 text-gray-400 hover:text-blue-500 transition-colors"
                      title="编辑"
                    >
                      <Edit className="w-5 h-5" />
                    </Link>
                    <button
                      onClick={() => handleCopy(article)}
                      className="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                      title="复制"
                    >
                      <Copy className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(article)}
                      className="p-2 rounded-xl hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                      title="删除"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Publish Dialog */}
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
