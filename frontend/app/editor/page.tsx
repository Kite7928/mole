'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import {
  Save,
  Eye,
  Upload,
  Image as ImageIcon,
  Code,
  Type,
  AlignLeft,
  Bold,
  Italic,
  Link,
  List,
  Quote,
  CheckSquare,
  X,
  GitBranch,
  Download,
  Copy,
} from 'lucide-react'

export default function MarkdownEditorPage() {
  const [content, setContent] = useState('')
  const [previewHtml, setPreviewHtml] = useState('')
  const [activeTab, setActiveTab] = useState<'editor' | 'preview' | 'split'>('split')
  const [theme, setTheme] = useState('default')
  const [wordCount, setWordCount] = useState(0)
  const [charCount, setCharCount] = useState(0)
  const [lineCount, setLineCount] = useState(0)

  useEffect(() => {
    // Calculate statistics
    const lines = content.split('\n')
    setWordCount(content.trim().split(/\s+/).filter(w => w).length)
    setCharCount(content.length)
    setLineCount(lines.length)

    // Generate preview (simplified)
    const html = convertMarkdownToHtml(content)
    setPreviewHtml(html)
  }, [content])

  const convertMarkdownToHtml = (markdown: string) => {
    // Simple Markdown to HTML conversion
    let html = markdown

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')

    // Bold and Italic
    html = html.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    html = html.replace(/\*(.*)\*/gim, '<em>$1</em>')

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank">$1</a>')

    // Images
    html = html.replace(/!\[(.*?)\]\((.*?)\)/gim, '<img src="$2" alt="$1" style="max-width:100%;height:auto;display:block;margin:1em auto;" />')

    // Code blocks
    html = html.replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')

    // Inline code
    html = html.replace(/`([^`]+)`/gim, '<code style="background:#f5f5f5;padding:2px 4px;border-radius:3px;">$1</code>')

    // Blockquotes
    html = html.replace(/^> (.*$)/gim, '<blockquote style="border-left:4px solid #576b95;padding-left:1em;color:#666;">$1</blockquote>')

    // Lists
    html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>')

    // Paragraphs
    html = html.replace(/\n\n/g, '</p><p>')
    html = '<p>' + html + '</p>'

    // Line breaks
    html = html.replace(/\n/g, '<br>')

    return html
  }

  const insertMarkdown = (prefix: string, suffix: string = '') => {
    const textarea = document.querySelector('textarea') as HTMLTextAreaElement
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = content.substring(start, end)

    const newText = content.substring(0, start) + prefix + selectedText + suffix + content.substring(end)
    setContent(newText)

    // Restore focus and cursor position
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(start + prefix.length, start + prefix.length + selectedText.length)
    }, 0)
  }

  const handleImageUpload = async () => {
    // Trigger file input
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        // TODO: Upload to image bed
        const reader = new FileReader()
        reader.onload = (e) => {
          const imageData = e.target?.result as string
          insertMarkdown(`![${file.name}](${imageData})`)
        }
        reader.readAsDataURL(file)
      }
    }
    input.click()
  }

  const handleSave = () => {
    // TODO: Save to backend
    alert('文章已保存')
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(previewHtml)
    alert('HTML 已复制到剪贴板')
  }

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `article-${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Code className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Markdown 编辑器</h1>
                <p className="text-sm text-muted-foreground">专业的 Markdown 编辑和预览</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="mr-2 h-4 w-4" />
                下载
              </Button>
              <Button variant="outline" size="sm" onClick={handleCopy}>
                <Copy className="mr-2 h-4 w-4" />
                复制 HTML
              </Button>
              <Button size="sm" onClick={handleSave}>
                <Save className="mr-2 h-4 w-4" />
                保存
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Toolbar */}
      <div className="border-b border-border bg-muted/50">
        <div className="container mx-auto px-4 py-2">
          <div className="flex items-center space-x-2 flex-wrap">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('**', '**')}
              title="粗体"
            >
              <Bold className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('*', '*')}
              title="斜体"
            >
              <Italic className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('[', '](url)')}
              title="链接"
            >
              <Link className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleImageUpload}
              title="图片"
            >
              <ImageIcon className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('`', '`')}
              title="行内代码"
            >
              <Code className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('```\n', '\n```')}
              title="代码块"
            >
              <Type className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('- ', '')}
              title="无序列表"
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('> ', '')}
              title="引用"
            >
              <Quote className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('# ', '')}
              title="标题 1"
            >
              H1
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('## ', '')}
              title="标题 2"
            >
              H2
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => insertMarkdown('### ', '')}
              title="标题 3"
            >
              H3
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid gap-4 lg:grid-cols-3">
          {/* Editor Panel */}
          <div className={activeTab === 'split' ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>编辑器</CardTitle>
                    <CardDescription>使用 Markdown 语法编写内容</CardDescription>
                  </div>
                  <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
                    <TabsList>
                      <TabsTrigger value="editor">编辑</TabsTrigger>
                      <TabsTrigger value="preview">预览</TabsTrigger>
                      <TabsTrigger value="split">分屏</TabsTrigger>
                    </TabsList>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {activeTab === 'editor' || activeTab === 'split' ? (
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="开始编写你的文章...&#10;&#10;# 标题&#10;&#10;这是一段正文。&#10;&#10;## 子标题&#10;&#10;- 列表项 1&#10;- 列表项 2&#10;&#10;```python&#10;代码块&#10;```"
                    className="w-full h-[600px] px-3 py-2 bg-input border border-border rounded-md font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                ) : null}
              </CardContent>
            </Card>
          </div>

          {/* Preview Panel */}
          {activeTab === 'preview' || activeTab === 'split' ? (
            <div className={activeTab === 'split' ? 'lg:col-span-1' : 'lg:col-span-3'}>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>预览</CardTitle>
                      <CardDescription>实时预览文章效果</CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      <select
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                        className="px-3 py-1 bg-input border border-border rounded-md text-sm"
                      >
                        <option value="default">默认主题</option>
                        <option value="blue">蓝色主题</option>
                        <option value="green">绿色主题</option>
                        <option value="purple">紫色主题</option>
                        <option value="dark">暗黑主题</option>
                      </select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div
                    className="prose prose-sm max-w-none h-[600px] overflow-y-auto p-4 border rounded-md bg-background"
                    dangerouslySetInnerHTML={{ __html: previewHtml }}
                  />
                </CardContent>
              </Card>
            </div>
          ) : null}

          {/* Statistics Panel */}
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>统计信息</CardTitle>
                <CardDescription>文章内容统计</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{wordCount}</div>
                    <div className="text-sm text-muted-foreground">字数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{charCount}</div>
                    <div className="text-sm text-muted-foreground">字符数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{lineCount}</div>
                    <div className="text-sm text-muted-foreground">行数</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}