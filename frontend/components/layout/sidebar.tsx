'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTheme } from 'next-themes'
import {
  FileText,
  Flame,
  Send,
  Settings,
  PenTool,
  Menu,
  X,
  Sparkles,
  Sun,
  Moon,
  Home,
  BarChart3,
  Calendar,
  BookOpen,
  Lightbulb,
  Wand2
} from 'lucide-react'
import { useState, useEffect } from 'react'

const navigation = [
  { name: '首页', href: '/', icon: Home },
  { name: 'AI写作', href: '/articles/create', icon: PenTool },
  { name: 'AI工具', href: '/ai-tools', icon: Wand2 },
  { name: '文章管理', href: '/articles', icon: FileText },
  { name: '系列文章', href: '/series', icon: BookOpen },
  { name: '选题库', href: '/topic-ideas', icon: Lightbulb },
  { name: '热点监控', href: '/hotspots', icon: Flame },
  { name: '内容日历', href: '/content-calendar', icon: Calendar },
  { name: '数据洞察', href: '/analytics', icon: BarChart3 },
  { name: '系统设置', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const toggleTheme = () => {
    if (theme === 'system') {
      setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
    } else {
      setTheme(theme === 'dark' ? 'light' : 'dark')
    }
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2.5 rounded-xl bg-primary text-primary-foreground shadow-lg shadow-primary/30"
      >
        {isCollapsed ? <Menu size={24} /> : <X size={24} />}
      </button>

      {/* Sidebar */}
      <aside
        className={`
          fixed left-0 top-0 h-screen w-64 lg:w-72 z-40
          transition-all duration-300 ease-smooth
          ${isCollapsed ? '-translate-x-full' : 'translate-x-0'}
          lg:translate-x-0
          bg-background border-r border-border
          flex flex-col
        `}
      >
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
              <Sparkles size={20} className="text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-foreground">
                AI写作助手
              </h1>
              <p className="text-xs text-foreground-secondary mt-0.5">
                智能创作平台
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto" data-tour="sidebar">
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg
                  transition-all duration-200 ease-smooth
                  ${isActive
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-foreground-secondary hover:text-foreground hover:bg-muted'
                  }
                `}
              >
                <Icon size={20} className={isActive ? 'text-primary' : ''} />
                <span>{item.name}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-primary" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* Bottom Section */}
        <div className="p-4 border-t border-border space-y-3">
          {/* Theme Toggle */}
          {mounted && (
            <button
              onClick={toggleTheme}
              className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg bg-muted hover:bg-muted/80 transition-colors text-sm text-foreground-secondary"
            >
              {resolvedTheme === 'dark' ? (
                <>
                  <Sun size={18} className="text-orange-500" />
                  <span>亮色模式</span>
                </>
              ) : (
                <>
                  <Moon size={18} className="text-primary" />
                  <span>暗色模式</span>
                </>
              )}
            </button>
          )}

          {/* User Info */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
            <div className="w-9 h-9 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-semibold text-sm">
              U
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm text-foreground truncate">用户</p>
              <p className="text-xs text-foreground-tertiary">管理员</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {!isCollapsed && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden"
          onClick={() => setIsCollapsed(true)}
        />
      )}
    </>
  )
}
