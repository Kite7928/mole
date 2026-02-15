'use client'

import { useState } from 'react'
import { Star, TrendingUp, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { API_URL } from '@/lib/api'

interface TitleScore {
  score: number
  click_rate: number
  analysis: string
  dimensions: {
    [key: string]: number
  }
  suggestions: string[]
}

interface TitleScorerProps {
  title: string
  topic?: string
}

export default function TitleScorer({ title, topic }: TitleScorerProps) {
  const [score, setScore] = useState<TitleScore | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScore = async () => {
    if (!title.trim()) {
      setError('请输入标题')
      return
    }

    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${API_URL}/api/ai/score-title`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, topic })
      })

      if (!response.ok) {
        throw new Error('评分失败')
      }

      const data = await response.json()
      setScore(data)
    } catch (err) {
      setError('评分服务暂时不可用，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500'
    if (score >= 60) return 'text-amber-500'
    return 'text-rose-500'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-500'
    if (score >= 60) return 'bg-amber-500'
    return 'bg-rose-500'
  }

  const getClickRateColor = (rate: number) => {
    if (rate >= 15) return 'text-emerald-500'
    if (rate >= 8) return 'text-amber-500'
    return 'text-rose-500'
  }

  return (
    <div className="space-y-4">
      {/* 评分按钮 */}
      <button
        onClick={handleScore}
        disabled={loading || !title.trim()}
        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            评分中...
          </>
        ) : (
          <>
            <Star size={18} />
            智能评分
          </>
        )}
      </button>

      {/* 错误提示 */}
      {error && (
        <div className="flex items-center gap-2 text-rose-500 text-sm">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* 评分结果 */}
      {score && !loading && (
        <div className="bg-white/80 backdrop-blur rounded-xl border border-slate-200 p-5 space-y-4">
          {/* 总分和点击率 */}
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className={`text-5xl font-bold ${getScoreColor(score.score)}`}>
                {score.score}
              </div>
              <div className="text-sm text-slate-500 mt-1">总分(100)</div>
            </div>
            
            <div className="h-16 w-px bg-slate-200" />
            
            <div className="text-center">
              <div className={`text-4xl font-bold ${getClickRateColor(score.click_rate)}`}>
                {score.click_rate}%
              </div>
              <div className="text-sm text-slate-500 mt-1 flex items-center gap-1">
                <TrendingUp size={14} />
                预估点击率
              </div>
            </div>

            <div className="flex-1">
              <div className="text-sm text-slate-600 leading-relaxed">
                {score.analysis}
              </div>
            </div>
          </div>

          {/* 维度评分 */}
          <div className="space-y-2">
            <div className="text-sm font-medium text-slate-700">各维度评分</div>
            <div className="grid grid-cols-5 gap-2">
              {Object.entries(score.dimensions).map(([dim, value]) => (
                <div key={dim} className="text-center p-2 bg-slate-50 rounded-lg">
                  <div className={`text-lg font-bold ${getScoreColor(value * 5)}`}>
                    {value}
                  </div>
                  <div className="text-xs text-slate-500">{dim}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 进度条 */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">标题质量</span>
              <span className={`font-medium ${getScoreColor(score.score)}`}>
                {score.score >= 80 ? '优秀' : score.score >= 60 ? '良好' : '需优化'}
              </span>
            </div>
            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getScoreBg(score.score)} transition-all duration-500`}
                style={{ width: `${score.score}%` }}
              />
            </div>
          </div>

          {/* 优化建议 */}
          {score.suggestions.length > 0 && (
            <div className="space-y-2">
              <div className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <CheckCircle size={16} className="text-indigo-500" />
                优化建议
              </div>
              <ul className="space-y-1.5">
                {score.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-slate-600 flex items-start gap-2">
                    <span className="text-indigo-500 mt-0.5">•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
