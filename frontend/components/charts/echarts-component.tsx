/**
 * ECharts可视化组件
 * 支持多种图表类型和交互
 */

'use client'

import { useEffect, useRef, useState } from 'react'
import * as echarts from 'echarts'
import { Loader2 } from 'lucide-react'

type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'radar' | 'heatmap' | 'wordcloud'

interface EChartsComponentProps {
  type: ChartType
  data: any
  height?: number
  loading?: boolean
  onClick?: (params: any) => void
}

export default function EChartsComponent({
  type,
  data,
  height = 300,
  loading = false,
  onClick
}: EChartsComponentProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (chartRef.current && !chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
      
      if (onClick) {
        chartInstance.current.on('click', onClick)
      }
      
      setIsReady(true)
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
        chartInstance.current = null
      }
    }
  }, [onClick])

  useEffect(() => {
    if (!chartInstance.current || !data) return

    const option = generateOption(type, data)
    chartInstance.current.setOption(option, true)
  }, [type, data])

  // 响应式处理
  useEffect(() => {
    const handleResize = () => {
      chartInstance.current?.resize()
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  if (loading) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-50 rounded-lg"
        style={{ height }}
      >
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div 
      ref={chartRef} 
      className="w-full"
      style={{ height }}
    />
  )
}

// 生成图表配置
function generateOption(type: ChartType, data: any): echarts.EChartsOption {
  const baseOption: echarts.EChartsOption = {
    tooltip: {
      trigger: type === 'pie' ? 'item' : 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      textStyle: {
        color: '#374151'
      },
      extraCssText: 'box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-radius: 8px;'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    }
  }

  switch (type) {
    case 'line':
    case 'area':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: data.labels,
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisLabel: { color: '#6b7280' }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLabel: { color: '#6b7280' }
        },
        series: data.datasets.map((dataset: any, index: number) => ({
          name: dataset.label,
          type: 'line',
          data: dataset.data,
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: {
            width: 3,
            color: dataset.borderColor || getColor(index)
          },
          itemStyle: {
            color: dataset.borderColor || getColor(index),
            borderWidth: 2,
            borderColor: '#fff'
          },
          areaStyle: type === 'area' ? {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: hexToRgba(dataset.borderColor || getColor(index), 0.3) },
              { offset: 1, color: hexToRgba(dataset.borderColor || getColor(index), 0.05) }
            ])
          } : undefined
        }))
      }

    case 'bar':
      return {
        ...baseOption,
        xAxis: {
          type: 'category',
          data: data.labels,
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisLabel: { color: '#6b7280' }
        },
        yAxis: {
          type: 'value',
          axisLine: { show: false },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLabel: { color: '#6b7280' }
        },
        series: data.datasets.map((dataset: any, index: number) => ({
          name: dataset.label,
          type: 'bar',
          data: dataset.data,
          barWidth: '60%',
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: dataset.backgroundColor || getColor(index) },
              { offset: 1, color: hexToRgba(dataset.backgroundColor || getColor(index), 0.7) }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }))
      }

    case 'pie':
      return {
        ...baseOption,
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '50%'],
          data: data.labels.map((label: string, index: number) => ({
            name: label,
            value: data.datasets[0].data[index]
          })),
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}\n{d}%',
            color: '#374151'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            }
          }
        }]
      }

    case 'radar':
      return {
        ...baseOption,
        radar: {
          indicator: data.labels.map((label: string, index: number) => ({
            name: label,
            max: Math.max(...data.datasets[0].data) * 1.2
          })),
          shape: 'polygon',
          splitNumber: 4,
          axisName: {
            color: '#6b7280'
          },
          splitLine: {
            lineStyle: {
              color: '#e5e7eb'
            }
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['#f9fafb', '#f3f4f6']
            }
          }
        },
        series: [{
          type: 'radar',
          data: data.datasets.map((dataset: any, index: number) => ({
            name: dataset.label,
            value: dataset.data,
            itemStyle: { color: dataset.borderColor || getColor(index) },
            areaStyle: {
              color: hexToRgba(dataset.borderColor || getColor(index), 0.2)
            }
          }))
        }]
      }

    default:
      return baseOption
  }
}

// 辅助函数
function getColor(index: number): string {
  const colors = [
    '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#22c55e',
    '#3b82f6', '#ef4444', '#14b8a6', '#f97316', '#84cc16'
  ]
  return colors[index % colors.length]
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}