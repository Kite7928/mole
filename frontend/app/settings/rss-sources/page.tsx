'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import {
  Rss,
  Plus,
  RefreshCw,
  Trash2,
  Edit3,
  CheckCircle,
  XCircle,
  AlertCircle,
  ExternalLink,
  Loader2,
  Globe,
  Tag,
  Clock,
  BarChart3,
  ArrowLeft
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { API_URL } from '@/lib/api'

// RSS源类型定义
interface RssSource {
  id: number
  name: string
  url: string
  description?: string
  category?: string
  is_active: boolean
  is_official: boolean
  fetch_count: number
  last_fetched_at?: string
  last_error?: string
  created_at: string
  updated_at?: string
}

// 预设分类
const PRESET_CATEGORIES = [
  '科技',
  '技术',
  '产品',
  '创业',
  '人工智能',
  '开源',
  '资讯',
  '博客',
  '其他'
]

// 推荐的RSS源
const RECOMMENDED_SOURCES = [
  { name: '阮一峰的网络日志', url: 'http://www.ruanyifeng.com/blog/atom.xml', category: '博客', description: '科技爱好者周刊' },
  { name: '酷壳', url: 'https://coolshell.cn/feed', category: '技术', description: '陈皓的技术博客' },
  { name: '月光博客', url: 'https://www.williamlong.info/rss.xml', category: '互联网', description: '知名中文IT博客' },
  { name: '张鑫旭-鑫空间', url: 'https://www.zhangxinxu.com/wordpress/feed/', category: '前端', description: '前端技术专家' },
]

// RSSHub 路由模板（点击可一键填入）
const RSSHUB_ROUTE_TEMPLATES = [
  { name: 'RSSHub · IT之家', url: '/ithome/rss', category: '科技', description: '通过 RSSHub 聚合 IT之家最新内容' },
  { name: 'RSSHub · 36氪快讯', url: '/36kr/newsflashes', category: '资讯', description: '通过 RSSHub 获取 36氪快讯流' },
  { name: 'RSSHub · 少数派', url: '/sspai/index', category: '产品', description: '通过 RSSHub 跟踪少数派最新文章' },
  { name: 'RSSHub · 开源中国', url: '/oschina/news', category: '开源', description: '通过 RSSHub 获取开源中国新闻' },
]

