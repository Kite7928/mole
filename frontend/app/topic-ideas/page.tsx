'use client'

import { useState, useEffect } from 'react'
import {
  Lightbulb,
  Plus,
  Search,
  Filter,
  MoreVertical,
  Edit2,
  Trash2,
  CheckCircle,
  Clock,
  AlertCircle,
  Sparkles,
  Tag,
  LayoutGrid,
  List,
  X,
  ArrowRight,
  Flame,
  Target,
  BookOpen
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 类型定义
interface TopicIdea {
  id: number
  title: string
  description?: string
  tags: string[]
  source?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'pending' | 'approved' | 'rejected' | 'converted'
  converted_article_id?: number
  created_at: string
}

const priorityConfig = {
  low: { label: '低', color: 'bg-slate-400', value: 1 },
  medium: { label: '中', color: 'bg-blue-500', value: 2 },
  high: { label: '高', color: 'bg-amber-500', value: 3 },
  urgent: { label: '紧急', color: 'bg-red-500', value: 4 }
}

const statusConfig = {
  pending: { label: '待审核', color: 'bg-slate-400', icon: Clock },
  approved: { label: '已通过', color: 'bg-emerald-500', icon: CheckCircle },
  rejected: { label: '已拒绝', color: 'bg-red-500', icon: AlertCircle },
  converted: { label: '已转化', color: 'bg-violet-500', icon: BookOpen }
}

export default function TopicIdeasPage() {
  type FormDataState = {
    title: string
    description: string
    source: string
    priority: TopicIdea['priority']
    tags: string
  }

  const [ideas, setIdeas] = useState<TopicIdea[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterPriority, setFilterPriority] = useState<string>('all')
  const [showModal, setShowModal] = useState(false)
  const [editingIdea, setEditingIdea] = useState<TopicIdea | null>(null)
  const [showIdeaCapture, setShowIdeaCapture] = useState(false)

  // 表单状态
  const [formData, setFormData] = useState<FormDataState>({
    title: '',
    description: '',
    source: '',
    priority: 'medium',
    tags: ''
  })

  useEffect(() => {
    fetchIdeas()
  }, [filterStatus, filterPriority])

  const fetchIdeas = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filterStatus !== 'all') params.append('status', filterStatus)
      if (filterPriority !== 'all') params.append('priority', filterPriority)
      
      const response = await fetch(`${API_URL}/api/content-strategy/topic-ideas?${params}`)
      if (response.ok) {
        const data = await response.json()
        setIdeas(data)
      }
    } catch (error) {
      console.error('获取选题列表失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const openCreateModal = () => {
    setEditingIdea(null)
    setFormData({
      title: '',
      description: '',
      source: '',
      priority: 'medium',
      tags: ''
    })
    setShowModal(true)
  }

  const openEditModal = (idea: TopicIdea) => {
    setEditingIdea(idea)
    setFormData({
      title: idea.title,
      description: idea.description || '',
      source: idea.source || '',
      priority: idea.priority,
      tags: idea.tags.join(', ')
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const url = editingIdea
        ? `${API_URL}/api/content-strategy/topic-ideas/${editingIdea.id}`
        : `${API_URL}/api/content-strategy/topic-ideas`
      
      const method = editingIdea ? 'PUT' : 'POST'
      
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
        fetchIdeas()
      } else {
        alert('保存失败')
      }
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个选题吗？')) return
    
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/topic-ideas/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        fetchIdeas()
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
      const response = await fetch(`${API_URL}/api/content-strategy/topic-ideas/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      
      if (response.ok) {
        fetchIdeas()
      }
    } catch (error) {
      console.error('更新状态失败:', error)
    }
  }

  const handleConvertToArticle = async (idea: TopicIdea) => {
    try {
      const response = await fetch(`${API_URL}/api/content-strategy/topic-ideas/${idea.id}/convert`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        // 跳转到文章编辑页面
        window.location.href = `/articles/create?article_id=${result.article_id}&from_topic=true&title=${encodeURIComponent(idea.title)}`
      } else {
        alert('转化失败')
      }
    } catch (error) {
      console.error('转化失败:', error)
      alert('转化失败')
    }
  }

  // 灵感采集器 - AI辅助生成选题
  const IdeaCaptureModal = () => {
    const [captureMode, setCaptureMode] = useState<'manual' | 'ai'>('manual')
    const [aiTopic, setAiTopic] = useState('')
    const [aiGenerating, setAiGenerating] = useState(false)
    const [aiSuggestions, setAiSuggestions] = useState<string[]>([])

    const generateIdeas = async () => {
      if (!aiTopic.trim()) return
      setAiGenerating(true)
      
      // 模拟AI生成选题建议
      setTimeout(() => {
        const suggestions = [
          `${aiTopic}入门指南：从零开始的完整教程`,
          `${aiTopic}实战案例：3个成功的应用实例`,
          `${aiTopic}避坑指南：新手常犯的10个错误`,
          `${aiTopic}进阶技巧：提升效率的5个秘诀`,
          `${aiTopic}行业趋势：2024年发展预测`
        ]
        setAiSuggestions(suggestions)
        setAiGenerating(false)
      }, 1500)
    }

    const addSuggestion = (title: string) => {
      setFormData({
        ...formData,
        title
      })
      setCaptureMode('manual')
    }

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowIdeaCapture(false)} />
        <div className="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">选题灵感采集器</h3>
            </div>
            <button
              onClick={() => setShowIdeaCapture(false)}
              className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6">
            {/* 模式切换 */}
            <div className="flex gap-2 mb-6 p-1 bg-slate-100 rounded-xl">
              <button
                onClick={() => setCaptureMode('manual')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                  captureMode === 'manual'
                    ? 'bg-white shadow-sm text-slate-900'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                手动录入
              </button>
              <button
                onClick={() => setCaptureMode('ai')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                  captureMode === 'ai'
                    ? 'bg-white shadow-sm text-violet-600'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Sparkles className="w-4 h-4" />
                AI辅助
              </button>
            </div>
            
            {captureMode === 'manual' ? (
              <form onSubmit={(e) => {
                e.preventDefault()
                setShowIdeaCapture(false)
                setShowModal(true)
              }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">选题标题</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    placeholder="输入选题标题..."
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">灵感来源</label>
                  <input
                    type="text"
                    value={formData.source}
                    onChange={(e) => setFormData({...formData, source: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    placeholder="如：用户反馈、热点新闻、行业报告..."
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90 transition-opacity"
                >
                  保存选题
                </button>
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">输入话题领域</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={aiTopic}
                      onChange={(e) => setAiTopic(e.target.value)}
                      className="flex-1 px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                      placeholder="例如：人工智能、投资理财、健身减肥..."
                    />
                    <button
                      onClick={generateIdeas}
                      disabled={aiGenerating || !aiTopic.trim()}
                      className="px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity flex items-center gap-2"
                    >
                      {aiGenerating ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          生成中
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          生成
                        </>
                      )}
                    </button>
                  </div>
                </div>
                
                {aiSuggestions.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm text-slate-500">AI生成的选题建议：</p>
                    {aiSuggestions.map((suggestion, index) => (
                      <div
                        key={index}
                        onClick={() => addSuggestion(suggestion)}
                        className="p-3 bg-slate-50 rounded-xl cursor-pointer hover:bg-violet-50 hover:border-violet-200 border border-transparent transition-all group"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-slate-700 group-hover:text-violet-700">{suggestion}</span>
                          <Plus className="w-4 h-4 text-slate-400 group-hover:text-violet-500" />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  const filteredIdeas = ideas.filter(idea =>
    idea.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    idea.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    idea.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const stats = {
    total: ideas.length,
    pending: ideas.filter(i => i.status === 'pending').length,
    approved: ideas.filter(i => i.status === 'approved').length,
    converted: ideas.filter(i => i.status === 'converted').length
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">选题库</h1>
                <p className="text-sm text-slate-500">收集和管理创作灵感</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* 搜索 */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="搜索选题..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-2 rounded-xl bg-slate-100 border-0 text-sm w-48 focus:ring-2 focus:ring-violet-100 focus:bg-white transition-all"
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
                onClick={() => setShowIdeaCapture(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
              >
                <Plus className="w-4 h-4" />
                采集灵感
              </button>
            </div>
          </div>
          
          {/* 统计卡片 */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="p-4 bg-slate-50 rounded-xl">
              <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
              <p className="text-sm text-slate-500">总选题</p>
            </div>
            <div className="p-4 bg-amber-50 rounded-xl">
              <p className="text-2xl font-bold text-amber-600">{stats.pending}</p>
              <p className="text-sm text-amber-600/70">待审核</p>
            </div>
            <div className="p-4 bg-emerald-50 rounded-xl">
              <p className="text-2xl font-bold text-emerald-600">{stats.approved}</p>
              <p className="text-sm text-emerald-600/70">已通过</p>
            </div>
            <div className="p-4 bg-violet-50 rounded-xl">
              <p className="text-2xl font-bold text-violet-600">{stats.converted}</p>
              <p className="text-sm text-violet-600/70">已转化</p>
            </div>
          </div>
          
          {/* 筛选器 */}
          <div className="flex gap-3 mt-4">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-100 text-sm text-slate-600 border-0 focus:ring-2 focus:ring-violet-100"
            >
              <option value="all">所有状态</option>
              <option value="pending">待审核</option>
              <option value="approved">已通过</option>
              <option value="rejected">已拒绝</option>
              <option value="converted">已转化</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-slate-100 text-sm text-slate-600 border-0 focus:ring-2 focus:ring-violet-100"
            >
              <option value="all">所有优先级</option>
              <option value="urgent">紧急</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
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
            {filteredIdeas.map(idea => {
              const priority = priorityConfig[idea.priority]
              const status = statusConfig[idea.status]
              const StatusIcon = status.icon
              
              return (
                <div
                  key={idea.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 hover:shadow-lg transition-shadow group"
                >
                  {/* 头部 */}
                  <div className="flex items-start justify-between mb-3">
                    <div className={`px-2 py-1 rounded-lg text-xs font-medium text-white ${priority.color}`}>
                      优先级: {priority.label}
                    </div>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => openEditModal(idea)}
                        className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(idea.id)}
                        className="p-1.5 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  {/* 标题 */}
                  <h3 className="font-semibold text-slate-900 text-lg mb-2">{idea.title}</h3>
                  <p className="text-sm text-slate-500 line-clamp-2 mb-3">
                    {idea.description || '暂无描述'}
                  </p>
                  
                  {/* 来源 */}
                  {idea.source && (
                    <div className="flex items-center gap-1 text-xs text-slate-400 mb-3">
                      <Target className="w-3 h-3" />
                      来源: {idea.source}
                    </div>
                  )}
                  
                  {/* 标签 */}
                  {idea.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {idea.tags.map(tag => (
                        <span key={tag} className="px-2 py-1 rounded-lg bg-slate-100 text-slate-600 text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {/* 状态和操作 */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                    <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium text-white ${status.color}`}>
                      <StatusIcon className="w-3 h-3" />
                      {status.label}
                    </div>
                    
                    {idea.status === 'approved' && (
                      <button
                        onClick={() => handleConvertToArticle(idea)}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-violet-100 text-violet-600 text-sm font-medium hover:bg-violet-200 transition-colors"
                      >
                        <ArrowRight className="w-4 h-4" />
                        创作
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
            
            {filteredIdeas.length === 0 && (
              <div className="col-span-full py-20 text-center text-slate-400">
                <Lightbulb className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="mb-4">暂无选题灵感</p>
                <button
                  onClick={() => setShowIdeaCapture(true)}
                  className="px-4 py-2 bg-violet-500 text-white rounded-xl text-sm hover:bg-violet-600 transition-colors"
                >
                  采集第一个灵感
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
            <div className="divide-y divide-slate-100">
              {filteredIdeas.map(idea => {
                const priority = priorityConfig[idea.priority]
                const status = statusConfig[idea.status]
                const StatusIcon = status.icon
                
                return (
                  <div key={idea.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors">
                    <div className={`w-2 h-12 rounded-full ${priority.color}`} />
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h4 className="font-medium text-slate-900">{idea.title}</h4>
                        <span className={`px-2 py-0.5 rounded-full text-xs text-white ${status.color}`}>
                          <div className="flex items-center gap-1">
                            <StatusIcon className="w-3 h-3" />
                            {status.label}
                          </div>
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
                        <span>优先级: {priority.label}</span>
                        {idea.source && <span>来源: {idea.source}</span>}
                        {idea.tags.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Tag className="w-3 h-3" />
                            {idea.tags.join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {idea.status === 'approved' && (
                        <button
                          onClick={() => handleConvertToArticle(idea)}
                          className="px-3 py-1.5 rounded-lg bg-violet-100 text-violet-600 text-sm font-medium hover:bg-violet-200 transition-colors"
                        >
                          开始创作
                        </button>
                      )}
                      <button
                        onClick={() => openEditModal(idea)}
                        className="p-2 rounded-lg hover:bg-slate-200 text-slate-500 transition-colors"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(idea.id)}
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

      {/* 创建/编辑弹窗 */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowModal(false)} />
          <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">
                {editingIdea ? '编辑选题' : '新建选题'}
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
                <label className="block text-sm font-medium text-slate-700 mb-1">选题标题</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  placeholder="输入选题标题"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all resize-none h-20"
                  placeholder="输入选题描述..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">优先级</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value as any})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  >
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                    <option value="urgent">紧急</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">来源</label>
                  <input
                    type="text"
                    value={formData.source}
                    onChange={(e) => setFormData({...formData, source: e.target.value})}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                    placeholder="如：用户反馈"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">标签</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({...formData, tags: e.target.value})}
                  className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 outline-none transition-all"
                  placeholder="用逗号分隔多个标签"
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
                  {editingIdea ? '保存修改' : '创建选题'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 灵感采集器弹窗 */}
      {showIdeaCapture && <IdeaCaptureModal />}
    </div>
  )
}
