/**
 * 富文本编辑器组件
 * 基于TipTap，支持图片拖拽上传、Markdown快捷输入
 */

'use client'

import { useEditor, EditorContent, BubbleMenu, FloatingMenu } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { 
  Bold, 
  Italic, 
  List, 
  ListOrdered, 
  Quote, 
  Link as LinkIcon,
  Image as ImageIcon,
  Heading1,
  Heading2,
  Undo,
  Redo,
  Code,
  Maximize2
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

interface RichEditorProps {
  content: string
  onChange: (content: string) => void
  placeholder?: string
}

export default function RichEditor({ 
  content, 
  onChange, 
  placeholder = '开始写作...' 
}: RichEditorProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const editor = useEditor({
    extensions: [
      StarterKit,
    ],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
  })

  useEffect(() => {
    if (!editor) return

    const normalizedContent = content || '<p></p>'
    if (editor.getHTML() === normalizedContent) return

    // 同步外部内容到编辑器，避免 A/B 切换后仍显示旧内容
    editor.commands.setContent(normalizedContent, false)
  }, [content, editor])

  // 处理图片上传
  const handleImageUpload = useCallback(async (file: File) => {
    if (!editor) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        editor.chain().focus().insertContent(`<img src="${data.url}" alt="image" />`).run()
      }
    } catch (error) {
      console.error('图片上传失败:', error)
    }
  }, [editor])

  // 处理拖拽
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    
    const files = Array.from(e.dataTransfer.files)
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        handleImageUpload(file)
      }
    })
  }, [handleImageUpload])

  // 添加链接
  const addLink = useCallback(() => {
    if (!editor) return
    
    const url = window.prompt('输入链接地址:')
    if (url) {
      editor.chain().focus().insertContent(`<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`).run()
    }
  }, [editor])

  // 添加图片
  const addImage = useCallback(() => {
    if (!editor) return
    
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        await handleImageUpload(file)
      }
    }
    input.click()
  }, [handleImageUpload])

  if (!editor) {
    return null
  }

  return (
    <div 
      className={`border rounded-lg overflow-hidden ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      {/* 工具栏 */}
      <div className="flex items-center gap-1 p-2 border-b bg-gray-50 flex-wrap">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          icon={<Bold className="w-4 h-4" />}
          title="加粗 (Ctrl+B)"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          icon={<Italic className="w-4 h-4" />}
          title="斜体 (Ctrl+I)"
        />
        <div className="w-px h-6 bg-gray-300 mx-1" />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          isActive={editor.isActive('heading', { level: 1 })}
          icon={<Heading1 className="w-4 h-4" />}
          title="标题1"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive('heading', { level: 2 })}
          icon={<Heading2 className="w-4 h-4" />}
          title="标题2"
        />
        <div className="w-px h-6 bg-gray-300 mx-1" />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          icon={<List className="w-4 h-4" />}
          title="无序列表"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          icon={<ListOrdered className="w-4 h-4" />}
          title="有序列表"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          isActive={editor.isActive('blockquote')}
          icon={<Quote className="w-4 h-4" />}
          title="引用"
        />
        <div className="w-px h-6 bg-gray-300 mx-1" />
        <ToolbarButton
          onClick={addLink}
          isActive={editor.isActive('link')}
          icon={<LinkIcon className="w-4 h-4" />}
          title="添加链接"
        />
        <ToolbarButton
          onClick={addImage}
          icon={<ImageIcon className="w-4 h-4" />}
          title="添加图片"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          isActive={editor.isActive('codeBlock')}
          icon={<Code className="w-4 h-4" />}
          title="代码块"
        />
        <div className="flex-1" />
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          icon={<Undo className="w-4 h-4" />}
          title="撤销"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          icon={<Redo className="w-4 h-4" />}
          title="重做"
        />
        <ToolbarButton
          onClick={() => setIsFullscreen(!isFullscreen)}
          isActive={isFullscreen}
          icon={<Maximize2 className="w-4 h-4" />}
          title="全屏"
        />
      </div>

      {/* 编辑器内容 */}
      <EditorContent 
        editor={editor} 
        className={`prose max-w-none p-4 ${isFullscreen ? 'h-[calc(100vh-60px)] overflow-y-auto' : 'min-h-[300px]'}`}
      />

      {/* 气泡菜单 */}
      {editor && (
        <BubbleMenu editor={editor} tippyOptions={{ duration: 100 }}>
          <div className="flex items-center gap-1 p-1 bg-gray-900 rounded-lg shadow-lg">
            <ToolbarButton
              onClick={() => editor.chain().focus().toggleBold().run()}
              isActive={editor.isActive('bold')}
              icon={<Bold className="w-4 h-4 text-white" />}
            />
            <ToolbarButton
              onClick={() => editor.chain().focus().toggleItalic().run()}
              isActive={editor.isActive('italic')}
              icon={<Italic className="w-4 h-4 text-white" />}
            />
            <ToolbarButton
              onClick={addLink}
              isActive={editor.isActive('link')}
              icon={<LinkIcon className="w-4 h-4 text-white" />}
            />
          </div>
        </BubbleMenu>
      )}

      {/* 浮动菜单 */}
      {editor && (
        <FloatingMenu editor={editor} tippyOptions={{ duration: 100 }}>
          <div className="flex items-center gap-1 p-1 bg-gray-900 rounded-lg shadow-lg">
            <ToolbarButton
              onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
              isActive={editor.isActive('heading', { level: 1 })}
              icon={<Heading1 className="w-4 h-4 text-white" />}
            />
            <ToolbarButton
              onClick={() => editor.chain().focus().toggleBulletList().run()}
              isActive={editor.isActive('bulletList')}
              icon={<List className="w-4 h-4 text-white" />}
            />
            <ToolbarButton
              onClick={addImage}
              icon={<ImageIcon className="w-4 h-4 text-white" />}
            />
          </div>
        </FloatingMenu>
      )}

      {/* 字数统计 */}
      <div className="flex items-center justify-between px-4 py-2 border-t bg-gray-50 text-sm text-gray-500">
        <span>
          {editor.storage.characterCount?.characters() || 0} 字符
        </span>
        <span>
          {editor.storage.characterCount?.words() || 0} 词
        </span>
      </div>
    </div>
  )
}

// 工具栏按钮组件
interface ToolbarButtonProps {
  onClick: () => void
  isActive?: boolean
  disabled?: boolean
  icon: React.ReactNode
  title?: string
}

function ToolbarButton({ onClick, isActive, disabled, icon, title }: ToolbarButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`p-2 rounded transition-colors ${
        isActive 
          ? 'bg-blue-100 text-blue-600' 
          : 'hover:bg-gray-200 text-gray-700'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {icon}
    </button>
  )
}
