'use client'

import { useState, useEffect } from 'react'
import { 
  Sparkles, 
  Wand2, 
  RefreshCw, 
  Check, 
  Copy,
  Save,
  Send,
  ChevronRight,
  Loader2,
  Smartphone,
  Edit3,
  Eye
} from 'lucide-react'
import { generateTitles, generateContent, createArticle, publishToWechat, updateArticle } from '@/lib/api'
import { API_URL } from '@/lib/api'

export default function ArticleCreate() {
  const [step, setStep] = useState<'input' | 'titles' | 'content' | 'preview'>('input')
  const [isEditMode, setIsEditMode] = useState(false)
  const [editArticleId, setEditArticleId] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null)
  const [topic, setTopic] = useState('')
  const [aiModel, setAiModel] = useState('deepseek-chat')
  const [writingStyle, setWritingStyle] = useState('professional')
  const [generatedTitles, setGeneratedTitles] = useState<any[]>([])
  const [generatedContent, setGeneratedContent] = useState<any>(null)
  const [showWechatPreview, setShowWechatPreview] = useState(false)
  const [editingContent, setEditingContent] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [savedArticleId, setSavedArticleId] = useState<number | null>(null)

  // 检查是否为编辑模式
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const editId = params.get('editId')
    if (editId) {
      setIsEditMode(true)
      setEditArticleId(parseInt(editId))
      loadArticle(parseInt(editId))
    }
  }, [])

  // 加载现有文章数据
  const loadArticle = async (articleId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/articles/${articleId}`)
      if (response.ok) {
        const article = await response.json()
        setTopic(article.title)
        setEditingContent(article.content)
        setGeneratedContent({
          content: article.content,
          summary: article.summary,
          word_count: article.content?.length || 0
        })
        setSelectedTitle(article.title)
        setSavedArticleId(articleId)
        setStep('content')
      }
    } catch (error) {
      console.error('加载文章失败:', error)
    }
  }
  
  // 图片生成配置
  const [generateCoverImage, setGenerateCoverImage] = useState(true)
  const [imageProvider, setImageProvider] = useState('cogview')
  const [imageStyle, setImageStyle] = useState('professional')

  const steps = [
    { id: 'input', name: '输入主题', icon: '✍️' },
    { id: 'titles', name: '选择标题', icon: '📝' },
    { id: 'content', name: '生成内容', icon: '✨' },
    { id: 'preview', name: '预览发布', icon: '👀' }
  ]

  const aiModels = [
    { id: 'deepseek-chat', name: 'DeepSeek', description: '开源性能王者', icon: '🚀', borderColor: 'border-orange-400', bgColor: 'bg-orange-50' },
    { id: 'gpt-4-turbo-preview', name: 'GPT-4', description: 'OpenAI最强模型', icon: '🧠', borderColor: 'border-blue-400', bgColor: 'bg-blue-50' },
    { id: 'claude-3-opus-20240229', name: 'Claude 3.5', description: 'Anthropic长文本专家', icon: '🎭', borderColor: 'border-purple-400', bgColor: 'bg-purple-50' },
    { id: 'gemini-pro', name: 'Gemini Pro', description: 'Google多模态模型', icon: '✨', borderColor: 'border-green-400', bgColor: 'bg-green-50' },
    { id: 'glm-4-flash', name: 'GLM-4 Flash', description: '智谱AI超快响应', icon: '🔮', borderColor: 'border-pink-400', bgColor: 'bg-pink-50' },
  ]

  const writingStyles = [
    { 
      id: 'professional', 
      name: '专业解读', 
      description: '深度分析，数据支撑，适合行业洞察',
      example: '根据最新数据显示...',
      color: 'from-indigo-500 to-blue-500',
      icon: '📊',
      tags: ['10w+', '深度']
    },
    { 
      id: 'casual', 
      name: '轻松聊天', 
      description: '像朋友一样自然交流，降低阅读门槛',
      example: '最近发现一个有趣的现象...',
      color: 'from-green-500 to-emerald-500',
      icon: '💬',
      tags: ['易读', '亲和']
    },
    { 
      id: 'story', 
      name: '故事共鸣', 
      description: '用真实案例打动人心，引发情感共鸣',
      example: '去年这个时候，我遇到了...',
      color: 'from-orange-500 to-red-500',
      icon: '📖',
      tags: ['情感', '共鸣']
    },
    { 
      id: 'opinion', 
      name: '犀利观点', 
      description: '独到见解，敢于表达，引发讨论',
      example: '说实话，我不太认同...',
      color: 'from-purple-500 to-pink-500',
      icon: '⚡',
      tags: ['爆款', '争议']
    },
    { 
      id: 'trend', 
      name: '热点追踪', 
      description: '紧跟时事，快速解读，抓住流量风口',
      example: '刚刚发生的这件事引发热议...',
      color: 'from-blue-500 to-cyan-500',
      icon: '🔥',
      tags: ['时效', '流量']
    },
    { 
      id: 'dry_goods', 
      name: '干货教程', 
      description: '步骤清晰，实用可操作，收藏率高',
      example: '只需要3步，就能掌握...',
      color: 'from-amber-500 to-orange-500',
      icon: '📚',
      tags: ['实用', '收藏']
    },
    { 
      id: 'gold_sentence', 
      name: '金句开头', 
      description: '用金句或反常识开场，吸引注意力',
      example: '90%的人都不知道的是...',
      color: 'from-yellow-500 to-amber-500',
      icon: '✨',
      tags: ['吸睛', '好奇']
    },
    { 
      id: 'qa_format', 
      name: '问答互动', 
      description: 'Q&A形式，解答痛点，互动性强',
      example: 'Q: 为什么总是... A: 因为...',
      color: 'from-teal-500 to-cyan-500',
      icon: '❓',
      tags: ['互动', '解惑']
    },
  ]

  const imageProviders = [
    { id: 'cogview', name: 'Cogview-3-Flash', description: '智谱AI快速生成', icon: '🎨', borderColor: 'border-pink-400', bgColor: 'bg-pink-50' },
    { id: 'dalle', name: 'DALL-E 3', description: 'OpenAI专业模型', icon: '🖼️', borderColor: 'border-blue-400', bgColor: 'bg-blue-50' },
    { id: 'midjourney', name: 'Midjourney', description: '艺术创作首选', icon: '🎭', borderColor: 'border-purple-400', bgColor: 'bg-purple-50' },
    { id: 'stable-diffusion', name: 'Stable Diffusion', description: '开源灵活选择', icon: '🌊', borderColor: 'border-green-400', bgColor: 'bg-green-50' },
  ]

  const handleGenerateTitles = async () => {
    setIsGenerating(true)
    try {
      // 调用真实API生成标题
      const titles = await generateTitles(topic, 5, aiModel)
      setGeneratedTitles(titles.map((t: any, index: number) => ({
        id: index + 1,
        title: t.title,
        predictedClickRate: Math.round(t.click_rate)
      })))
      setStep('titles')
    } catch (error: any) {
      console.error('生成标题失败:', error)
      // 降级方案：使用模拟数据
      console.log('使用模拟标题数据')
      setGeneratedTitles([
        { id: 1, title: `${topic}：深入解析与实践指南`, predictedClickRate: 92 },
        { id: 2, title: `如何有效${topic}？专家分享3个关键技巧`, predictedClickRate: 88 },
        { id: 3, title: `${topic}的完整方法论：从入门到精通`, predictedClickRate: 85 },
        { id: 4, title: `90%的人都不知道的${topic}秘诀`, predictedClickRate: 90 },
        { id: 5, title: `${topic}：2024年最新发展趋势与前景`, predictedClickRate: 82 }
      ])
      setStep('titles')
      // 提示用户
      if (confirm('AI API 暂时不可用，已生成模拟标题用于测试。是否继续？')) {
        setStep('titles')
      } else {
        setIsGenerating(false)
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSelectTitle = (title: string) => {
    setSelectedTitle(title)
    setStep('content')
  }

  const handleGenerateContent = async () => {
    setIsGenerating(true)
    try {
      // 调用真实API生成内容，传递选择的写作风格
      const content = await generateContent(topic, selectedTitle || '', writingStyle, 'medium', aiModel)
      setGeneratedContent({
        title: selectedTitle,
        summary: content.summary,
        content: content.content,
        qualityScore: Math.round(content.quality_score),
        sources: content.seo_data?.keywords || ['AI生成'],
      })
      setEditingContent(content.content)
      setStep('preview')
    } catch (error: any) {
      console.error('生成内容失败:', error)
      // 降级方案：使用模拟内容
      console.log('使用模拟内容数据')
      const mockContent = `# ${selectedTitle}

## 引言
${topic}是一个备受关注的话题，在当今时代具有重要的意义。本文将深入探讨${topic}的各个方面，帮助读者更好地理解和应用相关知识。

## 核心要点

### 1. 基本概念
${topic}作为${writingStyle === 'professional' ? '专业领域' : '日常生活中'}的重要组成部分，其核心价值在于解决实际问题。通过深入理解其基本原理，我们可以更好地运用相关方法。

### 2. 实践应用
在实际应用中，${topic}需要结合具体情况灵活运用。以下是几个关键要点：

- 要点一：明确目标，制定合理的实施计划
- 要点二：注重细节，确保每个环节都得到充分重视
- 要点三：持续优化，根据反馈不断改进

### 3. 常见问题与解决方案
在实践过程中，可能会遇到各种挑战。以下是一些常见问题及其解决方案：

**问题一**：如何快速上手？
**解决方案**：从基础开始，逐步深入，同时结合实际案例进行练习。

**问题二**：如何提高效率？
**解决方案**：合理分配时间，优先处理重要任务，善用工具和方法。

## 总结
${topic}是一个值得深入研究的领域。通过本文的介绍，希望读者能够对其有更清晰的认识，并在实践中取得更好的效果。`

      setGeneratedContent({
        title: selectedTitle,
        summary: `本文深入探讨了${topic}的核心概念、实践应用和常见问题，为读者提供了全面的指导。`,
        content: mockContent,
        qualityScore: 85,
        sources: ['模拟数据', 'AI生成'],
      })
      setEditingContent(mockContent)
      setStep('preview')
      // 提示用户
      if (confirm('AI API 暂时不可用，已生成模拟内容用于测试。是否继续？')) {
        setStep('preview')
      } else {
        setIsGenerating(false)
      }
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveDraft = async () => {
    if (!generatedContent) return
    setIsSaving(true)
    try {
      let article
      if (isEditMode && editArticleId) {
        // 编辑模式：更新现有文章
        article = await updateArticle(editArticleId, {
          title: generatedContent.title,
          content: editingContent,
          summary: generatedContent.summary,
          source_topic: topic,
          status: 'draft',
          tags: generatedContent.sources || [],
        })
        alert('文章更新成功！')
      } else {
        // 创建模式：创建新文章
        article = await createArticle({
          title: generatedContent.title,
          content: editingContent,
          summary: generatedContent.summary,
          source_topic: topic,
          status: 'draft',
          tags: generatedContent.sources || [],
          generate_cover_image: generateCoverImage,
          image_provider: imageProvider,
          image_style: imageStyle,
        })
        setSavedArticleId(article.id)
        alert('草稿保存成功！')
      }
    } catch (error: any) {
      console.error('保存草稿失败:', error)
      alert('保存失败：' + (error.message || '请稍后重试'))
    } finally {
      setIsSaving(false)
    }
  }

  const handlePublish = async () => {
    if (!generatedContent) return
    setIsSaving(true)
    try {
      let article
      if (isEditMode && editArticleId) {
        // 编辑模式：更新现有文章
        article = await updateArticle(editArticleId, {
          title: generatedContent.title,
          content: editingContent,
          summary: generatedContent.summary,
          source_topic: topic,
          status: 'ready',
          tags: generatedContent.sources || [],
        })
      } else {
        // 创建模式：创建新文章
        article = await createArticle({
          title: generatedContent.title,
          content: editingContent,
          summary: generatedContent.summary,
          source_topic: topic,
          status: 'draft',
          tags: generatedContent.sources || [],
          generate_cover_image: generateCoverImage,
          image_provider: imageProvider,
          image_style: imageStyle,
        })
        setSavedArticleId(article.id)
      }

      // 第二步：发布到微信草稿箱
      try {
        const wechatResult = await publishToWechat({
          title: generatedContent.title,
          content: editingContent,
          digest: generatedContent.summary,
          author: 'AI助手',
        })

        // 更新文章状态为已发布
        await updateArticle(article.id, {
          status: 'published',
          wechat_draft_id: wechatResult.draft_id,
        })

        alert('文章已成功发布到微信草稿箱！')
      } catch (wechatError: any) {
        console.error('发布到微信失败:', wechatError)
        alert('草稿已保存到数据库，但发布到微信失败：' + (wechatError.message || '请检查微信配置'))
      }
    } catch (error: any) {
      console.error('发布文章失败:', error)
      alert('发布失败：' + (error.message || '请稍后重试'))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold art-gradient-text">
            {isEditMode ? '编辑文章' : 'AI写作'}
          </h1>
          <p className="text-slate-600 mt-1">
            {isEditMode ? '修改现有文章内容' : '使用AI快速生成高质量内容'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700">
            <Save size={20} />
            保存草稿
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300">
            <Send size={20} />
            直接发布
          </button>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center gap-4 p-4 bg-white/95 backdrop-blur-xl rounded-2xl border border-slate-200 shadow-sm">
        {[
          { id: 'input', label: '输入主题' },
          { id: 'titles', label: '选择标题' },
          { id: 'content', label: '生成内容' },
          { id: 'preview', label: '预览编辑' },
        ].map((s, index) => (
          <div key={s.id} className="flex-1 flex items-center gap-4">
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
              step === s.id ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30' :
              ['input', 'titles', 'content', 'preview'].indexOf(step) > index ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
            }`}>
              {['input', 'titles', 'content', 'preview'].indexOf(step) > index ? <Check size={16} /> : index + 1}
            </div>
            <span className={`font-medium ${step === s.id ? 'text-indigo-600' : 'text-slate-500'}`}>
              {s.label}
            </span>
            {index < 3 && <ChevronRight size={20} className="text-slate-400" />}
          </div>
        ))}
      </div>

      {/* Step 1: Input Topic */}
      {step === 'input' && (
        <div className="bg-gradient-to-br from-[#f0f9f4]/90 via-white/90 to-[#f5f0ff]/90 backdrop-blur-xl rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
          <div>
            <label className="block text-sm font-medium mb-3 text-slate-700">选择AI模型</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {aiModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => setAiModel(model.id)}
                  className={`p-4 rounded-xl border-2 transition-all hover:scale-102 ${
                    aiModel === model.id 
                      ? `${model.borderColor} ${model.bgColor} shadow-lg shadow-indigo-500/10` 
                      : 'border-slate-200 hover:border-indigo-300 bg-white'
                  }`}
                >
                  <div className="text-2xl mb-2">{model.icon}</div>
                  <div className="font-medium mb-1 text-slate-900">{model.name}</div>
                  <div className="text-xs text-slate-500">{model.description}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3 text-slate-700">输入主题/关键词</label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="例如：AI大模型最新进展分析"
              className="w-full h-32 p-4 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none text-slate-800 placeholder-slate-400"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-medium text-slate-700">写作风格</label>
              <span className="text-xs text-slate-500">选择适合目标读者的风格</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {writingStyles.map((style) => (
                <button
                  key={style.id}
                  type="button"
                  onClick={() => setWritingStyle(style.id)}
                  className={`writing-style-btn p-4 rounded-xl border-2 transition-all text-left group cursor-pointer ${
                    writingStyle === style.id
                      ? `border-indigo-400 bg-gradient-to-r ${style.color} bg-opacity-10 shadow-lg pointer-events-auto`
                      : 'border-slate-200 hover:border-indigo-300 bg-white hover:shadow-md pointer-events-auto'
                  }`}
                  style={{ pointerEvents: 'auto' }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{style.icon}</span>
                      <div className="font-medium text-slate-900">{style.name}</div>
                    </div>
                    <div className="flex gap-1">
                      {style.tags?.map((tag, idx) => (
                        <span 
                          key={idx} 
                          className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                            writingStyle === style.id 
                              ? 'bg-white/80 text-indigo-600' 
                              : 'bg-indigo-50 text-indigo-500'
                          }`}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-xs text-slate-500 mb-2">{style.description}</div>
                  <div className={`text-xs italic p-2 rounded ${
                    writingStyle === style.id ? 'bg-white/60 text-slate-700' : 'bg-slate-50 text-slate-600'
                  }`}>
                    "{style.example}"
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" 
                checked={generateCoverImage}
                onChange={(e) => setGenerateCoverImage(e.target.checked)}
              />
              <span className="text-sm text-slate-700">生成技术配图</span>
            </label>
          </div>

          {generateCoverImage && (
            <div>
              <label className="block text-sm font-medium mb-3 text-slate-700">选择图片生成模型</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {imageProviders.map((provider) => (
                  <button
                    key={provider.id}
                    onClick={() => setImageProvider(provider.id)}
                    className={`p-4 rounded-xl border-2 transition-all hover:scale-102 ${
                      imageProvider === provider.id 
                        ? `${provider.borderColor} ${provider.bgColor} shadow-lg shadow-indigo-500/10` 
                        : 'border-slate-200 hover:border-indigo-300 bg-white'
                    }`}
                  >
                    <div className="text-2xl mb-2">{provider.icon}</div>
                    <div className="font-medium mb-1 text-slate-900">{provider.name}</div>
                    <div className="text-xs text-slate-500">{provider.description}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleGenerateTitles}
            disabled={!topic || isGenerating}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {isGenerating ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                生成中...
              </>
            ) : (
              <>
                <Wand2 size={20} />
                生成标题
              </>
            )}
          </button>
        </div>
      )}

      {/* Step 2: Select Title */}
      {step === 'titles' && (
        <div className="bg-gradient-to-br from-[#f0f9f4]/90 via-white/90 to-[#f5f0ff]/90 backdrop-blur-xl rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-slate-900">选择标题</h2>
            <button
              onClick={handleGenerateTitles}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700"
            >
              <RefreshCw size={20} />
              重新生成
            </button>
          </div>

          <div className="space-y-4">
            {generatedTitles.map((item) => (
              <button
                key={item.id}
                onClick={() => handleSelectTitle(item.title)}
                className="w-full p-4 rounded-xl border-2 border-slate-200 hover:border-indigo-300 transition-all text-left group bg-white hover:scale-102"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="font-medium mb-2 text-slate-900 group-hover:text-indigo-600 transition-colors">
                      {item.title}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-slate-500">
                      <Sparkles size={16} className="text-indigo-500" />
                      预测点击率: {item.predictedClickRate}%
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    item.predictedClickRate >= 80 ? 'bg-emerald-100 text-emerald-700' :
                    item.predictedClickRate >= 70 ? 'bg-amber-100 text-amber-700' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {item.predictedClickRate >= 80 ? '优秀' :
                     item.predictedClickRate >= 70 ? '良好' : '一般'}
                  </div>
                </div>
              </button>
            ))}
          </div>

          <button
            onClick={() => setStep('input')}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700"
          >
            返回修改
          </button>
        </div>
      )}

      {/* Step 3: Generate Content */}
      {step === 'content' && (
        <div className="bg-gradient-to-br from-[#f0f9f4]/90 via-white/90 to-[#f5f0ff]/90 backdrop-blur-xl rounded-2xl border border-slate-200 p-6 space-y-6 shadow-sm">
          <div className="text-center py-12">
            {isGenerating ? (
              <>
                <Loader2 size={48} className="mx-auto mb-4 text-indigo-600 animate-spin" />
                <h2 className="text-xl font-semibold mb-2 text-slate-900">正在生成内容...</h2>
                <p className="text-slate-600">AI正在为您创作高质量内容，请稍候</p>
              </>
            ) : (
              <>
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 flex items-center justify-center mx-auto mb-4">
                  <Sparkles size={32} className="text-indigo-600" />
                </div>
                <h2 className="text-xl font-semibold mb-2 text-slate-900">准备就绪</h2>
                <p className="text-slate-600 mb-6">已选择标题：{selectedTitle}</p>
                <button
                  onClick={handleGenerateContent}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300"
                >
                  <Wand2 size={20} />
                  开始生成内容
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Step 4: Preview */}
      {step === 'preview' && generatedContent && (
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-[#f0f9f4]/90 via-white/90 to-[#f5f0ff]/90 backdrop-blur-xl rounded-2xl border border-slate-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900">内容预览</h2>
              <div className="flex items-center gap-2">
                <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700">
                  <Copy size={20} />
                  复制
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all duration-300">
                  <Wand2 size={20} />
                  优化内容
                </button>
              </div>
            </div>

            <div className="space-y-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">标题</label>
                <input
                  type="text"
                  value={generatedContent.title}
                  onChange={(e) => setGeneratedContent({...generatedContent, title: e.target.value})}
                  className="w-full p-3 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-slate-800"
                />
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">摘要</label>
                <textarea
                  value={generatedContent.summary}
                  onChange={(e) => setGeneratedContent({...generatedContent, summary: e.target.value})}
                  className="w-full h-24 p-3 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none text-slate-800"
                />
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">正文内容</label>
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  className="w-full h-96 p-3 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none font-mono text-sm text-slate-800"
                />
              </div>

              {/* Quality Score */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-br from-indigo-50/50 to-purple-50/50 border border-indigo-200">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-indigo-600">{generatedContent.qualityScore}</div>
                    <div className="text-sm text-slate-600">质量评分</div>
                  </div>
                  <div className="h-12 w-px bg-slate-300" />
                  <div>
                    <div className="text-sm text-slate-600 mb-1">参考来源</div>
                    <div className="flex flex-wrap gap-2">
                      {generatedContent.sources.map((source: string, index: number) => (
                        <span key={index} className="px-2 py-1 rounded bg-indigo-100 text-indigo-700 text-xs font-medium">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setStep('input')}
              disabled={isSaving}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700 disabled:opacity-50"
            >
              重新生成
            </button>
            <button
              onClick={handleSaveDraft}
              disabled={isSaving}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700 disabled:opacity-50"
            >
              {isSaving ? <Loader2 size={20} className="animate-spin" /> : <Save size={20} />}
              保存草稿
            </button>
            <button
              onClick={handlePublish}
              disabled={isSaving}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/30 transition-all duration-300 disabled:opacity-50"
            >
              {isSaving ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
              直接发布
            </button>
          </div>
        </div>
      )}
    </div>
  )
}