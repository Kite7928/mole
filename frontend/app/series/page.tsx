'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  BookOpen,
  Plus,
  Search,
  MoreVertical,
  Edit2,
  Trash2,
  Eye,
  LayoutGrid,
  List,
  CheckCircle,
  Clock,
  PauseCircle,
  ChevronRight,
  FileText,
  GripVertical,
  X,
  Image as ImageIcon,
  Tag,
  FolderOpen
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 类型定义
interface Article {
  id: number
  title: string
  status: string
  view_count: number
  like_count: number
  cover_image_url?: string
  created_at: string
}

interface Series {
  id: number
  name: string
  description?: string
  cover_image_url?: string
  status: 'draft' | 'ongoing' | 'completed' | 'paused'
  article_order: number[]
  tags: string[]
  category?: string
  total_articles: number
  total_views: number
  created_at: string
  articles?: Article[]
}

const statusConfig = {
  draft: { label: '策划中', color: 'bg-slate-400', icon: Clock },
  ongoing: { label: '连载中', color: 'bg-violet-500', icon: BookOpen },
  completed: { label: '已完成', color: 'bg-emerald-500', icon: CheckCircle },
  paused: { label: '暂停', color: 'bg-amber-500', icon: PauseCircle }
}

export default function SeriesPage() {
  const router = useRouter()
  const [seriesList, setSeriesList] = useState<Series[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingSeries, setEditingSeries] = useState<Series | null>(null)
  const [selectedSeries, setSelectedSeries] = useState<Series | null>(null)

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    cover_image_url: '',
    category: '',
    tags: ''
  })

  useEffect(() => {
    fetchSeries()
  }, [])

  const fetchSeries = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/content-strategy/series`)
      if (response.ok) {
        const data = await response.json()
        setSeriesList(data)
      }
    } catch (error) {
      console.error('获取系列列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSeriesDetail = async (id: number) => {
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/series/${id}`)
      if (response.ok) {
        const data = await response.json()
        setSelectedSeries(data)
      }
    } catch (error) {
      console.error('获取系列详情失败:', error)
    }
  }

  const openCreateModal = () => {
    setEditingSeries(null)
    setFormData({
      name: '',
      description: '',
      cover_image_url: '',
      category: '',
      tags: ''
    })
    setShowModal(true)
  }

  const openEditModal = (series: Series) => {
    setEditingSeries(series)
    setFormData({
      name: series.name,
      description: series.description || '',
      cover_image_url: series.cover_image_url || '',
      category: series.category || '',
      tags: series.tags.join(', ')
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const url = editingSeries
        ? `${API_URL}/api/content-strategy/series/${editingSeries.id}`
        : `${API_URL}/api/content-strategy/series`
      
      const method = editingSeries ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean)
        })
      })

      if (response.ok) {
        setShowModal(false)
        fetchSeries()
      } else {
        alert('保存失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个系列吗？')) return
    
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/series/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        fetchSeries()
      } else {
        alert('删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      alert('删除失败')
    }
  }

  const handleStatusChange = async (id: number, status: string) => {
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/series/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      
      if (response.ok) {
        fetchSeries()
        if (selectedSeries?.id === id) {
          fetchSeriesDetail(id)
        }
      }
    } catch (error) {
      console.error('更新状态失败:', error)
    }
  }

  const filteredSeries = seriesList.filter(series =>
    series.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    series.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    series.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">系列文章</h1>
                <p className="text-sm text-slate-500">管理和组织系列内容</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* 搜索 */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="搜索系列..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 rounded-xl bg-slate-100 border-0 text-sm w-64 focus:ring-2 focus:ring-violet-100 focus:bg-white transition-all"
                />
              </div>
              
              {/* 视图切换 */}
              <div className="flex bg-slate-100 rounded-xl p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
                >
                  <LayoutGrid className="w-4 h-4 text-slate-600" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
                >
                  <List className="w-4 h-4 text-slate-600" />
                </button>
              </div>
              
              <button
                onClick={openCreateModal}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
              >
                <Plus className="w-4 h-4" />
                新建系列
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSeries.map(series => {
              const status = statusConfig[series.status]
              const StatusIcon = status.icon
              
              return (
                <div
                  key={series.id}
                  className="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
                  onClick={() => fetchSeriesDetail(series.id)}
                >
                  {/* 封面 */}
                  <div className="h-40 bg-gradient-to-br from-violet-100 to-purple-100 relative">
                    {series.cover_image_url ? (
                      <img
                        src={series.cover_image_url}
                        alt={series.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <BookOpen className="w-16 h-16 text-violet-200" />
                      </div>
                    )}
                    <div className={`absolute top-3 left-3 px-3 py-1 rounded-full text-xs font-medium text-white ${status.color}`}>
                      <div className="flex items-center gap-1">
                        <StatusIcon className="w-3 h-3" />
                        {status.label}
                      </div>
                    </div>
                  </div>
                  
                  {/* 内容 */}
                  <div className="p-5">
                    <h3 className="font-semibold text-slate-900 text-lg mb-2 group-hover:text-violet-600 transition-colors">
                      {series.name}
                    </h3>
                    <p className="text-sm text-slate-500 line-clamp-2 mb-4">
                      {series.description || '暂无描述'}
                    </p>
                    
                    {/* 标签 */}
                    {series.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {series.tags.slice(0, 3).map(tag => (
                          <span key={tag} className="px-2 py-1 rounded-lg bg-slate-100 text-slate-600 text-xs">
                            {tag}
                          </span>
                        ))}
                        {series.tags.length > 3 && (
                          <span className="px-2 py-1 rounded-lg bg-slate-100 text-slate-600 text-xs">
                            +{series.tags.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                    
                    {/* 统计 */}
                    <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span className="flex items-center gap-1">
                          <FileText className="w-4 h-4" />
                          {series.total_articles} 篇
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          {series.total_views.toLocaleString()}
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          openEditModal(series)
                        }}
                        className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
            
            {filteredSeries.length === 0 && (
              <div className="col-span-full py-20 text-center text-slate-400">
                <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="mb-4">暂无系列文章</p>
                <button
                  onClick={openCreateModal}
                  className="px-4 py-2 bg-violet-500 text-white rounded-xl text-sm hover:bg-violet-600 transition-colors"
                >
                  创建第一个系列
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="divide-y divide-slate-100">
              {filteredSeries.map(series => {
                const status = statusConfig[series.status]
                const StatusIcon = status.icon
                
                return (
                  <div
                    key={series.id}
                    className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => fetchSeriesDetail(series.id)}
                  >
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-white ${status.color}`}>
                      <StatusIcon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h4 className="font-medium text-slate-900">{series.name}</h4>
                        <span className={`px-2 py-0.5 rounded-full text-xs text-white ${status.color}`}>
                          {status.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                        <span>{series.total_articles} 篇文章</span>
                        <span>{series.total_views.toLocaleString()} 阅读</span>
                        {series.category && (
                          <span className="px-2 py-0.5 rounded bg-slate-100">{series.category}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          openEditModal(series)
                        }}
                        className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDelete(series.id)
                        }}
                        className="p-2 rounded-lg hover:bg-red-50 text-slate-500 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* 系列详情侧边栏 */}
      {selectedSeries && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setSelectedSeries(null)} />
          <div className="relative w-full max-w-2xl bg-white h-full overflow-y-auto">
            {/* 头部 */}
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">系列详情</h2>
              <button
                onClick={() => setSelectedSeries(null)}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6">
              {/* 封面和标题 */}
              <div className="h-48 bg-gradient-to-br from-violet-100 to-purple-100 rounded-2xl mb-6 flex items-center justify-center relative overflow-hidden">
                {selectedSeries.cover_image_url ? (
                  <img
                    src={selectedSeries.cover_image_url}
                    alt={selectedSeries.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <BookOpen className="w-24 h-24 text-violet-200" />
                )}
                <div className={`absolute top-4 left-4 px-3 py-1 rounded-full text-xs font-medium text-white ${statusConfig[selectedSeries.status].color}`}>
                  {statusConfig[selectedSeries.status].label}
                </div>
              </div>
              
              <h3 className="text-2xl font-bold text-slate-900 mb-2">{selectedSeries.name}</h3>
              <p className="text-slate-500 mb-6">{selectedSeries.description || '暂无描述'}</p>
              
              {/* 状态切换 */}
              <div className="flex gap-2 mb-6">
                {Object.entries(statusConfig).map(([key, config]) => (
                  <button
                    key={key}
                    onClick={() => handleStatusChange(selectedSeries.id, key)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                      selectedSeries.status === key
                        ? `${config.color} text-white`
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    <config.icon className="w-4 h-4" />
                    {config.label}
                  </button>
                ))}
              </div>
              
              {/* 统计 */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-slate-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-slate-900">{selectedSeries.total_articles}</p>
                  <p className="text-sm text-slate-500">文章数</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-slate-900">{selectedSeries.total_views.toLocaleString()}</p>
                  <p className="text-sm text-slate-500">总阅读</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-slate-900">{selectedSeries.tags.length}</p>
                  <p className="text-sm text-slate-500">标签数</p>
                </div>
              </div>
              
              {/* 文章列表 */}
              <div>
                <h4 className="font-semibold text-slate-900 mb-4">系列文章</h4>
                <div className="space-y-3">
                  {selectedSeries.articles?.map((article, index) => (
                    <div
                      key={article.id}
                      className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                      onClick={() => router.push(`/articles/create?editId=${article.id}`)}
                    >
                      <div className="w-8 h-8 rounded-lg bg-violet-100 text-violet-600 flex items-center justify-center font-bold text-sm">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-slate-900">{article.title}</h5>
                        <div className="flex items-center gap-3 text-sm text-slate-500 mt-1">
                          <span>{article.view_count.toLocaleString()} 阅读</span>
                          <span>{article.like_count.toLocaleString()} 点赞</span>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    </div>
                  ))}
                  
                  {(!selectedSeries.articles || selectedSeries.articles.length === 0) && (
                    <div className="text-center py-8 text-slate-400">
                      <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
                      <p>暂无文章</p>
                      <Link
                        href="/articles/create"
                        className="mt-3 inline-block px-4 py-2 bg-violet-500 text-white rounded-xl text-sm hover:bg-violet-600 transition-colors"
                      >
                        创建文章
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 创建/编辑弹窗 */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowModal(false)} />
          <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">
                {editingSeries ? '编辑系列' : '新建系列'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">系列名称</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  placeholder="输入系列名称"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all resize-none h-20"
                  placeholder="输入系列描述..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">分类</label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    placeholder="如：技术教程"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">标签</label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({...formData, tags: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    placeholder="用逗号分隔"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">封面图片URL</label>
                <input
                  type="url"
                  value={formData.cover_image_url}
                  onChange={(e) => setFormData({...formData, cover_image_url: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  placeholder="https://..."
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 font-medium hover:bg-slate-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90 transition-opacity"
                >
                  {editingSeries ? '保存修改' : '创建系列'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
