'use client'

import React from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
  fill?: boolean
  tension?: number
}

export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'area'
  title: string
  labels: string[]
  datasets: ChartDataset[]
  options?: {
    responsive?: boolean
    maintainAspectRatio?: boolean
    plugins?: {
      legend?: {
        display?: boolean
        position?: 'top' | 'bottom' | 'left' | 'right'
      }
      title?: {
        display?: boolean
        text?: string
      }
    }
  }
}

interface DataChartProps {
  data: ChartData
  height?: number
}

// 默认颜色
const DEFAULT_COLORS = [
  '#6366f1', // indigo
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#22c55e', // green
  '#3b82f6', // blue
  '#f59e0b', // amber
  '#ef4444', // red
  '#14b8a6', // teal
]

export default function DataChart({ data, height = 300 }: DataChartProps) {
  // 数据验证
  if (!data || !data.labels || !Array.isArray(data.labels) || data.labels.length === 0) {
    return (
      <div className="w-full bg-[#1A1D24] border border-gray-800 rounded-xl p-6 text-center">
        <div className="text-gray-500 text-sm">暂无数据</div>
      </div>
    )
  }

  if (!data.datasets || !Array.isArray(data.datasets) || data.datasets.length === 0) {
    return (
      <div className="w-full bg-[#1A1D24] border border-gray-800 rounded-xl p-6 text-center">
        <div className="text-gray-500 text-sm">暂无数据集</div>
      </div>
    )
  }

  // 转换数据格式为 recharts 需要的格式
  const chartData = data.labels.map((label, index) => {
    const item: Record<string, string | number> = { name: label }
    data.datasets.forEach((dataset) => {
      item[dataset.label] = dataset.data?.[index] ?? 0
    })
    return item
  })

  // 饼图数据特殊处理
  const pieData = data.labels.map((label, index) => ({
    name: label,
    value: data.datasets[0]?.data?.[index] ?? 0
  }))

  const renderChart = () => {
    switch (data.type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} />
              <YAxis tick={{ fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  color: '#e2e8f0'
                }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              {data.datasets.map((dataset, index) => (
                <Bar
                  key={dataset.label}
                  dataKey={dataset.label}
                  fill={Array.isArray(dataset.backgroundColor) ? dataset.backgroundColor[0] : (dataset.backgroundColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length])}
                  stroke={Array.isArray(dataset.borderColor) ? dataset.borderColor[0] : (dataset.borderColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length])}
                  strokeWidth={dataset.borderWidth || 0}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} />
              <YAxis tick={{ fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  color: '#e2e8f0'
                }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              {data.datasets.map((dataset, index) => {
                const strokeColor = Array.isArray(dataset.borderColor) ? dataset.borderColor[0] : (dataset.borderColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length])
                return (
                  <Line
                    key={dataset.label}
                    type="monotone"
                    dataKey={dataset.label}
                    stroke={strokeColor}
                    strokeWidth={dataset.borderWidth || 2}
                    dot={{ fill: strokeColor, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                )
              })}
            </LineChart>
          </ResponsiveContainer>
        )

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} />
              <YAxis tick={{ fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  color: '#e2e8f0'
                }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              {data.datasets.map((dataset, index) => {
                const strokeColor = Array.isArray(dataset.borderColor) ? dataset.borderColor[0] : (dataset.borderColor || DEFAULT_COLORS[index % DEFAULT_COLORS.length])
                const fillColor = Array.isArray(dataset.backgroundColor) ? dataset.backgroundColor[0] : (dataset.backgroundColor || `${DEFAULT_COLORS[index % DEFAULT_COLORS.length]}33`)
                return (
                  <Area
                    key={dataset.label}
                    type="monotone"
                    dataKey={dataset.label}
                    stroke={strokeColor}
                    fill={fillColor}
                    strokeWidth={dataset.borderWidth || 2}
                  />
                )
              })}
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      Array.isArray(data.datasets[0]?.backgroundColor)
                        ? data.datasets[0].backgroundColor[index % data.datasets[0].backgroundColor.length]
                        : DEFAULT_COLORS[index % DEFAULT_COLORS.length]
                    }
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(30, 41, 59, 0.95)',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  color: '#e2e8f0'
                }}
                itemStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )

      default:
        return <div>不支持的图表类型: {data.type}</div>
    }
  }

  return (
    <div className="w-full bg-transparent rounded-xl border-0 p-0">
      {data.title && (
        <h3 className="text-lg font-semibold text-gray-300 text-center mb-4">
          {data.title}
        </h3>
      )}
      <div className="w-full">
        {renderChart()}
      </div>
    </div>
  )
}
