'use client'

import { useState } from 'react'
import { 
  Send, 
  Save, 
  Eye, 
  RefreshCw,
  Calendar,
  Clock,
  CheckCircle,
  Loader2,
  Image as ImageIcon,
  Type,
  Layout,
  Copy,
  Wand2,
  FileText,
  Check,
  ArrowRight,
  Smartphone,
  BarChart3,
  Users,
  ArrowUpRight,
  Play
} from 'lucide-react'
import { useStore } from '@/lib/store'

export default function EditorPage() {
  const { addNotification, currentArticle, setCurrentArticle } = useStore()
  const [selectedAccount, setSelectedAccount] = useState('tech')
  const [publishMode, setPublishMode] = useState('immediate')
  const [publishTime, setPublishTime] = useState('2026-01-09T10:00')
  const [isPublishing, setIsPublishing] = useState(false)
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [isCopying, setIsCopying] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [currentStep, setCurrentStep] = useState(4)
  const [showMobilePreview, setShowMobilePreview] = useState(false)
  const [publishProgress, setPublishProgress] = useState(0)
  const [publishStatus, setPublishStatus] = useState<any[]>([
    { step: 'cover', label: '封面图上传', status: 'success' },
    { step: 'images', label: '正文图片上传', status: 'success' },
    { step: 'format', label: 'HTML格式转换', status: 'success' },
    { step: 'draft', label: '创建草稿', status: 'pending' },
  ])

  const accounts = [
    { id: 'tech', name: '科技前沿', avatar: '🚀' },
    { id: 'ai', name: 'AI观察', avatar: '🤖' },
    { id: 'design', name: '设计美学', avatar: '🎨' },
  ]

  const [article, setArticle] = useState({
    title: 'GPT-4o发布：AI推理能力的新突破',
    author: 'AI写作助手',
    digest: '本文深入分析GPT-4o的技术特性、性能表现和应用场景，帮助读者全面了解这一突破性AI模型。',
    content: `## 引言

2024年5月，OpenAI发布了备受期待的GPT-4o模型，在推理能力上实现重大突破。

## GPT-4o的核心技术特性

### 1. 增强的推理引擎

GPT-4o采用了全新的推理引擎架构，通过多层次的思维链机制，显著提升了复杂问题的解决能力。

### 2. 优化的注意力机制

新的注意力机制设计使得模型能够更有效地处理长文本，上下文窗口扩展至128K tokens。

## 性能表现

在多项基准测试中，GPT-4o的表现都超越了前代模型：

- **MMLU**: 89.2%
- **HumanEval**: 92.5%
- **GSM8K**: 94.8%

## 总结

GPT-4o的发布标志着AI技术又迈出了重要一步。`,
    coverImage: 'https://via.placeholder.com/900x383',
    coverImageMediaId: 'media_123',
    needOpenComment: true,
    onlyFansCanComment: false,
  })

  const handlePublish = async () => {
    setIsPublishing(true)
    setPublishProgress(0)
    addNotification('开始发布...', 'info')
    
    try {
      // 模拟发布流程
      const steps = ['cover', 'images', 'format', 'draft']
      for (let i = 0; i < steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        setPublishProgress(((i + 1) / steps.length) * 100)
        setPublishStatus(prev => prev.map(s => 
          s.step === steps[i] ? { ...s, status: 'loading' } : s
        ))
        await new Promise(resolve => setTimeout(resolve, 500))
        setPublishStatus(prev => prev.map(s => 
          s.step === steps[i] ? { ...s, status: 'success' } : s
        ))
      }
      
      addNotification('发布成功！', 'success')
    } catch (error) {
      addNotification('发布失败', 'error')
      setPublishStatus(prev => prev.map(s => 
        s.step === 'draft' ? { ...s, status: 'pending' } : s
      ))
    } finally {
      setIsPublishing(false)
    }
  }

  const handleSaveDraft = async () => {
    setIsSaving(true)
    addNotification('正在保存草稿...', 'info')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      addNotification('草稿已保存', 'success')
    } catch (error) {
      addNotification('保存失败', 'error')
    } finally {
      setIsSaving(false)
    }
  }

  const handlePreview = () => {
    setShowMobilePreview(true)
    addNotification('手机预览模式已开启', 'info')
  }

  const handleCopy = async () => {
    setIsCopying(true)
    addNotification('正在复制内容...', 'info')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
      await navigator.clipboard.writeText(article.content)
      addNotification('内容已复制到剪贴板', 'success')
    } catch (error) {
      addNotification('复制失败', 'error')
    } finally {
      setIsCopying(false)
    }
  }

  const handleOptimize = async () => {
    setIsOptimizing(true)
    addNotification('正在优化内容...', 'info')
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      addNotification('内容优化完成', 'success')
    } catch (error) {
      addNotification('优化失败', 'error')
    } finally {
      setIsOptimizing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={16} className="text-green-500" />
      case 'pending':
        return <Clock size={16} className="text-yellow-500" />
      case 'loading':
        return <Loader2 size={16} className="text-blue-500 animate-spin" />
      default:
        return <Clock size={16} className="text-muted-foreground" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] bg-clip-text text-transparent">微信发布</h1>
          <p className="text-gray-600 mt-1">发布文章到微信公众号</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => window.location.href = '/statistics'}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 transition-colors text-gray-700 font-medium"
          >
            <BarChart3 size={20} />
            数据分析
          </button>
          <button
            onClick={handlePreview}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white border border-gray-300 hover:bg-gray-100 transition-colors text-gray-700 font-medium"
          >
            <Smartphone size={20} />
            手机预览
          </button>
          <button
            onClick={handleSaveDraft}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 transition-colors text-gray-700 font-medium disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                保存中...
              </>
            ) : (
              <>
                <Save size={20} />
                保存草稿
              </>
            )}
          </button>
          <button
            onClick={handlePublish}
            disabled={isPublishing}
            className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300 font-medium disabled:opacity-50"
          >
            {isPublishing ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                发布中...
              </>
            ) : (
              <>
                <Send size={20} />
                直接发布
              </>
            )}
          </button>
        </div>
      </div>

      {/* Account Tabs */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 p-4">
        <div className="flex items-center gap-2 overflow-x-auto">
          {accounts.map((account) => (
            <button
              key={account.id}
              onClick={() => setSelectedAccount(account.id)}
              className={`flex items-center gap-3 px-5 py-3 rounded-xl transition-all duration-300 flex-shrink-0 ${
                selectedAccount === account.id
                  ? 'bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white shadow-lg'
                  : 'bg-white hover:bg-gray-100 text-gray-700 border border-gray-200'
              }`}
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-xl">
                {account.avatar}
              </div>
              <span className="font-semibold">{account.name}</span>
              {selectedAccount === account.id && (
                <Check size={18} className="ml-1" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Publish Progress */}
      {isPublishing && (
        <div className="bg-gradient-to-r from-[#5a6e5c]/10 to-[#4a5e4c]/10 rounded-2xl border border-[#5a6e5c]/20 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Loader2 size={24} className="text-[#5a6e5c] animate-spin" />
              <div>
                <h3 className="font-semibold text-gray-900">正在发布...</h3>
                <p className="text-sm text-gray-600">请勿关闭页面</p>
              </div>
            </div>
            <span className="text-2xl font-bold text-[#5a6e5c]">{Math.round(publishProgress)}%</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] transition-all duration-500"
              style={{ width: `${publishProgress}%` }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Article Preview - WeChat Style */}
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">文章预览</h2>
              <p className="text-sm text-gray-500 mt-1">模拟微信公众号排版效果</p>
            </div>
            
            {/* WeChat Preview Container */}
            <div className="p-8 bg-[#f5f5f5]">
              {/* Cover Image */}
              <div className="mb-6">
                <div className="relative aspect-[2.35:1] rounded-lg overflow-hidden bg-gradient-to-br from-gray-200 to-gray-300 shadow-md">
                  <img
                    src={article.coverImage}
                    alt="封面"
                    className="w-full h-full object-cover"
                  />
                  <button className="absolute top-3 right-3 p-2 rounded-lg bg-black/50 hover:bg-black/70 transition-colors">
                    <ImageIcon size={20} className="text-white" />
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-500 text-center">
                  尺寸: 900x383 (2.35:1) | Media ID: {article.coverImageMediaId}
                </div>
              </div>

              {/* Title */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">标题</label>
                <input
                  type="text"
                  value={article.title}
                  onChange={(e) => setArticle({ ...article, title: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg bg-white border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all text-gray-900 font-medium"
                />
              </div>

              {/* Author */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">作者</label>
                <input
                  type="text"
                  value={article.author}
                  onChange={(e) => setArticle({ ...article, author: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg bg-white border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all text-gray-900"
                />
              </div>

              {/* Digest */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">摘要</label>
                <textarea
                  value={article.digest}
                  onChange={(e) => setArticle({ ...article, digest: e.target.value })}
                  className="w-full h-24 px-4 py-3 rounded-lg bg-white border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all resize-none text-gray-700"
                />
              </div>

              {/* Content Editor */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">正文内容</label>
                <div className="bg-white rounded-xl border border-gray-300 overflow-hidden shadow-sm">
                  {/* Toolbar */}
                  <div className="flex items-center gap-1.5 p-2.5 bg-gray-50 border-b border-gray-300">
                    <button className="p-2 rounded hover:bg-gray-200 transition-colors">
                      <Type size={18} className="text-gray-600" />
                    </button>
                    <button className="p-2 rounded hover:bg-gray-200 transition-colors">
                      <Layout size={18} className="text-gray-600" />
                    </button>
                    <button className="p-2 rounded hover:bg-gray-200 transition-colors">
                      <ImageIcon size={18} className="text-gray-600" />
                    </button>
                    <div className="w-px h-6 bg-gray-300 mx-1" />
                    <button className="p-2 rounded hover:bg-gray-200 transition-colors">
                      <Copy size={18} className="text-gray-600" />
                    </button>
                    <button className="p-2 rounded hover:bg-gray-200 transition-colors">
                      <RefreshCw size={18} className="text-gray-600" />
                    </button>
                  </div>
                  
                  {/* Editor */}
                  <textarea
                    value={article.content}
                    onChange={(e) => setArticle({ ...article, content: e.target.value })}
                    className="w-full h-80 px-4 py-3 focus:outline-none resize-none font-mono text-sm text-gray-700 leading-relaxed"
                  />
                  
                  {/* Bottom Actions */}
                  <div className="flex items-center gap-2 p-3 bg-gray-50 border-t border-gray-300">
                    <button
                      onClick={handleCopy}
                      disabled={isCopying}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-gray-300 hover:bg-gray-200 transition-colors text-gray-700 font-medium disabled:opacity-50"
                    >
                      {isCopying ? (
                        <>
                          <Loader2 size={18} className="animate-spin" />
                          复制中...
                        </>
                      ) : (
                        <>
                          <Copy size={18} />
                          复制
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleOptimize}
                      disabled={isOptimizing}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all duration-300 font-medium disabled:opacity-50"
                    >
                      {isOptimizing ? (
                        <>
                          <Loader2 size={18} className="animate-spin" />
                          优化中...
                        </>
                      ) : (
                        <>
                          <Wand2 size={18} />
                          优化内容
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Publish Options - Card Style */}
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-6 text-gray-900">发布选项</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-700">发布方式</label>
                <div className="grid grid-cols-1 gap-3">
                  <button
                    onClick={() => {
                      setPublishMode('immediate')
                      addNotification('已选择立即发布', 'info')
                    }}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      publishMode === 'immediate'
                        ? 'border-[#5a6e5c] bg-[#5a6e5c]/10'
                        : 'border-gray-200 hover:border-[#5a6e5c]/50 hover:bg-gray-50'
                    }`}
                  >
                    <div className={`p-2.5 rounded-lg ${
                      publishMode === 'immediate' ? 'bg-[#5a6e5c]' : 'bg-gray-200'
                    }`}>
                      <Send size={20} className={publishMode === 'immediate' ? 'text-white' : 'text-gray-600'} />
                    </div>
                    <div className="text-left">
                      <span className="font-semibold text-gray-900 block">立即发布</span>
                      <span className="text-xs text-gray-500">直接发布到公众号</span>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => {
                      setPublishMode('draft')
                      addNotification('已选择保存草稿', 'info')
                    }}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      publishMode === 'draft'
                        ? 'border-[#5a6e5c] bg-[#5a6e5c]/10'
                        : 'border-gray-200 hover:border-[#5a6e5c]/50 hover:bg-gray-50'
                    }`}
                  >
                    <div className={`p-2.5 rounded-lg ${
                      publishMode === 'draft' ? 'bg-[#5a6e5c]' : 'bg-gray-200'
                    }`}>
                      <FileText size={20} className={publishMode === 'draft' ? 'text-white' : 'text-gray-600'} />
                    </div>
                    <div className="text-left">
                      <span className="font-semibold text-gray-900 block">保存草稿</span>
                      <span className="text-xs text-gray-500">保存到草稿箱</span>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => {
                      setPublishMode('scheduled')
                      addNotification('已选择定时发布', 'info')
                    }}
                    className={`flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                      publishMode === 'scheduled'
                        ? 'border-[#5a6e5c] bg-[#5a6e5c]/10'
                        : 'border-gray-200 hover:border-[#5a6e5c]/50 hover:bg-gray-50'
                    }`}
                  >
                    <div className={`p-2.5 rounded-lg ${
                      publishMode === 'scheduled' ? 'bg-[#5a6e5c]' : 'bg-gray-200'
                    }`}>
                      <Calendar size={20} className={publishMode === 'scheduled' ? 'text-white' : 'text-gray-600'} />
                    </div>
                    <div className="text-left">
                      <span className="font-semibold text-gray-900 block">定时发布</span>
                      <span className="text-xs text-gray-500">设置发布时间</span>
                    </div>
                  </button>
                </div>
              </div>

              {publishMode === 'scheduled' && (
                <div className="p-4 rounded-xl bg-gray-50 border border-gray-200">
                  <label className="block text-sm font-medium mb-2 text-gray-700">发布时间</label>
                  <input
                    type="datetime-local"
                    value={publishTime}
                    onChange={(e) => setPublishTime(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg bg-white border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#5a6e5c] focus:border-transparent transition-all text-gray-900"
                  />
                  <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
                    <Clock size={14} />
                    建议选择 10:00-11:00 发布，效果最佳
                  </div>
                </div>
              )}

              <div className="pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium mb-3 text-gray-700">评论设置</label>
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <input
                      type="checkbox"
                      checked={article.needOpenComment}
                      onChange={(e) => {
                        setArticle({ ...article, needOpenComment: e.target.checked })
                        addNotification('评论设置已更新', 'info')
                      }}
                      className="w-5 h-5 rounded border-gray-300 text-[#5a6e5c] focus:ring-[#5a6e5c]"
                    />
                    <div>
                      <span className="text-gray-900 font-medium">开启评论</span>
                      <span className="text-xs text-gray-500 block">允许读者在文章下评论</span>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <input
                      type="checkbox"
                      checked={article.onlyFansCanComment}
                      onChange={(e) => {
                        setArticle({ ...article, onlyFansCanComment: e.target.checked })
                        addNotification('粉丝评论设置已更新', 'info')
                      }}
                      disabled={!article.needOpenComment}
                      className="w-5 h-5 rounded border-gray-300 text-[#5a6e5c] focus:ring-[#5a6e5c] disabled:opacity-50"
                    />
                    <div>
                      <span className="text-gray-900 font-medium">仅粉丝可评论</span>
                      <span className="text-xs text-gray-500 block">只有关注者才能评论</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Publish Status */}
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-6 text-gray-900">发布状态</h2>
            <div className="space-y-3">
              {publishStatus.map((item) => (
                <div key={item.step} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <div className="flex-shrink-0">
                    {getStatusIcon(item.status)}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{item.label}</span>
                  {item.status === 'loading' && (
                    <Loader2 size={16} className="text-[#5a6e5c] animate-spin ml-auto" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="bg-gradient-to-br from-[#5a6e5c]/10 to-[#4a5e4c]/10 rounded-2xl border border-[#5a6e5c]/20 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center gap-2">
              <Play size={20} className="text-[#5a6e5c]" />
              发布提示
            </h2>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-[#5a6e5c] mt-0.5">•</span>
                <span>封面图尺寸建议 900x383 (2.35:1)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#5a6e5c] mt-0.5">•</span>
                <span>标题长度建议 64 字以内</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#5a6e5c] mt-0.5">•</span>
                <span>摘要长度建议 120 字以内</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#5a6e5c] mt-0.5">•</span>
                <span>正文图片建议宽度 900px</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#5a6e5c] mt-0.5">•</span>
                <span>发布后无法修改正文内容</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Mobile Preview Modal */}
      {showMobilePreview && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">手机预览</h3>
              <button
                onClick={() => setShowMobilePreview(false)}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                ×
              </button>
            </div>
            <div className="p-6 bg-[#f5f5f5]">
              {/* Phone Mockup */}
              <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                {/* Cover */}
                <div className="aspect-[2.35:1] bg-gradient-to-br from-gray-200 to-gray-300">
                  <img
                    src={article.coverImage}
                    alt="封面"
                    className="w-full h-full object-cover"
                  />
                </div>
                {/* Content */}
                <div className="p-4">
                  <h4 className="text-lg font-bold text-gray-900 mb-2">{article.title}</h4>
                  <p className="text-sm text-gray-600 mb-4">{article.digest}</p>
                  <div className="text-xs text-gray-400">{article.author}</div>
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-gray-200">
              <button
                onClick={() => setShowMobilePreview(false)}
                className="w-full py-3 bg-gradient-to-r from-[#5a6e5c] to-[#4a5e4c] text-white rounded-xl font-medium hover:shadow-lg hover:shadow-[#5a6e5c]/30 transition-all"
              >
                关闭预览
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}