'use client'

import { useState, useEffect } from 'react'
import { Image, Check, Loader2 } from 'lucide-react'

interface ImageStyle {
  value: string
  label: string
  description: string
  icon: string
}

interface ImageStyleSelectorProps {
  value: string
  onChange: (style: string) => void
  disabled?: boolean
}

const defaultStyles: ImageStyle[] = [
  { value: 'professional', label: '专业商务', description: '简洁大气，适合职场和商业场景', icon: '💼' },
  { value: 'creative', label: '创意艺术', description: '色彩丰富，充满想象力', icon: '🎨' },
  { value: 'minimal', label: '极简风格', description: '留白充足，突出主题', icon: '⬜' },
  { value: 'vibrant', label: '鲜艳活力', description: '色彩明快，充满能量', icon: '🌈' },
  { value: 'tech', label: '科技感', description: '未来主义，数字化元素', icon: '🔬' },
  { value: 'nature', label: '自然生态', description: '清新自然，绿色环保', icon: '🌿' },
  { value: 'chinese', label: '中国风', description: '水墨画风格，传统文化', icon: '🎋' },
  { value: 'cartoon', label: '卡通插画', description: '可爱生动，适合轻松话题', icon: '🎭' },
  { value: 'realistic', label: '写实摄影', description: '真实自然，高清晰度', icon: '📷' },
]

export function ImageStyleSelector({ value, onChange, disabled }: ImageStyleSelectorProps) {
  const [styles, setStyles] = useState<ImageStyle[]>(defaultStyles)
  const [loading, setLoading] = useState(false)

  // 可选：从后端获取风格列表
  useEffect(() => {
    const fetchStyles = async () => {
      try {
        const response = await fetch('/api/articles/0/images/styles')
        if (response.ok) {
          const data = await response.json()
          if (Array.isArray(data) && data.length > 0) {
            setStyles(data)
          }
        }
      } catch (error) {
        // 使用默认风格
        console.log('使用默认风格列表')
      }
    }
    
    fetchStyles()
  }, [])

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        选择图片风格
      </label>
      <div className="grid grid-cols-3 gap-3">
        {styles.map((style) => (
          <button
            key={style.value}
            onClick={() => onChange(style.value)}
            disabled={disabled}
            className={`relative p-4 rounded-xl border-2 text-left transition-all duration-200 ${
              value === style.value
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {/* 选中标记 */}
            {value === style.value && (
              <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                <Check className="w-3 h-3 text-white" />
              </div>
            )}
            
            {/* 图标 */}
            <div className="text-2xl mb-2">{style.icon}</div>
            
            {/* 标签 */}
            <div className={`font-medium text-sm ${
              value === style.value ? 'text-blue-900' : 'text-gray-900'
            }`}>
              {style.label}
            </div>
            
            {/* 描述 */}
            <div className={`text-xs mt-1 ${
              value === style.value ? 'text-blue-600' : 'text-gray-500'
            }`}>
              {style.description}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

// 生成数量选择器
interface ImageCountSelectorProps {
  value: number
  onChange: (count: number) => void
  disabled?: boolean
  maxCount?: number
}

export function ImageCountSelector({ 
  value, 
  onChange, 
  disabled,
  maxCount = 5 
}: ImageCountSelectorProps) {
  const options = [1, 2, 3, 4, 5].filter(n => n <= maxCount)
  
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        生成图片数量
      </label>
      <div className="flex gap-2">
        {options.map((count) => (
          <button
            key={count}
            onClick={() => onChange(count)}
            disabled={disabled}
            className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
              value === count
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300 text-gray-600'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {count}张
          </button>
        ))}
      </div>
      <p className="text-xs text-gray-500">
        包括1张封面图 + {value - 1}张段落配图
      </p>
    </div>
  )
}

// 生成按钮组件
interface GenerateButtonProps {
  onClick: () => void
  loading?: boolean
  disabled?: boolean
  hasExistingImages?: boolean
}

export function GenerateImagesButton({
  onClick,
  loading,
  disabled,
  hasExistingImages
}: GenerateButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
        hasExistingImages
          ? 'bg-amber-100 text-amber-700 hover:bg-amber-200 border-2 border-amber-300'
          : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-lg hover:shadow-xl'
      } ${disabled || loading ? 'opacity-70 cursor-not-allowed' : ''}`}
    >
      {loading ? (
        <>
          <Loader2 className="w-5 h-5 animate-spin" />
          生成中...
        </>
      ) : (
        <>
          <Image className="w-5 h-5" />
          {hasExistingImages ? '重新生成配图' : 'AI生成配图'}
        </>
      )}
    </button>
  )
}