export default function RssSourcesPage() {
  const router = useRouter()
  const [sources, setSources] = useState<RssSource[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState<number | null>(null)
  const [testing, setTesting] = useState<number | null>(null)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [importingPresets, setImportingPresets] = useState(false)

  // 添加/编辑对话框状态
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingSource, setEditingSource] = useState<RssSource | null>(null)

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    description: '',
    category: ''
  })
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 测试结果显示
  const [testResults, setTestResults] = useState<Record<number, any>>({})

  const isValidRssUrl = (url: string) => {
    const value = url.trim()
    return (
      value.startsWith('http://') ||
      value.startsWith('https://') ||
      value.startsWith('rsshub://') ||
      value.startsWith('/')
    )
  }

  // 加载RSS源列表
  const fetchSources = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_URL}/api/rss-sources?include_inactive=true`)
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setSources(data.sources || [])
        }
      }
    } catch (error) {
      console.error('获取RSS源失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSources()
  }, [])

  // 验证表单
  const validateForm = () => {
    const errors: Record<string, string> = {}

    if (!formData.name.trim()) {
      errors.name = '请输入源名称'
    }

    if (!formData.url.trim()) {
      errors.url = '请输入RSS地址'
    } else if (!isValidRssUrl(formData.url)) {
      errors.url = '支持 http(s)://、rsshub:// 或 /route 格式'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  // 添加RSS源
  const handleAddSource = async () => {
    if (!validateForm()) return

    try {
      setIsSubmitting(true)
      const response = await fetch(`${API_URL}/api/rss-sources/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setIsAddDialogOpen(false)
        setFormData({ name: '', url: '', description: '', category: '' })
        fetchSources()
      } else {
        setFormErrors({ submit: data.detail || '添加失败' })
      }
    } catch (error) {
      setFormErrors({ submit: '网络错误，请稍后重试' })
    } finally {
      setIsSubmitting(false)
    }
  }

  // 更新RSS源
  const handleUpdateSource = async () => {
    if (!editingSource || !validateForm()) return

    try {
      setIsSubmitting(true)
      const response = await fetch(`${API_URL}/api/rss-sources/${editingSource.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setIsEditDialogOpen(false)
        setEditingSource(null)
        setFormData({ name: '', url: '', description: '', category: '' })
        fetchSources()
      } else {
        setFormErrors({ submit: data.detail || '更新失败' })
      }
    } catch (error) {
      setFormErrors({ submit: '网络错误，请稍后重试' })
    } finally {
      setIsSubmitting(false)
    }
  }

  // 删除RSS源
  const handleDeleteSource = async (id: number) => {
    if (!confirm('确定要删除这个RSS源吗？')) return

    try {
      setDeleting(id)
      const response = await fetch(`${API_URL}/api/rss-sources/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (response.ok && data.success) {
        fetchSources()
      } else {
        alert(data.detail || '删除失败')
      }
    } catch (error) {
      alert('删除失败，请稍后重试')
    } finally {
      setDeleting(null)
    }
  }

  // 测试RSS源
  const handleTestSource = async (id: number) => {
    try {
      setTesting(id)
      const response = await fetch(`${API_URL}/api/rss-sources/${id}/test`, {
        method: 'POST'
      })

      const data = await response.json()
      setTestResults({ ...testResults, [id]: data })

      if (!data.success) {
        alert(`测试失败: ${data.message}`)
      }
    } catch (error) {
      alert('测试失败，请稍后重试')
    } finally {
      setTesting(null)
    }
  }

  // 从RSS源抓取新闻
  const handleFetchFromSource = async (id: number) => {
    try {
      setRefreshing(id)
      const response = await fetch(`${API_URL}/api/rss-sources/${id}/fetch?limit=20`, {
        method: 'POST'
      })

      const data = await response.json()

      if (response.ok && data.success) {
        alert(`成功抓取 ${data.count} 条新闻`)
        fetchSources()
      } else {
        alert(data.detail || '抓取失败')
      }
    } catch (error) {
      alert('抓取失败，请稍后重试')
    } finally {
      setRefreshing(null)
    }
  }

  // 打开编辑对话框
  const openEditDialog = (source: RssSource) => {
    setEditingSource(source)
    setFormData({
      name: source.name,
      url: source.url,
      description: source.description || '',
      category: source.category || ''
    })
    setFormErrors({})
    setIsEditDialogOpen(true)
  }

  // 打开添加对话框
  const openAddDialog = () => {
    setFormData({ name: '', url: '', description: '', category: '' })
    setFormErrors({})
    setIsAddDialogOpen(true)
  }

  // 一键导入预设源（6官方 + 4 RSSHub模板）
  const handleImportPresets = async () => {
    if (!confirm('将导入 6 个官方源 + 4 个 RSSHub 模板，是否继续？')) return

    try {
      setImportingPresets(true)
      const response = await fetch(`${API_URL}/api/rss-sources/import-presets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          include_official: true,
          include_rsshub: true,
          reactivate_existing: true,
        })
      })

      const data = await response.json()
      if (response.ok && data.success) {
        alert(data.message || '预设源导入成功')
        await fetchSources()
      } else {
        alert(data.detail || data.message || '导入失败')
      }
    } catch (error) {
      alert('导入失败，请稍后重试')
    } finally {
      setImportingPresets(false)
    }
  }

  // 使用推荐源
  const useRecommendedSource = (source: typeof RECOMMENDED_SOURCES[0]) => {
    setFormData({
      name: source.name,
      url: source.url,
      description: source.description,
      category: source.category
    })
    setFormErrors({})
  }

  // 格式化日期
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '从未'
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 获取状态徽章
  const getStatusBadge = (source: RssSource) => {
    if (!source.is_active) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-gray-600 text-xs">
          <XCircle size={12} />
          已禁用
        </span>
      )
    }
    if (source.last_error) {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 text-red-600 text-xs">
          <AlertCircle size={12} />
          异常
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-600 text-xs">
        <CheckCircle size={12} />
        正常
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-[#0F1117] text-white p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={() => router.push('/settings')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            返回
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-white">RSS源管理</h1>
            <p className="text-gray-500 text-sm mt-1">
              管理自定义RSS新闻源
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            className="border-gray-700 text-gray-300 hover:bg-gray-800"
            onClick={handleImportPresets}
            disabled={importingPresets}
          >
            {importingPresets ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                导入中...
              </>
            ) : (
              <>
                <Rss className="w-4 h-4 mr-2" />
                一键导入预设
              </>
            )}
          </Button>

          <Button
            className="bg-blue-600 hover:bg-blue-700 text-white"
            onClick={openAddDialog}
          >
            <Plus className="w-4 h-4 mr-2" />
            添加源
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：RSS源列表 */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Rss className="w-5 h-5 text-blue-400" />
                  <CardTitle className="text-base font-medium text-gray-300">自定义RSS源</CardTitle>
                </div>
                <span className="text-sm text-gray-500">
                  共 {sources.length} 个源
                </span>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {loading ? (
                <div className="text-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-4" />
                  <p className="text-gray-500">加载中...</p>
                </div>
              ) : sources.length === 0 ? (
                <div className="text-center py-12">
                  <Rss className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-400 mb-2">还没有自定义RSS源</h3>
                  <p className="text-sm text-gray-600 mb-4">添加RSS源以获取更多新闻内容</p>
                  <Button
                    variant="outline"
                    className="border-gray-700 text-gray-300 hover:bg-gray-800"
                    onClick={openAddDialog}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    添加第一个源
                  </Button>
                </div>
              ) : (
                <div className="divide-y divide-gray-800">
                  {sources.map((source) => (
                    <div
                      key={source.id}
                      className="p-4 hover:bg-white/5 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0 mr-4">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="text-sm font-medium text-white truncate">
                              {source.name}
                            </h4>
                            {getStatusBadge(source)}
                            {source.category && (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-xs">
                                <Tag size={10} />
                                {source.category}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-500 mb-2 truncate">
                            {source.url}
                          </p>
                          {source.description && (
                            <p className="text-xs text-gray-600 mb-2">
                              {source.description}
                            </p>
                          )}
                          <div className="flex items-center gap-4 text-xs text-gray-600">
                            <span className="flex items-center gap-1">
                              <BarChart3 size={12} />
                              已抓取 {source.fetch_count} 次
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock size={12} />
                              最后更新: {formatDate(source.last_fetched_at)}
                            </span>
                          </div>
                          {source.last_error && (
                            <p className="text-xs text-red-400 mt-2">
                              错误: {source.last_error}
                            </p>
                          )}
                          {testResults[source.id] && (
                            <div className="mt-2 p-2 bg-gray-800 rounded text-xs">
                              <p className={testResults[source.id].success ? 'text-green-400' : 'text-red-400'}>
                                测试结果: {testResults[source.id].message}
                              </p>
                              {testResults[source.id].sample_entries && testResults[source.id].sample_entries.length > 0 && (
                                <div className="mt-1 text-gray-500">
                                  <p>示例条目:</p>
                                  {testResults[source.id].sample_entries.map((entry: any, idx: number) => (
                                    <p key={idx} className="truncate">- {entry.title}</p>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-gray-500 hover:text-blue-400"
                            onClick={() => handleFetchFromSource(source.id)}
                            disabled={refreshing === source.id || !source.is_active}
                            title="抓取新闻"
                          >
                            {refreshing === source.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <RefreshCw className="w-4 h-4" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-gray-500 hover:text-green-400"
                            onClick={() => handleTestSource(source.id)}
                            disabled={testing === source.id}
                            title="测试源"
                          >
                            {testing === source.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <CheckCircle className="w-4 h-4" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-gray-500 hover:text-white"
                            onClick={() => openEditDialog(source)}
                            title="编辑"
                          >
                            <Edit3 className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-gray-500 hover:text-red-400"
                            onClick={() => handleDeleteSource(source.id)}
                            disabled={deleting === source.id}
                            title="删除"
                          >
                            {deleting === source.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* 右侧：推荐源 */}
        <div className="space-y-4">
          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-4">
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-green-400" />
                <CardTitle className="text-base font-medium text-gray-300">推荐RSS源</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {RECOMMENDED_SOURCES.map((source, index) => (
                <div
                  key={index}
                  className="p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                  onClick={() => {
                    useRecommendedSource(source)
                    setIsAddDialogOpen(true)
                  }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-white">{source.name}</h4>
                    <span className="text-xs text-blue-400">{source.category}</span>
                  </div>
                  <p className="text-xs text-gray-500">{source.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-4">
              <div className="flex items-center gap-2">
                <Rss className="w-5 h-5 text-blue-400" />
                <CardTitle className="text-base font-medium text-gray-300">RSSHub模板</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {RSSHUB_ROUTE_TEMPLATES.map((source, index) => (
                <div
                  key={index}
                  className="p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
                  onClick={() => {
                    useRecommendedSource(source)
                    setIsAddDialogOpen(true)
                  }}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-white">{source.name}</h4>
                    <span className="text-xs text-blue-400">{source.category}</span>
                  </div>
                  <p className="text-xs text-gray-500">{source.url}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="bg-[#1A1D24] border-gray-800">
            <CardHeader className="py-4">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-yellow-400" />
                <CardTitle className="text-base font-medium text-gray-300">使用提示</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="text-sm text-gray-500 space-y-2">
              <p>• 地址支持 http(s)://、rsshub://、/route 三种格式</p>
              <p>• 建议先测试再抓取新闻</p>
              <p>• 抓取的新闻会进入新闻库</p>
              <p>• 可在热点监控中查看抓取的新闻</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 添加RSS源对话框 */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="bg-[#1A1D24] border-gray-800 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-400" />
              添加RSS源
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">源名称 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：阮一峰的网络日志"
                className="bg-gray-800 border-gray-700 text-white"
              />
              {formErrors.name && (
                <p className="text-xs text-red-400">{formErrors.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="url">RSS地址 *</Label>
              <Input
                id="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://example.com/feed.xml 或 /ithome/rss"
                className="bg-gray-800 border-gray-700 text-white"
              />
              {formErrors.url && (
                <p className="text-xs text-red-400">{formErrors.url}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="category">分类</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                  <SelectValue placeholder="选择分类" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {PRESET_CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat} className="text-white">
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">描述</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="简要描述这个RSS源的内容..."
                className="bg-gray-800 border-gray-700 text-white min-h-[80px]"
              />
            </div>
            {formErrors.submit && (
              <p className="text-sm text-red-400">{formErrors.submit}</p>
            )}
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" className="border-gray-700 text-gray-300 hover:bg-gray-800">
                取消
              </Button>
            </DialogClose>
            <Button
              onClick={handleAddSource}
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  添加中...
                </>
              ) : (
                '添加'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑RSS源对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="bg-[#1A1D24] border-gray-800 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Edit3 className="w-5 h-5 text-blue-400" />
              编辑RSS源
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">源名称 *</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-gray-800 border-gray-700 text-white"
              />
              {formErrors.name && (
                <p className="text-xs text-red-400">{formErrors.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-url">RSS地址 *</Label>
              <Input
                id="edit-url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://example.com/feed.xml 或 /ithome/rss"
                className="bg-gray-800 border-gray-700 text-white"
              />
              {formErrors.url && (
                <p className="text-xs text-red-400">{formErrors.url}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-category">分类</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger className="bg-gray-800 border-gray-700 text-white">
                  <SelectValue placeholder="选择分类" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 border-gray-700">
                  {PRESET_CATEGORIES.map((cat) => (
                    <SelectItem key={cat} value={cat} className="text-white">
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">描述</Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="bg-gray-800 border-gray-700 text-white min-h-[80px]"
              />
            </div>
            {formErrors.submit && (
              <p className="text-sm text-red-400">{formErrors.submit}</p>
            )}
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" className="border-gray-700 text-gray-300 hover:bg-gray-800">
                取消
              </Button>
            </DialogClose>
            <Button
              onClick={handleUpdateSource}
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  保存中...
                </>
              ) : (
                '保存'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
