'use client'

import React, { useState } from 'react'
import { X, BarChart3, PieChart, LineChart, AreaChart, Loader2, Wand2 } from 'lucide-react'
import { apiRequest } from '@/lib/api'
import DataChart, { ChartData } from './data-chart'

interface ChartGeneratorProps {
  isOpen: boolean
  onClose: () => void
  onInsert: (chartData: ChartData) => void
  topic?: string
}

const CHART_TYPES = [
  { value: 'bar', label: '柱状图', icon: BarChart3 },
  { value: 'line', label: '折线图', icon: LineChart },
  { value: 'pie', label: '饼图', icon: PieChart },
  { value: 'area', label: '面积图', icon: AreaChart },
]

export default function ChartGenerator({ isOpen, onClose, onInsert, topic }: ChartGeneratorProps) {
  const [chartType, setChartType] = useState('bar')
  const [title, setTitle] = useState('')
  const [dataText, setDataText] = useState('')
  const [generatedChart, setGeneratedChart] = useState<ChartData | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError('')

    try {
      let response

      if (dataText.trim()) {
        // 从文本解析数据
        response = await apiRequest('/charts/parse', {
          method: 'POST',
          body: JSON.stringify({
            text: dataText,
            chart_type: chartType
          })
        })
      } else if (topic) {
        // 生成示例数据
        response = await apiRequest('/charts/sample', {
          method: 'POST',
          body: JSON.stringify({ topic })
        })
      } else {
        setError('请输入数据或提供主题')
        return
      }

      if (response.success && response.data) {
        setGeneratedChart(response.data)
      } else {
        setError(response.message || '生成失败')
      }
    } catch (err) {
      setError('生成图表时出错')
      console.error(err)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleInsert = () => {
    if (generatedChart) {
      onInsert(generatedChart)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-xl font-semibold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-600" />
            生成数据图表
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        <div className="flex h-[calc(90vh-80px)]">
          {/* 左侧：配置面板 */}
          <div className="w-1/2 p-6 border-r border-slate-200 overflow-y-auto">
            {/* 图表类型选择 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-3">
                图表类型
              </label>
              <div className="grid grid-cols-2 gap-3">
                {CHART_TYPES.map((type) => {
                  const Icon = type.icon
                  return (
                    <button
                      key={type.value}
                      onClick={() => setChartType(type.value)}
                      className={`flex items-center gap-2 p-3 rounded-xl border transition-all ${
                        chartType === type.value
                          ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                          : 'border-slate-200 hover:border-indigo-300 hover:bg-slate-50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{type.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* 图表标题 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                图表标题
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="例如：2024年销售数据"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all"
              />
            </div>

            {/* 数据输入 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-slate-700 mb-2">
                数据（可选）
              </label>
              <p className="text-xs text-slate-500 mb-2">
                支持 CSV 格式：标签,数值（每行一个）或留空自动生成示例数据
              </p>
              <textarea
                value={dataText}
                onChange={(e) => setDataText(e.target.value)}
                placeholder={`例如：
第一季度,120
第二季度,180
第三季度,240
第四季度,320`}
                rows={8}
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all resize-none font-mono text-sm"
              />
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* 生成按钮 */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || (!dataText.trim() && !topic)}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  生成中...
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  生成图表
                </>
              )}
            </button>
          </div>

          {/* 右侧：预览面板 */}
          <div className="w-1/2 p-6 bg-slate-50 overflow-y-auto">
            <h3 className="text-sm font-medium text-slate-700 mb-4">预览</h3>
            
            {generatedChart ? (
              <div className="space-y-4">
                <DataChart data={generatedChart} height={350} />
                
                <button
                  onClick={handleInsert}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all font-medium"
                >
                  插入到文章
                </button>
              </div>
            ) : (
              <div className="h-[400px] flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
                <BarChart3 className="w-16 h-16 mb-4 opacity-50" />
                <p>配置参数并点击生成按钮</p>
                <p className="text-sm mt-1">图表将在这里预览</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
