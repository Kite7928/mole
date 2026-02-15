'use client'

import { useState, useEffect } from 'react'
import { 
  Sparkles, 
  Wand2, 
  RefreshCw, 
  Check, 
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Save,
  Send,
  ChevronRight,
  Loader2,
  ArrowLeft,
  Image as ImageIcon,
  FileText,
  Type,
  BarChart3,
  PenTool
} from 'lucide-react'
import {
  generateTitles,
  generateContent,
  createArticle,
  updateArticle,
  publishToWechat,
  scoreTitle,
  checkSensitiveContent,
  type TitleScoreResponse,
  type SensitiveWordMatch,
} from '@/lib/api'
import { API_URL } from '@/lib/api'
import RichEditor from '@/components/rich-editor'


interface TitleOption {
  title: string
  click_rate: number
  score: number
  reason: string
}


interface GeneratedContentState {
  title: string
  summary: string
  content: string
  qualityScore: number
}


interface ContentVariant extends GeneratedContentState {
  key: 'A' | 'B'
}

interface PrePublishCheckResult {
  pass: boolean
  checkedAt: string
  titleScore: TitleScoreResponse | null
  hasSensitive: boolean
  sensitiveCount: number
  sensitiveMatches: SensitiveWordMatch[]
  filteredContent?: string
  formatWarnings: string[]
  blockingIssues: string[]
}

type QualityCheckStatus = 'unchecked' | 'pass' | 'warning' | 'blocked'

