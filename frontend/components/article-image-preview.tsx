'use client'

import { useState } from 'react'
import { Image, RefreshCw, Eye, EyeOff, GripVertical, Trash2, Check, X } from 'lucide-react'

interface ImagePosition {
  position: string
  type: 'cover' | 'paragraph'
  title: string
  description?: string
  priority: number
  url?: string
  prompt?: string
  status: 'pending' | 'generating' | 'completed' | 'failed'
}

interface ArticleImagePreviewProps {
  title: string
  content: string
  positions: ImagePosition[]
  onRegenerate?: (position: string) => void
  onTogglePosition?: (position: string, enabled: boolean) => void
  onReorder?: (positions: ImagePosition[]) => void
  readonly?: boolean
}

export function ArticleImagePreview({
  title,
  content,
  positions,
  onRegenerate,
  onTogglePosition,
  onReorder,
  readonly = false
}: ArticleImagePreviewProps) {
  const [expandedPosition, setExpandedPosition] = useState<string | null>(null)
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null)

  const coverImage = positions.find(p => p.type === 'cover')
  const paragraphImages = positions.filter(p => p.type === 'paragraph')

  // 解析文章内容，显示图片位置
  const renderContentWithImages = () => {
    const lines = content.split('\n')
    const result: JSX.Element[] = []
    let paragraphIndex = 0

    lines.forEach((line, index) => {
      // 检测标题
      if (line.startsWith('## ') || line.startsWith('# ')) {
        // 在标题前插入封面图（如果是第一个标题）
        if (paragraphIndex === 0 && coverImage) {
          result.push(
            <ImageSlot
              key="cover"
              position={coverImage}
              type="cover"
              onRegenerate={onRegenerate}
              readonly={readonly}
            />
          )
        }
        
        result.push(
          <h2 key={`h-${index}`} className="text-xl font-bold text-gray-900 mt-8 mb-4">
            {line.replace(/^#+\s+/, '')}
          </h2>
        )

        // 在标题后插入段落配图
        const paragraphImage = paragraphImages[paragraphIndex]
        if (paragraphImage) {
          result.push(
            <ImageSlot
              key={paragraphImage.position}
              position={paragraphImage}
              type="paragraph"
              onRegenerate={onRegenerate}
              readonly={readonly}
            />
          )
          paragraphIndex++
        }
      } else if (line.trim()) {
        result.push(
          <p key={`p-${index}`} className="text-gray-700 mb-4 leading-relaxed">
            {line}
          </p>
        )
      }
    })

    return result
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
      {/* 头部信息 */}
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <h3 className="font-semibold text-gray-900">配图预览</h3>
        <p className="text-sm text-gray-500 mt-1">
          共 {positions.length} 张图片（封面 {coverImage ? 1 : 0} 张 + 段落配图 {paragraphImages.length} 张）
        </p>
      </div>

      {/* 文章内容预览 */}
      <div className="p-6 max-h-96 overflow-y-auto">
        {renderContentWithImages()}
      </div>
    </div>
  )
}

// 图片位置插槽组件
interface ImageSlotProps {
  position: ImagePosition
  type: 'cover' | 'paragraph'
  onRegenerate?: (position: string) => void
  readonly?: boolean
}

function ImageSlot({ position, type, onRegenerate, readonly }: ImageSlotProps) {
  const [showPrompt, setShowPrompt] = useState(false)

  const isCover = type === 'cover'
  
  return (
    <div className={`my-6 ${isCover ? '' : 'ml-4'}`}>
      {/* 图片卡片 */}
      <div className={`relative rounded-xl border-2 overflow-hidden ${
        position.status === 'completed' && position.url
          ? 'border-green-200 bg-green-50'
          : position.status === 'generating'
          ? 'border-blue-200 bg-blue-50'
          : position.status === 'failed'
          ? 'border-red-200 bg-red-50'
          : 'border-gray-200 bg-gray-50'
      }`}>
        {/* 状态标签 */}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            position.status === 'completed' ? 'bg-green-100 text-green-700' :
            position.status === 'generating' ? 'bg-blue-100 text-blue-700' :
            position.status === 'failed' ? 'bg-red-100 text-red-700' :
            'bg-gray-100 text-gray-600'
          }`}>
            {position.status === 'completed' ? '✓ 已完成' :
             position.status === 'generating' ? '⟳ 生成中' :
             position.status === 'failed' ? '✗ 失败' :
             '○ 待生成'}
          </span>
          <span className="px-2 py-1 rounded-full text-xs font-medium bg-white/80 text-gray-600">
            {isCover ? '封面图' : '段落配图'}
          </span>
        </div>

        {/* 图片内容 */}
        <div className={`flex items-center justify-center ${isCover ? 'h-48' : 'h-32'}`}>
          {position.status === 'completed' && position.url ? (
            <img
              src={position.url}
              alt={position.title}
              className="w-full h-full object-cover"
            />
          ) : position.status === 'generating' ? (
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-2" />
              <p className="text-sm text-gray-500">AI正在创作...</p>
            </div>
          ) : (
            <div className="text-center">
              <Image className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">{position.title}</p>
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        {!readonly && position.status !== 'generating' && (
          <div className="absolute top-3 right-3 flex gap-1">
            {position.status === 'completed' && (
              <button
                onClick={() => setShowPrompt(!showPrompt)}
                className="p-2 rounded-lg bg-white/80 hover:bg-white text-gray-600 hover:text-gray-900 transition-colors"
                title="查看提示词"
              >
                {showPrompt ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            )}
            <button
              onClick={() => onRegenerate?.(position.position)}
              className="p-2 rounded-lg bg-white/80 hover:bg-white text-gray-600 hover:text-blue-600 transition-colors"
              title="重新生成"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* 提示词展示 */}
      {showPrompt && position.prompt && (
        <div className="mt-2 p-3 bg-gray-100 rounded-lg text-sm text-gray-600">
          <p className="font-medium text-gray-700 mb-1">生成提示词：</p>
          <p className="line-clamp-3">{position.prompt}</p>
        </div>
      )}
    </div>
  )
}

// 图片位置列表（用于手动调整）
interface ImagePositionListProps {
  positions: ImagePosition[]
  onReorder: (positions: ImagePosition[]) => void
  onToggle: (position: string, enabled: boolean) => void
}

export function ImagePositionList({ positions, onReorder, onToggle }: ImagePositionListProps) {
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null)

  const handleDragStart = (index: number) => {
    setDraggingIndex(index)
  }

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault()
    if (draggingIndex === null || draggingIndex === index) return

    const newPositions = [...positions]
    const draggedItem = newPositions[draggingIndex]
    newPositions.splice(draggingIndex, 1)
    newPositions.splice(index, 0, draggedItem)
    
    onReorder(newPositions)
    setDraggingIndex(index)
  }

  const handleDragEnd = () => {
    setDraggingIndex(null)
  }

  return (
    <div className="space-y-2">
      {positions.map((position, index) => (
        <div
          key={position.position}
          draggable
          onDragStart={() => handleDragStart(index)}
          onDragOver={(e) => handleDragOver(e, index)}
          onDragEnd={handleDragEnd}
          className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-move transition-all ${
            draggingIndex === index
              ? 'border-blue-300 bg-blue-50 opacity-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          <GripVertical className="w-5 h-5 text-gray-400" />
          
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-lg">{position.type === 'cover' ? '📰' : '🖼️'}</span>
              <span className="font-medium text-gray-900">{position.title}</span>
            </div>
            {position.description && (
              <p className="text-sm text-gray-500 mt-1 line-clamp-1">
                {position.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded text-xs ${
              position.type === 'cover'
                ? 'bg-purple-100 text-purple-700'
                : 'bg-blue-100 text-blue-700'
            }`}>
              {position.type === 'cover' ? '封面' : '段落'}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}