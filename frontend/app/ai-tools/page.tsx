'use client'

import { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import {
  Wand2,
  Split,
  Search,
  Edit3,
  Copy,
  ChevronRight,
  Star,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  ArrowLeft,
  Sparkles,
  Lightbulb,
  FileText,
  BarChart3,
  Target,
  Clock,
  MessageSquare,
  Zap,
  X
} from 'lucide-react'
import Link from 'next/link'
import { API_URL } from '@/lib/api'

// 工具卡片组件
interface Tool {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  color: string
}

const tools: Tool[] = [
  {
    id: 'title-ab-test',
    name: '标题A/B测试',
    description: '生成多个标题变体，智能评分选出最佳标题',
    icon: <Split className="w-6 h-6" />,
    color: 'from-violet-500 to-purple-600'
  },
  {
    id: 'seo-analysis',
    name: 'SEO优化分析',
    description: '分析文章SEO表现，提供优化建议',
    icon: <Search className="w-6 h-6" />,
    color: 'from-emerald-500 to-teal-600'
  },
  {
    id: 'continue-write',
    name: '智能续写',
    description: '根据现有内容智能续写和扩写',
    icon: <Edit3 className="w-6 h-6" />,
    color: 'from-amber-500 to-orange-600'
  },
  {
    id: 'multi-version',
    name: '多版本生成',
    description: '生成正式版、通俗版、精简版等不同版本',
    icon: <Copy className="w-6 h-6" />,
    color: 'from-blue-500 to-cyan-600'
  }
]

export default function AIToolsPage() {
  const searchParams = useSearchParams()
  const articleId = searchParams.get('article_id')
  const [selectedTool, setSelectedTool] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // 标题A/B测试状态
  const [abTestContent, setAbTestContent] = useState('')
  const [abTestResults, setAbTestResults] = useState<any>(null)

  // SEO分析状态
  const [seoArticleId, setSeoArticleId] = useState(articleId || '')
  const [seoResults, setSeoResults] = useState<any>(null)

  // 续写状态
  const [continueContent, setContinueContent] = useState('')
  const [continueDirection, setContinueDirection] = useState('')
  const [continueLength, setContinueLength] = useState(500)
  const [continuedText, setContinuedText] = useState('')

  // 多版本状态
  const [multiContent, setMultiContent] = useState('')
  const [multiTopic, setMultiTopic] = useState('')
  const [selectedVersions, setSelectedVersions] = useState<string[]>(['formal', 'casual', 'concise'])
  const [multiResults, setMultiResults] = useState<any>(null)

  const handleTitleABTest = async () => {
    if (!abTestContent.trim()) return
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/ai-enhance/title-ab-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: abTestContent,
          count: 5
        })
      })
      if (response.ok) {
        const data = await response.json()
        setAbTestResults(data)
      }
    } catch (error) {
      console.error('A/B测试失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSEOAnalysis = async () => {
    if (!seoArticleId) return
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/ai-enhance/seo-analysis?article_id=${seoArticleId}`)
      if (response.ok) {
        const data = await response.json()
        setSeoResults(data)
      }
    } catch (error) {
      console.error('SEO分析失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleContinueWrite = async () => {
    if (!continueContent.trim()) return
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/ai-enhance/continue-write`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: continueContent,
          direction: continueDirection,
          target_length: continueLength
        })
      })
      if (response.ok) {
        const data = await response.json()
        setContinuedText(data.continued_content)
      }
    } catch (error) {
      console.error('续写失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMultiVersion = async () => {
    if (!multiContent.trim() || !multiTopic.trim()) return
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/ai-enhance/multi-version`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: multiContent,
          topic: multiTopic,
          versions: selectedVersions
        })
      })
      if (response.ok) {
        const data = await response.json()
        setMultiResults(data)
      }
    } catch (error) {
      console.error('多版本生成失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 渲染工具选择界面
  if (!selectedTool) {
    return (
      <div className="min-h-screen bg-slate-50">
        {/* 头部 */}
        <div className="bg-white border-b border-slate-200">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                <Wand2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">AI 增强工具</h1>
                <p className="text-slate-500 mt-1">智能工具助力内容创作</p>
              </div>
            </div>
          </div>
        </div>

        {/* 工具卡片 */}
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tools.map(tool => (
              <div
                key={tool.id}
                onClick={() => setSelectedTool(tool.id)}
                className="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-xl transition-all cursor-pointer group"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${tool.color} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform`}>
                    {tool.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-slate-900 group-hover:text-violet-600 transition-colors">
                      {tool.name}
                    </h3>
                    <p className="text-slate-500 mt-1">{tool.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-violet-500 group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            ))}
          </div>

          {/* 使用提示 */}
          <div className="mt-12 p-6 bg-gradient-to-r from-violet-50 to-purple-50 rounded-2xl border border-violet-100">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-violet-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 mb-2">使用提示</h3>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    标题A/B测试可帮助您选择最具吸引力的标题
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    SEO分析可优化文章的搜索引擎排名
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    智能续写可帮您快速扩展文章内容
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    多版本生成适合不同平台和受众
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 渲染具体工具界面
  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <div className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                setSelectedTool(null)
                setAbTestResults(null)
                setSeoResults(null)
                setContinuedText('')
                setMultiResults(null)
              }}
              className="p-2 rounded-xl hover:bg-slate-100 text-slate-500 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${tools.find(t => t.id === selectedTool)?.color} flex items-center justify-center text-white`}>
                {tools.find(t => t.id === selectedTool)?.icon}
              </div>
              <h1 className="text-xl font-semibold text-slate-900">
                {tools.find(t => t.id === selectedTool)?.name}
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* 内容区 */}
      <div className="max-w-5xl mx-auto px-6 py-6">
        {/* 标题A/B测试 */}
        {selectedTool === 'title-ab-test' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">文章内容</label>
              <textarea
                value={abTestContent}
                onChange={(e) => setAbTestContent(e.target.value)}
                placeholder="粘贴文章内容，AI将为您生成多个标题变体..."
                className="w-full h-48 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none transition-all"
              />
              <div className="flex justify-end mt-4">
                <button
                  onClick={handleTitleABTest}
                  disabled={loading || !abTestContent.trim()}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      分析中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      生成标题变体
                    </>
                  )}
                </button>
              </div>
            </div>

            {abTestResults && (
              <div className="space-y-6">
                {/* 最佳标题推荐 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-5 h-5" />
                      <span className="font-medium">最适合点击</span>
                    </div>
                    <p className="text-lg font-semibold mb-2">{abTestResults.best_for_click?.title}</p>
                    <div className="flex items-center gap-4 text-sm text-white/80">
                      <span>评分: {abTestResults.best_for_click?.score}分</span>
                      <span>风格: {abTestResults.best_for_click?.style}</span>
                    </div>
                  </div>
                  <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
                    <div className="flex items-center gap-2 mb-3">
                      <Search className="w-5 h-5" />
                      <span className="font-medium">最适合SEO</span>
                    </div>
                    <p className="text-lg font-semibold mb-2">{abTestResults.best_for_seo?.title}</p>
                    <div className="flex items-center gap-4 text-sm text-white/80">
                      <span>评分: {abTestResults.best_for_seo?.score}分</span>
                      <span>风格: {abTestResults.best_for_seo?.style}</span>
                    </div>
                  </div>
                </div>

                {/* 所有变体 */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6">
                  <h3 className="font-semibold text-slate-900 mb-4">所有标题变体</h3>
                  <div className="space-y-3">
                    {abTestResults.variants?.map((variant: any, index: number) => (
                      <div
                        key={index}
                        className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl hover:bg-violet-50 transition-colors group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-violet-100 text-violet-600 flex items-center justify-center font-bold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-slate-900">{variant.title}</p>
                          <p className="text-sm text-slate-500 mt-1">{variant.reason}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-1 rounded-lg text-xs font-medium ${
                            variant.score >= 85 ? 'bg-emerald-100 text-emerald-600' :
                            variant.score >= 70 ? 'bg-blue-100 text-blue-600' :
                            'bg-amber-100 text-amber-600'
                          }`}>
                            {variant.score}分
                          </span>
                          <span className="px-2 py-1 rounded-lg bg-slate-200 text-slate-600 text-xs">
                            {variant.style}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 分析建议 */}
                {abTestResults.analysis && (
                  <div className="bg-amber-50 rounded-2xl p-6 border border-amber-100">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="w-5 h-5 text-amber-500 mt-0.5" />
                      <div>
                        <h4 className="font-medium text-slate-900 mb-2">分析建议</h4>
                        <p className="text-sm text-slate-600">{abTestResults.analysis}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* SEO分析 */}
        {selectedTool === 'seo-analysis' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">文章ID</label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={seoArticleId}
                  onChange={(e) => setSeoArticleId(e.target.value)}
                  placeholder="输入文章ID"
                  className="flex-1 px-4 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition-all"
                />
                <button
                  onClick={handleSEOAnalysis}
                  disabled={loading || !seoArticleId}
                  className="flex items-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                >
                  {loading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  分析
                </button>
              </div>
            </div>

            {seoResults && (
              <div className="space-y-6">
                {/* 总体评分 */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-slate-900">SEO评分</h3>
                    <div className={`text-3xl font-bold ${
                      seoResults.score >= 80 ? 'text-emerald-500' :
                      seoResults.score >= 60 ? 'text-amber-500' :
                      'text-red-500'
                    }`}>
                      {seoResults.score}分
                    </div>
                  </div>
                  <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        seoResults.score >= 80 ? 'bg-emerald-500' :
                        seoResults.score >= 60 ? 'bg-amber-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${seoResults.score}%` }}
                    />
                  </div>
                </div>

                {/* 详细分析 */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white rounded-2xl border border-slate-200 p-5">
                    <h4 className="font-medium text-slate-900 mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-violet-500" />
                      标题分析
                    </h4>
                    <ul className="space-y-2 text-sm">
                      {seoResults.title_analysis?.suggestions?.map((s: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-slate-600">
                          <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-white rounded-2xl border border-slate-200 p-5">
                    <h4 className="font-medium text-slate-900 mb-3 flex items-center gap-2">
                      <Target className="w-4 h-4 text-violet-500" />
                      关键词分析
                    </h4>
                    <ul className="space-y-2 text-sm">
                      {seoResults.keyword_analysis?.suggestions?.map((s: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-slate-600">
                          <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="bg-white rounded-2xl border border-slate-200 p-5">
                    <h4 className="font-medium text-slate-900 mb-3 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-violet-500" />
                      内容分析
                    </h4>
                    <ul className="space-y-2 text-sm">
                      {seoResults.content_analysis?.suggestions?.map((s: string, i: number) => (
                        <li key={i} className="flex items-start gap-2 text-slate-600">
                          <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 优化建议 */}
                {seoResults.suggestions?.length > 0 && (
                  <div className="bg-white rounded-2xl border border-slate-200 p-6">
                    <h4 className="font-medium text-slate-900 mb-4">优化建议</h4>
                    <div className="space-y-3">
                      {seoResults.suggestions.map((suggestion: any, index: number) => (
                        <div
                          key={index}
                          className="flex items-start gap-3 p-3 bg-slate-50 rounded-xl"
                        >
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            suggestion.priority === '高' ? 'bg-red-100 text-red-600' :
                            suggestion.priority === '中' ? 'bg-amber-100 text-amber-600' :
                            'bg-blue-100 text-blue-600'
                          }`}>
                            {suggestion.priority}优先级
                          </span>
                          <div>
                            <span className="font-medium text-slate-700">{suggestion.type}:</span>
                            <span className="text-slate-600 ml-2">{suggestion.content}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* 智能续写 */}
        {selectedTool === 'continue-write' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">现有内容</label>
              <textarea
                value={continueContent}
                onChange={(e) => setContinueContent(e.target.value)}
                placeholder="输入现有文章内容..."
                className="w-full h-40 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none transition-all"
              />
              <div className="mt-4 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">续写方向（可选）</label>
                  <input
                    type="text"
                    value={continueDirection}
                    onChange={(e) => setContinueDirection(e.target.value)}
                    placeholder="例如：深入分析原因、提供解决方案、展望未来趋势..."
                    className="w-full px-4 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">目标字数: {continueLength}字</label>
                  <input
                    type="range"
                    min="100"
                    max="2000"
                    step="100"
                    value={continueLength}
                    onChange={(e) => setContinueLength(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
              <div className="flex justify-end mt-4">
                <button
                  onClick={handleContinueWrite}
                  disabled={loading || !continueContent.trim()}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      续写中...
                    </>
                  ) : (
                    <>
                      <Edit3 className="w-4 h-4" />
                      智能续写
                    </>
                  )}
                </button>
              </div>
            </div>

            {continuedText && (
              <div className="bg-white rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-slate-900">续写结果</h3>
                  <button
                    onClick={() => navigator.clipboard.writeText(continuedText)}
                    className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 text-sm hover:bg-slate-200 transition-colors"
                  >
                    复制内容
                  </button>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {continuedText}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 多版本生成 */}
        {selectedTool === 'multi-version' && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">文章主题</label>
                  <input
                    type="text"
                    value={multiTopic}
                    onChange={(e) => setMultiTopic(e.target.value)}
                    placeholder="输入文章主题..."
                    className="w-full px-4 py-2 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">原文内容</label>
                  <textarea
                    value={multiContent}
                    onChange={(e) => setMultiContent(e.target.value)}
                    placeholder="粘贴原文内容..."
                    className="w-full h-40 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">选择版本</label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { id: 'formal', name: '正式版', desc: '专业严谨' },
                      { id: 'casual', name: '通俗版', desc: '轻松易懂' },
                      { id: 'concise', name: '精简版', desc: '核心要点' },
                      { id: 'detailed', name: '详细版', desc: '深度解析' },
                      { id: 'creative', name: '创意版', desc: '独特视角' }
                    ].map(version => (
                      <button
                        key={version.id}
                        onClick={() => {
                          if (selectedVersions.includes(version.id)) {
                            setSelectedVersions(selectedVersions.filter(v => v !== version.id))
                          } else {
                            setSelectedVersions([...selectedVersions, version.id])
                          }
                        }}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                          selectedVersions.includes(version.id)
                            ? 'bg-blue-500 text-white'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        {version.name}
                        <span className="ml-1 text-xs opacity-70">({version.desc})</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end mt-4">
                <button
                  onClick={handleMultiVersion}
                  disabled={loading || !multiContent.trim() || !multiTopic.trim() || selectedVersions.length === 0}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      生成多版本
                    </>
                  )}
                </button>
              </div>
            </div>

            {multiResults && (
              <div className="space-y-6">
                {multiResults.versions?.map((version: any, index: number) => (
                  <div key={index} className="bg-white rounded-2xl border border-slate-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="font-semibold text-slate-900">{version.title}</h4>
                        <p className="text-sm text-slate-500 mt-1">{version.description}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        version.version_type === 'formal' ? 'bg-violet-100 text-violet-600' :
                        version.version_type === 'casual' ? 'bg-green-100 text-green-600' :
                        version.version_type === 'concise' ? 'bg-amber-100 text-amber-600' :
                        version.version_type === 'detailed' ? 'bg-blue-100 text-blue-600' :
                        'bg-pink-100 text-pink-600'
                      }`}>
                        {version.version_type === 'formal' ? '正式版' :
                         version.version_type === 'casual' ? '通俗版' :
                         version.version_type === 'concise' ? '精简版' :
                         version.version_type === 'detailed' ? '详细版' : '创意版'}
                      </span>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-xl text-slate-700 text-sm leading-relaxed max-h-60 overflow-y-auto">
                      {version.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
