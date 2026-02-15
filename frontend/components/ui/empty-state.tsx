'use client'

import { ReactNode } from 'react'
import { FileText, Plus, Sparkles } from 'lucide-react'
import { Button } from './button'
import Link from 'next/link'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description: string
  action?: {
    label: string
    href: string
    icon?: ReactNode
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({
  icon = <FileText className="w-12 h-12" />,
  title,
  description,
  action,
  secondaryAction
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center mb-6 text-gray-600">
        {icon}
      </div>
      
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-500 max-w-md mb-6">{description}</p>
      
      <div className="flex gap-3">
        {action && (
          <Link href={action.href}>
            <Button className="bg-blue-600 hover:bg-blue-700">
              {action.icon || <Plus className="w-4 h-4 mr-2" />}
              {action.label}
            </Button>
          </Link>
        )}
        
        {secondaryAction && (
          <Button
            variant="outline"
            onClick={secondaryAction.onClick}
            className="border-white/10"
          >
            {secondaryAction.label}
          </Button>
        )}
      </div>
    </div>
  )
}

// 预定义的空状态
export function EmptyArticles() {
  return (
    <EmptyState
      icon={<FileText className="w-12 h-12" />}
      title="还没有文章"
      description="创建你的第一篇文章，开始使用 AI 写作功能"
      action={{
        label: '立即创建',
        href: '/articles/create',
        icon: <Plus className="w-4 h-4 mr-2" />
      }}
    />
  )
}

export function EmptyHotspots() {
  return (
    <EmptyState
      icon={<Sparkles className="w-12 h-12" />}
      title="暂无热点数据"
      description="选择平台和时间范围，获取最新热点话题"
      action={{
        label: '刷新数据',
        href: '/hotspots',
        icon: <Sparkles className="w-4 h-4 mr-2" />
      }}
    />
  )
}
