'use client'

import { useState } from 'react'
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

export default function ArticleCreate() {
  const [step, setStep] = useState<'input' | 'titles' | 'content' | 'preview'>('input')
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null)
  const [topic, setTopic] = useState('')
  const [aiModel, setAiModel] = useState('gpt-4')
  const [generatedTitles, setGeneratedTitles] = useState<any[]>([])
  const [generatedContent, setGeneratedContent] = useState<any>(null)
  const [showWechatPreview, setShowWechatPreview] = useState(false)
  const [editingContent, setEditingContent] = useState('')

  const aiModels = [
    { id: 'gpt-4', name: 'GPT-4', description: 'OpenAI最强模型', icon: '🧠', borderColor: 'border-blue-400', bgColor: 'bg-blue-50' },
    { id: 'claude-3.5', name: 'Claude 3.5', description: 'Anthropic长文本专家', icon: '🎭', borderColor: 'border-purple-400', bgColor: 'bg-purple-50' },
    { id: 'deepseek', name: 'DeepSeek', description: '开源性能王者', icon: '🚀', borderColor: 'border-orange-400', bgColor: 'bg-orange-50' },
    { id: 'gemini', name: 'Gemini Pro', description: 'Google多模态模型', icon: '✨', borderColor: 'border-green-400', bgColor: 'bg-green-50' },
  ]

  const writingStyles = [
    { id: 'deep', name: '深度分析', description: '专业、详细、有深度', color: 'from-blue-500 to-purple-500' },
    { id: 'simple', name: '简洁明了', description: '通俗易懂、重点突出', color: 'from-green-500 to-emerald-500' },
    { id: 'popular', name: '通俗易懂', description: '生动有趣、适合大众', color: 'from-orange-500 to-red-500' },
    { id: 'professional', name: '专业严谨', description: '学术风格、引用权威', color: 'from-indigo-500 to-blue-500' },
  ]

  const handleGenerateTitles = async () => {
    setIsGenerating(true)
    // 模拟AI生成
    await new Promise(resolve => setTimeout(resolve, 2000))
    setGeneratedTitles([
      { id: 1, title: 'GPT-4o发布：AI推理能力的新突破', predictedClickRate: 85 },
      { id: 2, title: 'DeepSeek-V3：开源模型的新里程碑', predictedClickRate: 78 },
      { id: 3, title: 'Claude 3.5 Sonnet：长文本处理的王者', predictedClickRate: 72 },
      { id: 4, title: 'Gemini Pro：谷歌AI的最新答卷', predictedClickRate: 68 },
      { id: 5, title: '2024年AI大模型发展报告', predictedClickRate: 65 },
    ])
    setIsGenerating(false)
    setStep('titles')
  }

  const handleSelectTitle = (title: string) => {
    setSelectedTitle(title)
    setStep('content')
  }

  const handleGenerateContent = async () => {
    setIsGenerating(true)
    // 模拟生成内容
    await new Promise(resolve => setTimeout(resolve, 5000))
    setGeneratedContent({
      title: selectedTitle,
      summary: '本文深入分析GPT-4o的技术特性、性能表现和应用场景，帮助读者全面了解这一突破性AI模型。',
      content: `## 引言

2024年5月，OpenAI发布了备受期待的GPT-4o模型，在推理能力上实现重大突破。作为GPT系列的最新成员，GPT-4o不仅继承了前代模型的强大语言理解能力，更在逻辑推理、数学计算和代码生成等方面展现出惊人的性能提升。

## GPT-4o的核心技术特性

### 1. 增强的推理引擎

GPT-4o采用了全新的推理引擎架构，通过多层次的思维链（Chain of Thought）机制，显著提升了复杂问题的解决能力。在处理需要多步骤推理的任务时，GPT-4o能够更准确地分解问题、规划解决路径，并逐步执行验证。

### 2. 优化的注意力机制

新的注意力机制设计使得模型能够更有效地处理长文本，上下文窗口扩展至128K tokens，同时保持了优秀的性能表现。这使得GPT-4o在处理长文档、代码库分析等任务时具有明显优势。

### 3. 多模态融合能力

GPT-4o在多模态处理方面也取得了显著进展，能够更好地理解和生成图文内容，为未来的应用场景打开了更多可能性。

## 性能表现对比

在多项基准测试中，GPT-4o的表现都超越了前代模型：

- **MMLU**: 89.2% (GPT-4: 86.4%)
- **HumanEval**: 92.5% (GPT-4: 67.0%)
- **GSM8K**: 94.8% (GPT-4: 92.0%)

## 应用场景

GPT-4o的强大能力使其在众多领域都有广泛的应用前景：

1. **科研辅助**: 帮助研究人员快速分析文献、生成假设
2. **教育领域**: 个性化学习辅导、智能答疑
3. **软件开发**: 代码生成、调试、优化
4. **内容创作**: 高质量文章、营销文案生成

## 总结

GPT-4o的发布标志着AI技术又迈出了重要一步。其强大的推理能力和多模态融合特性，将为各行各业带来深远的影响。我们有理由相信，随着技术的不断进步，AI将在更多领域发挥更大的价值。`,
      qualityScore: 87,
      sources: ['OpenAI官方文档', '学术论文', '技术博客'],
    })
    setIsGenerating(false)
    setStep('preview')
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold art-gradient-text">AI写作</h1>
          <p className="text-slate-600 mt-1">使用AI快速生成高质量内容</p>
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
            <label className="block text-sm font-medium mb-3 text-slate-700">写作风格</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {writingStyles.map((style) => (
                <button
                  key={style.id}
                  className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 transition-all text-left bg-white hover:scale-102"
                >
                  <div className="font-medium mb-1 text-slate-900">{style.name}</div>
                  <div className="text-xs text-slate-500">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" defaultChecked />
              <span className="text-sm text-slate-700">联网搜索</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" defaultChecked />
              <span className="text-sm text-slate-700">生成技术配图</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <span className="text-sm text-slate-700">添加数据图表</span>
            </label>
          </div>

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
                  className="w-full p-3 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-slate-800"
                />
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">摘要</label>
                <textarea
                  value={generatedContent.summary}
                  className="w-full h-24 p-3 rounded-xl bg-white/80 border border-slate-300 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 resize-none text-slate-800"
                />
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">正文内容</label>
                <textarea
                  value={generatedContent.content}
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
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700"
            >
              重新生成
            </button>
            <button className="flex-1 flex items-center justify-center gap-2 px-6 py-3 border border-slate-300 hover:bg-slate-50 transition-colors text-slate-700">
              <Save size={20} />
              保存草稿
            </button>
            <button className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl hover:shadow-lg hover:shadow-emerald-500/30 transition-all duration-300">
              <Send size={20} />
              直接发布
            </button>
          </div>
        </div>
      )}
    </div>
  )
}