export default function ArticleCreate() {
  const [step, setStep] = useState<'input' | 'titles' | 'preview'>('input')
  const [isEditMode, setIsEditMode] = useState(false)
  const [editArticleId, setEditArticleId] = useState<number | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedTitleCandidates, setSelectedTitleCandidates] = useState<string[]>([])
  const [topic, setTopic] = useState('')
  const [aiModel, setAiModel] = useState('gpt-5-nano')
  const [writingStyle, setWritingStyle] = useState('professional')
  const [generatedTitles, setGeneratedTitles] = useState<TitleOption[]>([])
  const [generatedContent, setGeneratedContent] = useState<GeneratedContentState | null>(null)
  const [contentVariants, setContentVariants] = useState<ContentVariant[]>([])
  const [activeVariantKey, setActiveVariantKey] = useState<'A' | 'B' | null>(null)
  const [editingContent, setEditingContent] = useState('')
  const [editorMode, setEditorMode] = useState<'plain' | 'rich'>('plain')
  const [isSaving, setIsSaving] = useState(false)
  const [generateCoverImage, setGenerateCoverImage] = useState(true)
  const [coverImageUrl, setCoverImageUrl] = useState<string>('')
  const [newsSource, setNewsSource] = useState<{title?: string, source?: string} | null>(null)
  const [generationError, setGenerationError] = useState<string>('')
  const [isScoringTitle, setIsScoringTitle] = useState(false)
  const [titleScores, setTitleScores] = useState<Record<string, TitleScoreResponse>>({})
  const [activeTitleScore, setActiveTitleScore] = useState<TitleScoreResponse | null>(null)
  const [isQualityChecking, setIsQualityChecking] = useState(false)
  const [qualityCheck, setQualityCheck] = useState<PrePublishCheckResult | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const editId = params.get('editId')
    const articleId = params.get('article_id')
    const fromNews = params.get('from_news')
    const titleFromNews = params.get('title')
    const sourceFromNews = params.get('source')
    
    if (editId) {
      setIsEditMode(true)
      setEditArticleId(parseInt(editId))
      loadArticle(parseInt(editId))
    } else if (articleId) {
      setIsEditMode(true)
      setEditArticleId(parseInt(articleId))
      loadArticle(parseInt(articleId))
      if (fromNews && titleFromNews) {
        setNewsSource({ title: decodeURIComponent(titleFromNews), source: sourceFromNews ? decodeURIComponent(sourceFromNews) : undefined })
      }
    }
  }, [])

  const loadArticle = async (articleId: number) => {
    try {
      const response = await fetch(`${API_URL}/api/articles/${articleId}`)
      if (response.ok) {
        const article = await response.json()
        setTopic(article.title)
        setEditingContent(article.content)
        let summary = article.summary || ''
        if (summary.includes('点击查看原文') || summary.includes('http')) {
          summary = article.content ? article.content.substring(0, 200).replace(/[#*\n]/g, ' ') + '...' : ''
        }
        const loadedContent: GeneratedContentState = {
          title: article.title,
          content: article.content,
          summary: summary,
          qualityScore: article.quality_score || 85
        }
        setGeneratedContent(loadedContent)
        setContentVariants([{ key: 'A', ...loadedContent }])
        setActiveVariantKey('A')
        setSelectedTitleCandidates([article.title])
        setActiveTitleScore(null)
        setQualityCheck(null)
        setCoverImageUrl(article.cover_image_url || '')
        setStep('preview')
      }
    } catch (error) {
      console.error('加载文章失败:', error)
    }
  }

  const sanitizeSummary = (summary: string, content: string, fallbackTopic: string) => {
    if (summary.includes('点击查看原文') || summary.includes('http') || !summary.trim()) {
      return content ? content.substring(0, 200).replace(/[#*\n]/g, ' ') + '...' : `本文深入探讨了${fallbackTopic}的核心概念。`
    }
    return summary
  }

  const normalizeTitles = (titles: any[]): TitleOption[] => {
    return titles.map((item: any, index: number) => {
      const clickRate = Math.round(Number(item?.click_rate ?? item?.score ?? 75))
      const score = Math.round(Number(item?.score ?? item?.click_rate ?? 75))
      return {
        title: String(item?.title ?? ''),
        click_rate: clickRate,
        score,
        reason: item?.reason || `预估点击率 ${clickRate}%`
      }
    }).filter((item: TitleOption) => !!item.title)
  }

  const buildVariant = (
    variantKey: 'A' | 'B',
    title: string,
    payload: any
  ): ContentVariant => {
    const contentText = payload?.content || ''
    const summary = sanitizeSummary(payload?.summary || '', contentText, topic)
    return {
      key: variantKey,
      title,
      summary,
      content: contentText,
      qualityScore: Math.round(payload?.quality_score || 85),
    }
  }

  const applyActiveVariant = (variant: ContentVariant) => {
    setActiveVariantKey(variant.key)
    setGeneratedContent({
      title: variant.title,
      summary: variant.summary,
      content: variant.content,
      qualityScore: variant.qualityScore,
    })
    setEditingContent(variant.content)
    setActiveTitleScore(titleScores[variant.title] || null)
    setQualityCheck(null)
    setStep('preview')
  }

  const handleTitleCandidatesToggle = (title: string) => {
    setSelectedTitleCandidates((prev) => {
      if (prev.includes(title)) {
        return prev.filter((item) => item !== title)
      }
      if (prev.length >= 2) {
        return [...prev.slice(1), title]
      }
      return [...prev, title]
    })
  }

  const generateContentFromCandidates = async () => {
    const targets = selectedTitleCandidates.slice(0, 2)
    if (targets.length === 0) {
      alert('请先选择至少一个标题')
      return
    }

    setIsGenerating(true)
    setGenerationError('')
    setQualityCheck(null)

    try {
      try {
        await refreshTitleScores(targets)
      } catch {
        // 标题评分失败不阻断正文生成
      }

      const settled = await Promise.allSettled(
        targets.map((title) => generateContent(topic, title, writingStyle, 'medium', aiModel))
      )

      const variants: ContentVariant[] = []
      const failures: string[] = []

      settled.forEach((result, index) => {
        const variantKey: 'A' | 'B' = index === 0 ? 'A' : 'B'
        const title = targets[index]

        if (result.status === 'fulfilled') {
          variants.push(buildVariant(variantKey, title, result.value))
        } else {
          failures.push(`${variantKey}版《${title}》生成失败`)
        }
      })

      if (variants.length === 0) {
        throw new Error('正文生成失败，请检查AI配置后重试')
      }

      setContentVariants(variants)
      applyActiveVariant(variants[0])

      if (failures.length > 0) {
        alert(`部分版本生成失败：\n${failures.join('\n')}`)
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : '生成内容失败，请检查AI配置后重试'
      setGenerationError(message)
      alert(message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleVariantSwitch = (variantKey: 'A' | 'B') => {
    const targetVariant = contentVariants.find((item) => item.key === variantKey)
    if (!targetVariant) return
    applyActiveVariant(targetVariant)
  }

  const handleTitleChange = (value: string) => {
    if (!generatedContent) return
    setGeneratedContent({ ...generatedContent, title: value })
    setActiveTitleScore(titleScores[value] || null)
    setQualityCheck(null)
    if (!activeVariantKey) return
    setContentVariants((prev) => prev.map((item) => (
      item.key === activeVariantKey ? { ...item, title: value } : item
    )))
  }

  const handleSummaryChange = (value: string) => {
    if (!generatedContent) return
    setGeneratedContent({ ...generatedContent, summary: value })
    setQualityCheck(null)
    if (!activeVariantKey) return
    setContentVariants((prev) => prev.map((item) => (
      item.key === activeVariantKey ? { ...item, summary: value } : item
    )))
  }

  const handleContentChange = (value: string) => {
    setEditingContent(value)
    setQualityCheck(null)
    if (!activeVariantKey) return
    setContentVariants((prev) => prev.map((item) => (
      item.key === activeVariantKey ? { ...item, content: value } : item
    )))
  }

  const toPlainText = (value: string) => {
    return value
      .replace(/<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<script[\s\S]*?<\/script>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
  }

  const analyzeContentFormat = (title: string, summary: string, content: string) => {
    const warnings: string[] = []
    const blocking: string[] = []

    const plainText = toPlainText(content)
    const contentLength = plainText.length
    const titleLength = title.trim().length
    const summaryLength = summary.trim().length

    const hasMarkdownHeading = /(^|\n)#{1,3}\s+\S+/m.test(content)
    const hasHtmlHeading = /<h[1-3][^>]*>.*?<\/h[1-3]>/i.test(content)
    const hasHeading = hasMarkdownHeading || hasHtmlHeading

    const markdownParagraphs = content.split(/\n{2,}/).filter((item) => item.trim().length > 0).length
    const htmlParagraphs = (content.match(/<p[\s>]/gi) || []).length
    const paragraphCount = Math.max(markdownParagraphs, htmlParagraphs)

    if (!title.trim()) {
      blocking.push('标题不能为空')
    }

    if (contentLength < 300) {
      blocking.push('正文内容过短（少于300字），建议补充后再发布')
    }

    if (titleLength > 35 || titleLength < 10) {
      warnings.push('标题建议控制在10~35字，避免过短或过长')
    }

    if (summaryLength < 40) {
      warnings.push('摘要偏短，建议补充到40字以上以提升分发效果')
    }

    if (!hasHeading) {
      warnings.push('正文缺少小标题，建议加入至少1个二级标题提升可读性')
    }

    if (paragraphCount < 3) {
      warnings.push('段落层次偏少，建议拆分为至少3个段落')
    }

    const hasImage = /<img\s+[^>]*src=|!\[[^\]]*\]\([^\)]+\)/i.test(content)
    if (!hasImage) {
      warnings.push('正文暂未包含配图，建议添加至少1张配图提升阅读完成率')
    }

    return {
      warnings,
      blocking,
      contentLength,
    }
  }

  const refreshTitleScores = async (titles: string[]) => {
    if (titles.length === 0) {
      return {}
    }

    setIsScoringTitle(true)
    const scoreMap: Record<string, TitleScoreResponse> = {}

    try {
      const settled = await Promise.allSettled(
        titles.map((title) => scoreTitle(title, topic, aiModel))
      )

      settled.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          scoreMap[titles[index]] = result.value
        }
      })

      if (Object.keys(scoreMap).length === 0) {
        throw new Error('标题评分服务暂时不可用')
      }

      setTitleScores((prev) => ({ ...prev, ...scoreMap }))
      setGeneratedTitles((prev) => prev.map((item) => {
        const scoreResult = scoreMap[item.title]
        if (!scoreResult) return item
        return {
          ...item,
          score: Math.round(scoreResult.score),
          click_rate: Math.round(scoreResult.click_rate),
          reason: scoreResult.analysis || `预估点击率 ${Math.round(scoreResult.click_rate)}%`
        }
      }))

      return scoreMap
    } finally {
      setIsScoringTitle(false)
    }
  }

  const handleScoreSelectedTitles = async () => {
    const targets = selectedTitleCandidates.slice(0, 2)
    if (targets.length === 0) {
      alert('请先选择至少一个标题')
      return
    }

    try {
      const scoreMap = await refreshTitleScores(targets)
      const first = scoreMap[targets[0]]
      if (first) {
        setActiveTitleScore(first)
      }
      alert('标题评分已更新')
    } catch (error: any) {
      alert(error?.message || '标题评分失败')
    }
  }

  const handleScoreCurrentTitle = async () => {
    if (!generatedContent?.title?.trim()) {
      alert('请先输入标题')
      return
    }

    setIsScoringTitle(true)
    try {
      const result = await scoreTitle(generatedContent.title, topic, aiModel)
      setTitleScores((prev) => ({ ...prev, [generatedContent.title]: result }))
      setActiveTitleScore(result)
      alert('标题评分完成')
    } catch (error: any) {
      alert(error?.message || '标题评分失败')
    } finally {
      setIsScoringTitle(false)
    }
  }

  const handleOptimizeCurrentTitle = async () => {
    const currentTitle = generatedContent?.title?.trim()
    if (!currentTitle) {
      alert('请先输入标题')
      return
    }

    setIsScoringTitle(true)
    try {
      const seedTopic = topic.trim() || currentTitle
      const generated = await generateTitles(seedTopic, 6, aiModel)
      const normalized = normalizeTitles(generated)

      const uniqueCandidates = Array.from(new Set([
        currentTitle,
        ...normalized.map((item) => item.title.trim()).filter(Boolean),
      ])).slice(0, 6)

      let scoreMap: Record<string, TitleScoreResponse> = {}
      try {
        const settled = await Promise.allSettled(
          uniqueCandidates.map((title) => scoreTitle(title, seedTopic, aiModel))
        )

        settled.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            scoreMap[uniqueCandidates[index]] = result.value
          }
        })

        if (Object.keys(scoreMap).length > 0) {
          setTitleScores((prev) => ({ ...prev, ...scoreMap }))
        }
      } catch {
        scoreMap = {}
      }

      const ranked = uniqueCandidates
        .map((title, index) => ({
          title,
          score: scoreMap[title]?.score ?? 0,
          clickRate: scoreMap[title]?.click_rate ?? 0,
          index,
        }))
        .sort((a, b) => {
          if (b.score !== a.score) {
            return b.score - a.score
          }
          if (b.clickRate !== a.clickRate) {
            return b.clickRate - a.clickRate
          }
          return a.index - b.index
        })

      const optimized = ranked.find((item) => item.title !== currentTitle)
      if (!optimized) {
        alert('暂未生成更优标题，请调整主题后重试')
        return
      }

      handleTitleChange(optimized.title)
      setSelectedTitleCandidates((prev) => {
        const merged = Array.from(new Set([optimized.title, ...prev]))
        return merged.slice(0, 2)
      })
      setActiveTitleScore(scoreMap[optimized.title] || null)

      if (scoreMap[optimized.title]) {
        alert(`已生成更优标题：${optimized.title}`)
      } else {
        alert(`已为你生成推荐标题：${optimized.title}`)
      }
    } catch (error: any) {
      alert(error?.message || '标题优化失败')
    } finally {
      setIsScoringTitle(false)
    }
  }

  const runPrePublishCheck = async (): Promise<PrePublishCheckResult> => {
    if (!generatedContent) {
      throw new Error('请先生成正文内容')
    }

    setIsQualityChecking(true)
    try {
      const latestTitle = generatedContent.title || ''
      const latestSummary = generatedContent.summary || ''
      const latestContent = editingContent || ''

      const formatResult = analyzeContentFormat(latestTitle, latestSummary, latestContent)

      let sensitiveCount = 0
      let sensitiveMatches: SensitiveWordMatch[] = []
      let filteredContent: string | undefined
      let hasSensitive = false

      try {
        const sensitiveResult = await checkSensitiveContent(latestContent)
        sensitiveCount = sensitiveResult.total_count || 0
        sensitiveMatches = sensitiveResult.matches || []
        filteredContent = sensitiveResult.filtered_content
        hasSensitive = !!sensitiveResult.has_sensitive
      } catch {
        formatResult.warnings.push('敏感词检测服务暂不可用，请手动复核后发布')
      }

      let currentTitleScore: TitleScoreResponse | null = titleScores[latestTitle] || null
      if (!currentTitleScore) {
        try {
          currentTitleScore = await scoreTitle(latestTitle, topic, aiModel)
          setTitleScores((prev) => ({ ...prev, [latestTitle]: currentTitleScore as TitleScoreResponse }))
        } catch {
          formatResult.warnings.push('标题评分服务暂不可用，未能完成自动评分')
        }
      }

      const blockingIssues = [...formatResult.blocking]
      if (hasSensitive) {
        blockingIssues.push(`检测到 ${sensitiveCount} 处敏感词，需处理后再发布`)
      }

      const checkResult: PrePublishCheckResult = {
        pass: blockingIssues.length === 0,
        checkedAt: new Date().toISOString(),
        titleScore: currentTitleScore,
        hasSensitive,
        sensitiveCount,
        sensitiveMatches,
        filteredContent,
        formatWarnings: formatResult.warnings,
        blockingIssues,
      }

      setQualityCheck(checkResult)
      setActiveTitleScore(currentTitleScore)
      return checkResult
    } finally {
      setIsQualityChecking(false)
    }
  }

  const applySensitiveReplacement = () => {
    if (!qualityCheck?.filteredContent) {
      return
    }

    handleContentChange(qualityCheck.filteredContent)
    setQualityCheck((prev) => {
      if (!prev) return prev
      return {
        ...prev,
        hasSensitive: false,
        sensitiveCount: 0,
        sensitiveMatches: [],
        blockingIssues: prev.blockingIssues.filter((item) => !item.includes('敏感词')),
        pass: prev.blockingIssues.filter((item) => !item.includes('敏感词')).length === 0,
      }
    })
    alert('敏感词已自动替换，请再次执行质检确认')
  }

  const resolveQualityCheckStatus = (result: PrePublishCheckResult | null): QualityCheckStatus => {
    if (!result) {
      return 'unchecked'
    }

    if (result.blockingIssues.length > 0) {
      return 'blocked'
    }

    if (result.formatWarnings.length > 0) {
      return 'warning'
    }

    return 'pass'
  }

  const buildQualityCheckPayload = (result: PrePublishCheckResult | null) => {
    const qualityCheckStatus = resolveQualityCheckStatus(result)

    if (!result) {
      return {
        quality_check_status: qualityCheckStatus,
        quality_check_data: null,
        quality_checked_at: null,
      }
    }

    return {
      quality_check_status: qualityCheckStatus,
      quality_check_data: {
        pass: result.pass,
        checkedAt: result.checkedAt,
        titleScore: result.titleScore,
        hasSensitive: result.hasSensitive,
        sensitiveCount: result.sensitiveCount,
        sensitiveMatches: result.sensitiveMatches,
        filteredContent: result.filteredContent,
        formatWarnings: result.formatWarnings,
        blockingIssues: result.blockingIssues,
      },
      quality_checked_at: result.checkedAt,
    }
  }

  const handleManualQualityCheck = async () => {
    try {
      const result = await runPrePublishCheck()
      if (result.pass) {
        alert('质检通过，可发布')
      } else {
        alert('质检未通过，请根据提示修正后重试')
      }
    } catch (error: any) {
      alert(error?.message || '质检失败')
    }
  }

  const aiModels = [
    { id: 'gpt-5-nano', name: 'GPT-5 Nano', icon: '🧠', desc: '默认' },
    { id: 'claude-sonnet-4.5', name: 'Claude Sonnet 4.5', icon: '✨', desc: '渠道33' },
    { id: 'moonshotai/kimi-k2-thinking', name: 'Kimi K2 Thinking', icon: '🌙', desc: '深度思考' },
    { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', icon: '💎', desc: '渠道33' },
    { id: 'qwen-max', name: '通义千问', icon: '🌐', desc: '备选' },
    { id: 'deepseek-chat', name: 'DeepSeek', icon: '🚀', desc: '备选' },
  ]

  const writingStyles = [
    { id: 'professional', name: '专业解读', icon: '📊', desc: '深度分析' },
    { id: 'casual', name: '轻松聊天', icon: '💬', desc: '亲和力强' },
    { id: 'story', name: '故事共鸣', icon: '📖', desc: '引人入胜' },
  ]

  const handleGenerateTitles = async () => {
    if (!topic.trim()) { alert('请输入主题'); return }
    setIsGenerating(true)
    setGenerationError('')
    setActiveTitleScore(null)
    setQualityCheck(null)
    try {
      const titles = await generateTitles(topic, 5, aiModel)
      const normalizedTitles = normalizeTitles(titles)
      setGeneratedTitles(normalizedTitles)
      setSelectedTitleCandidates(normalizedTitles.slice(0, 2).map((item) => item.title))
      setStep('titles')
    } catch (error) {
      const message = error instanceof Error ? error.message : '生成标题失败'
      setGenerationError(message)
      alert(message)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSelectTitle = async (title: string) => {
    handleTitleCandidatesToggle(title)
  }

  const persistDraft = async (silent = false, contentOverride?: string): Promise<number> => {
    if (!generatedContent) {
      throw new Error('请先生成正文内容')
    }

    const draftContent = contentOverride ?? editingContent

    const summary = sanitizeSummary(
      generatedContent.summary || '',
      draftContent,
      topic
    )
    const qualityPayload = buildQualityCheckPayload(qualityCheck)

    if (isEditMode && editArticleId) {
      await updateArticle(editArticleId, {
        title: generatedContent.title,
        content: draftContent,
        summary,
        status: 'draft',
        cover_image_url: coverImageUrl,
        ...qualityPayload,
      })

      if (!silent) {
        alert('保存成功！')
      }
      return editArticleId
    }

    const article = await createArticle({
      title: generatedContent.title,
      content: draftContent,
      summary,
      status: 'draft',
      ...qualityPayload,
      generate_cover_image: generateCoverImage,
    })

    setEditArticleId(article.id)
    setIsEditMode(true)

    if (!silent) {
      alert('保存成功！')
    }

    return article.id
  }

  const handleSaveDraft = async () => {
    setIsSaving(true)
    try {
      await persistDraft(false)
    } catch (error: any) {
      alert(`保存失败: ${error?.message || '未知错误'}`)
    } finally {
      setIsSaving(false)
    }
  }

  const handlePublish = async () => {
    if (!confirm('确定要发布到微信公众号吗？')) return
    if (!generatedContent) {
      alert('请先生成正文内容')
      return
    }

    setIsSaving(true)
    try {
      const checkResult = await runPrePublishCheck()
      if (checkResult.blockingIssues.length > 0) {
        alert(`发布前质检未通过：\n${checkResult.blockingIssues.map((item) => `- ${item}`).join('\n')}`)
        return
      }

      if (checkResult.formatWarnings.length > 0) {
        const proceed = confirm(
          `质检发现以下优化项：\n${checkResult.formatWarnings.map((item) => `- ${item}`).join('\n')}\n\n是否仍要继续发布？`
        )
        if (!proceed) {
          return
        }
      }

      let contentForPublish = editingContent
      if (checkResult.hasSensitive && checkResult.filteredContent) {
        const confirmReplace = confirm(`检测到 ${checkResult.sensitiveCount} 处敏感词，是否自动替换后继续发布？`)
        if (!confirmReplace) {
          return
        }
        contentForPublish = checkResult.filteredContent
        handleContentChange(contentForPublish)
      }

      const summaryForPublish = sanitizeSummary(
        generatedContent.summary || '',
        contentForPublish,
        topic
      )

      const articleId = await persistDraft(true, contentForPublish)
      const result = await publishToWechat({
        title: generatedContent.title,
        content: contentForPublish,
        digest: summaryForPublish
      })

      if (!result.success) {
        alert('发布响应异常')
        return
      }

      await updateArticle(articleId, { status: 'published', wechat_draft_id: result.draft_id })
      alert(`发布成功！草稿ID: ${result.draft_id}`)
    } catch (error: any) {
      alert(`发布失败: ${error?.message || '未知错误'}`)
    } finally {
      setIsSaving(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-600'
    if (score >= 80) return 'text-blue-600'
    if (score >= 70) return 'text-amber-600'
    return 'text-slate-500'
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-emerald-500'
    if (score >= 80) return 'bg-blue-500'
    if (score >= 70) return 'bg-amber-500'
    return 'bg-slate-400'
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-6">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <a href="/articles" className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors">
                <ArrowLeft className="w-4 h-4 text-slate-500" />
              </a>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-semibold text-slate-900">
                  {isEditMode ? '编辑文章' : 'AI 创作'}
                </h1>
                {newsSource && (
                  <span className="px-2 py-0.5 rounded-md bg-orange-50 text-orange-600 text-xs font-medium">
                    📰 {newsSource.source || '热点'}
                  </span>
                )}
              </div>
            </div>
            
            {step === 'preview' && (
              <div className="flex items-center gap-2">
                <button
                  onClick={handleManualQualityCheck}
                  disabled={isSaving || isQualityChecking}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-50 text-emerald-700 text-sm font-medium hover:bg-emerald-100 disabled:opacity-50 transition-colors"
                >
                  {isQualityChecking ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
                  质检
                </button>
                <button onClick={handleSaveDraft} disabled={isSaving} className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 disabled:opacity-50 transition-colors">
                  <Save className="w-4 h-4" />
                  保存
                </button>
                <button onClick={handlePublish} disabled={isSaving} className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-violet-500 text-white text-sm font-medium hover:bg-violet-600 disabled:opacity-50 transition-colors">
                  <Send className="w-4 h-4" />
                  发布
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-6">
        {/* 步骤指示器 */}
        {step === 'preview' && (
          <div className="flex items-center gap-1.5 mb-6">
            {[
              { id: 'input', label: '主题' },
              { id: 'titles', label: '标题' },
              { id: 'preview', label: '编辑' },
            ].map((s, index, arr) => {
              const isActive = step === s.id
              const isCompleted = arr.findIndex(x => x.id === step) > index
              return (
                <div key={s.id} className="flex items-center">
                  <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    isActive ? 'bg-violet-500 text-white' :
                    isCompleted ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-400'
                  }`}>
                    {isCompleted && <Check className="w-3.5 h-3.5" />}
                    {s.label}
                  </div>
                  {index < arr.length - 1 && (
                    <div className={`w-4 h-0.5 mx-1 ${isCompleted ? 'bg-emerald-500' : 'bg-slate-200'}`} />
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* 输入步骤 */}
        {step === 'input' && (
          <div className="space-y-4">
            {/* AI 模型选择 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">AI 模型</h3>
                  <p className="text-xs text-slate-500">选择智能写作引擎</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {aiModels.map((model) => (
                  <button
                    key={model.id}
                    onClick={() => setAiModel(model.id)}
                    className={`p-3 rounded-xl border-2 text-center transition-all ${
                      aiModel === model.id 
                        ? 'border-violet-500 bg-violet-50' 
                        : 'border-slate-100 hover:border-slate-200'
                    }`}
                  >
                    <div className="text-xl mb-1">{model.icon}</div>
                    <div className="text-sm font-medium text-slate-900">{model.name}</div>
                    <div className="text-xs text-slate-400">{model.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {generationError && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {generationError}
              </div>
            )}

            {/* 写作风格 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center">
                  <PenTool className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">写作风格</h3>
                  <p className="text-xs text-slate-500">选择内容风格</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {writingStyles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => setWritingStyle(style.id)}
                    className={`p-3 rounded-xl border-2 text-center transition-all ${
                      writingStyle === style.id 
                        ? 'border-violet-500 bg-violet-50' 
                        : 'border-slate-100 hover:border-slate-200'
                    }`}
                  >
                    <div className="text-xl mb-1">{style.icon}</div>
                    <div className="text-sm font-medium text-slate-900">{style.name}</div>
                    <div className="text-xs text-slate-400">{style.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* 主题输入 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center">
                  <Type className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">文章主题</h3>
                  <p className="text-xs text-slate-500">输入想要创作的内容方向</p>
                </div>
              </div>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="例如：AI大模型在内容创作领域的最新应用..."
                className="w-full h-28 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100 resize-none text-sm leading-relaxed"
              />
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleGenerateTitles}
                  disabled={isGenerating || !topic.trim()}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
                >
                  {isGenerating ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> 生成中...</>
                  ) : (
                    <><Sparkles className="w-4 h-4" /> 生成标题</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 标题选择步骤 */}
        {step === 'titles' && (
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                  <FileText className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">选择标题</h3>
                  <p className="text-xs text-slate-500">可勾选 1~2 个标题，生成单篇或 A/B 双版本</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleScoreSelectedTitles}
                  disabled={isScoringTitle || selectedTitleCandidates.length === 0}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-emerald-700 bg-emerald-50 hover:bg-emerald-100 disabled:opacity-50"
                >
                  {isScoringTitle ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  智能评分
                </button>
                <button
                  onClick={handleGenerateTitles}
                  disabled={isGenerating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-violet-600 bg-violet-50 hover:bg-violet-100 disabled:opacity-50"
                >
                  {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                  重新生成
                </button>
                <button onClick={() => setStep('input')} className="px-3 py-1.5 rounded-lg text-sm text-slate-500 hover:bg-slate-100">
                  返回修改
                </button>
              </div>
            </div>

            <div className="mb-3 flex items-center gap-2 text-xs">
              <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                已选择 {selectedTitleCandidates.length} / 2
              </span>
              {selectedTitleCandidates.map((title, index) => (
                <span key={title} className="px-2 py-0.5 rounded-md bg-violet-50 text-violet-600">
                  {index === 0 ? 'A' : 'B'} · {title}
                </span>
              ))}
            </div>
            
            <div className="space-y-2">
              {generatedTitles.map((item, index) => (
                <button
                  key={index}
                  onClick={() => handleSelectTitle(item.title)}
                  disabled={isGenerating}
                  className={`group w-full p-4 rounded-xl border transition-all text-left ${
                    selectedTitleCandidates.includes(item.title)
                      ? 'border-violet-300 bg-violet-50/50'
                      : 'border-slate-100 hover:border-violet-300 hover:bg-violet-50/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-lg bg-violet-100 text-violet-600 flex items-center justify-center font-medium text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-slate-900 group-hover:text-violet-600 truncate">
                        {item.title}
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">{item.reason}</p>
                    </div>
                    {selectedTitleCandidates.includes(item.title) && (
                      <div className="px-2 py-1 rounded-md text-xs font-medium bg-violet-100 text-violet-700">
                        {selectedTitleCandidates.indexOf(item.title) === 0 ? 'A' : 'B'}
                      </div>
                    )}
                    <div className={`px-2 py-1 rounded-md text-xs font-medium ${
                      item.score >= 90 ? 'bg-emerald-50 text-emerald-600' :
                      item.score >= 80 ? 'bg-blue-50 text-blue-600' :
                      'bg-amber-50 text-amber-600'
                    }`}>
                      {item.score}分
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-violet-500 transition-colors" />
                  </div>
                </button>
              ))}
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={generateContentFromCandidates}
                disabled={isGenerating || selectedTitleCandidates.length === 0}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium hover:opacity-90 disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4" />
                    {selectedTitleCandidates.length === 1 ? '生成正文' : '生成 A/B 双版本'}
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* 预览编辑步骤 */}
        {step === 'preview' && generatedContent && (
          <div className="space-y-4">
            {/* 基本信息 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="w-4 h-4 text-slate-400" />
                <label className="text-sm font-medium text-slate-500">文章标题</label>
              </div>
              <input
                type="text"
                value={generatedContent.title}
                onChange={(e) => handleTitleChange(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 font-semibold text-lg focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
              />

              <div className="mt-3 flex items-center gap-2">
                <button
                  onClick={handleScoreCurrentTitle}
                  disabled={isScoringTitle}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-emerald-50 text-emerald-700 hover:bg-emerald-100 disabled:opacity-50"
                >
                  {isScoringTitle ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                  标题评分
                </button>

                <button
                  onClick={handleOptimizeCurrentTitle}
                  disabled={isScoringTitle}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm bg-violet-50 text-violet-700 hover:bg-violet-100 disabled:opacity-50"
                >
                  {isScoringTitle ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  一键优化标题
                </button>

                {activeTitleScore && (
                  <div className="flex items-center gap-2 text-xs text-slate-600">
                    <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700">
                      评分 {Math.round(activeTitleScore.score)}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700">
                      点击率 {Math.round(activeTitleScore.click_rate)}%
                    </span>
                    <span className="text-slate-500 truncate max-w-[360px]">{activeTitleScore.analysis}</span>
                  </div>
                )}
              </div>

              {(activeTitleScore?.suggestions?.length ?? 0) > 0 && (
                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                  {(activeTitleScore?.suggestions ?? []).slice(0, 3).map((item) => (
                    <span key={item} className="px-2 py-1 rounded-md bg-slate-100 text-slate-600">
                      {item}
                    </span>
                  ))}
                </div>
              )}

              {contentVariants.length > 1 && (
                <div className="mt-4 rounded-xl border border-violet-100 bg-violet-50/50 p-3">
                  <div className="text-xs text-violet-700 mb-2">已生成标题 A/B 两个版本，可快速切换对比</div>
                  <div className="flex flex-wrap gap-2">
                    {contentVariants.map((variant) => (
                      <button
                        key={variant.key}
                        onClick={() => handleVariantSwitch(variant.key)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                          activeVariantKey === variant.key
                            ? 'bg-violet-500 text-white'
                            : 'bg-white text-violet-700 border border-violet-200 hover:bg-violet-100'
                        }`}
                      >
                        {variant.key} 版 · {variant.title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {/* 封面图 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <ImageIcon className="w-4 h-4 text-slate-400" />
                      <label className="text-sm text-slate-500">封面图</label>
                    </div>
                    {isEditMode && (
                      <button
                        onClick={async () => {
                          if (!confirm('确定要重新生成封面图吗？') || !editArticleId) return
                          setIsGenerating(true)
                          try {
                            const result = await fetch(`${API_URL}/api/articles/${editArticleId}/generate-cover`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ topic: generatedContent.title, style: 'professional' })
                            })
                            if (result.ok) {
                              const data = await result.json()
                              setCoverImageUrl(data.cover_image_url)
                              alert('封面图生成成功！')
                            } else { alert('生成失败') }
                          } catch (error) { alert('生成失败') }
                          finally { setIsGenerating(false) }
                        }}
                        disabled={isGenerating}
                        className="flex items-center gap-1 px-2 py-1 rounded-lg bg-violet-50 text-violet-600 text-xs font-medium hover:bg-violet-100"
                      >
                        {isGenerating ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                        重新生成
                      </button>
                    )}
                  </div>
                  {coverImageUrl ? (
                    <div className="relative group rounded-xl overflow-hidden h-32">
                      <img src={coverImageUrl.startsWith('http') ? coverImageUrl : `${API_URL}/${coverImageUrl}`} alt="封面" className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <button onClick={() => setCoverImageUrl('')} className="px-3 py-1.5 rounded-lg bg-white text-red-500 text-xs font-medium">删除</button>
                      </div>
                    </div>
                  ) : (
                    <div className="h-32 rounded-xl bg-slate-50 border-2 border-dashed border-slate-200 flex flex-col items-center justify-center gap-1">
                      <ImageIcon className="w-6 h-6 text-slate-300" />
                      <p className="text-xs text-slate-400">暂无封面</p>
                    </div>
                  )}
                </div>

                {/* 摘要 */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-4 h-4 text-slate-400" />
                    <label className="text-sm text-slate-500">文章摘要</label>
                  </div>
                  <textarea
                    value={generatedContent.summary || ''}
                    onChange={(e) => handleSummaryChange(e.target.value)}
                    placeholder="输入文章摘要..."
                    className="w-full h-32 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-sm resize-none focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                  />
                </div>
              </div>
            </div>

            {/* 正文内容 */}
            <div className="bg-white rounded-2xl border border-slate-200 p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <PenTool className="w-4 h-4 text-slate-400" />
                  <label className="text-sm font-medium text-slate-500">正文内容</label>
                </div>
                <div className="inline-flex items-center rounded-lg border border-slate-200 p-1 bg-slate-50">
                  <button
                    onClick={() => setEditorMode('plain')}
                    className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                      editorMode === 'plain' ? 'bg-white text-slate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    Markdown
                  </button>
                  <button
                    onClick={() => setEditorMode('rich')}
                    className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                      editorMode === 'rich' ? 'bg-white text-slate-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    富文本
                  </button>
                </div>
              </div>

              {editorMode === 'rich' ? (
                <RichEditor
                  content={editingContent}
                  onChange={handleContentChange}
                />
              ) : (
                <textarea
                  value={editingContent}
                  onChange={(e) => handleContentChange(e.target.value)}
                  className="w-full h-96 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 resize-none font-mono text-sm leading-relaxed focus:outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-100"
                />
              )}
            </div>

            {/* 质量评分 */}
            {generatedContent.qualityScore && (
              <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-2xl p-4 border border-violet-100">
                <div className="flex items-center gap-4">
                  <div className="text-center min-w-[60px]">
                    <div className={`text-3xl font-bold ${getScoreColor(generatedContent.qualityScore)}`}>
                      {generatedContent.qualityScore}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5 font-medium">质量分</div>
                  </div>
                  <div className="flex-1">
                    <div className="h-2 bg-white/60 rounded-full overflow-hidden">
                      <div className={`h-full ${getScoreBgColor(generatedContent.qualityScore)} rounded-full transition-all`} style={{ width: `${generatedContent.qualityScore}%` }} />
                    </div>
                    <p className="text-xs text-slate-600 mt-2">
                      {generatedContent.qualityScore >= 90 ? '质量优秀，可直接发布' :
                       generatedContent.qualityScore >= 80 ? '质量良好，建议微调' :
                       generatedContent.qualityScore >= 70 ? '质量尚可，建议优化' : '需要进一步修改'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {qualityCheck && (
              <div className={`rounded-2xl border p-4 ${qualityCheck.pass ? 'bg-emerald-50 border-emerald-100' : 'bg-amber-50 border-amber-100'}`}>
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    {qualityCheck.pass ? (
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <ShieldAlert className="w-4 h-4 text-amber-600" />
                    )}
                    <p className="text-sm font-medium text-slate-800">
                      {qualityCheck.pass ? '发布前质检已通过' : '发布前质检待处理'}
                    </p>
                  </div>
                  <p className="text-xs text-slate-500">
                    {new Date(qualityCheck.checkedAt).toLocaleString('zh-CN')}
                  </p>
                </div>

                {qualityCheck.titleScore && (
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded-md bg-white text-slate-700 border border-slate-200">
                      标题评分 {Math.round(qualityCheck.titleScore.score)}
                    </span>
                    <span className="px-2 py-0.5 rounded-md bg-white text-slate-700 border border-slate-200">
                      预估点击率 {Math.round(qualityCheck.titleScore.click_rate)}%
                    </span>
                    <span className="text-slate-600">{qualityCheck.titleScore.analysis}</span>
                  </div>
                )}

                {qualityCheck.blockingIssues.length > 0 && (
                  <div className="mt-3 space-y-1 text-sm text-rose-600">
                    {qualityCheck.blockingIssues.map((issue) => (
                      <p key={issue} className="flex items-start gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 mt-0.5" />
                        <span>{issue}</span>
                      </p>
                    ))}
                  </div>
                )}

                {qualityCheck.formatWarnings.length > 0 && (
                  <div className="mt-3 space-y-1 text-xs text-amber-700">
                    {qualityCheck.formatWarnings.map((warning) => (
                      <p key={warning}>• {warning}</p>
                    ))}
                  </div>
                )}

                {qualityCheck.hasSensitive && qualityCheck.sensitiveCount > 0 && (
                  <div className="mt-3 flex items-center justify-between gap-3 rounded-xl bg-white/70 border border-amber-200 px-3 py-2">
                    <p className="text-xs text-amber-700">
                      检测到 {qualityCheck.sensitiveCount} 处敏感词，建议自动替换后再发布。
                    </p>
                    <button
                      onClick={applySensitiveReplacement}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-amber-100 text-amber-700 hover:bg-amber-200"
                    >
                      一键替换
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
