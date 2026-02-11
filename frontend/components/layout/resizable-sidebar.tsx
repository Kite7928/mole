'use client'

import { useState, useEffect, useRef } from 'react'
import {
  PenTool,
  FileText,
  Flame,
  Send,
  Settings,
  X,
  ChevronLeft,
  ChevronRight,
  Menu
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

interface ResizableSidebarProps {
  defaultWidth?: number
  minWidth?: number
  maxWidth?: number
}

export default function ResizableSidebar({ 
  defaultWidth = 280,
  minWidth = 220,
  maxWidth = 400 
}: ResizableSidebarProps) {
  const [width, setWidth] = useState(defaultWidth)
  const [isResizing, setIsResizing] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const sidebarRef = useRef<HTMLDivElement>(null)
  const pathname = usePathname()

  // 响应式处理
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) {
        setIsMobileOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // 拖动处理
  const handleMouseDown = (e: React.MouseEvent) => {
    if (window.innerWidth < 1024) return // 移动端禁用拖动
    setIsResizing(true)
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return
      if (!sidebarRef.current) return

      const newWidth = e.clientX
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing, minWidth, maxWidth])

  // 双击折叠/展开
  const handleDoubleClick = () => {
    if (window.innerWidth < 1024) return
    setIsCollapsed(!isCollapsed)
    setWidth(isCollapsed ? defaultWidth : 64)
  }

  // 移动端菜单
  const toggleMobileMenu = () => {
    setIsMobileOpen(!isMobileOpen)
  }

  const navItems = [
    { icon: PenTool, label: 'AI写作', href: '/articles/create' },
    { icon: FileText, label: '文章管理', href: '/articles' },
    { icon: Flame, label: '热点监控', href: '/hotspots' },
    { icon: Settings, label: '系统设置', href: '/settings' },
  ]

  return (
    <>
      {/* 移动端遮罩 */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={toggleMobileMenu}
        />
      )}

      {/* 侧边栏 */}
      <aside
        ref={sidebarRef}
        className={`
          fixed lg:relative z-50 lg:z-0 h-screen transition-all duration-300
          light:bg-gradient-to-b light:from-indigo-50 light:via-purple-50 light:to-indigo-50
          dark:bg-gradient-to-b dark:from-indigo-900 dark:via-purple-900 dark:to-indigo-900
          backdrop-blur-xl relative
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        style={{ width: isCollapsed ? '64px' : width }}
      >
        {/* 侧边栏过渡光晕 */}
        <div className="sidebar-glow" />
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 light:border-b light:border-indigo-200/50 dark:border-b dark:border-indigo-700/50 relative z-10">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <PenTool size={20} className="text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-base font-bold light:text-indigo-900 dark:text-indigo-50 leading-tight">AI写作助手</h1>
                <p className="text-xs light:text-indigo-600 dark:text-indigo-400 mt-0.5">Pro</p>
              </div>
            </div>
          )}
          
          {/* 移动端关闭按钮 */}
          <button
            onClick={toggleMobileMenu}
            className="lg:hidden p-2 rounded-lg light:hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors light:text-indigo-700 dark:text-indigo-200"
          >
            <X size={20} />
          </button>

          {/* 桌面端折叠按钮 */}
          <button
            onClick={handleDoubleClick}
            className="hidden lg:block p-2 rounded-lg light:hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors light:text-indigo-700 dark:text-indigo-200"
          >
            {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1 relative z-10">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsMobileOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 touch-friendly
                  ${isActive 
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/30' 
                    : 'light:text-indigo-700 dark:text-indigo-200 light:hover:bg-indigo-100/50 dark:hover:bg-indigo-800/50 light:hover:text-indigo-900 dark:hover:text-indigo-100'
                  }
                `}
              >
                <Icon size={22} className="flex-shrink-0" />
                {!isCollapsed && (
                  <span className="text-base font-medium hidden sm:block">{item.label}</span>
                )}
                {isActive && !isCollapsed && (
                  <div className="ml-auto w-2 h-2 rounded-full bg-white shadow-lg shadow-white/50" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* 用户信息 */}
        <div className="light:border-t light:border-indigo-200/50 dark:border-t dark:border-indigo-700/50 p-4 relative z-10">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold flex-shrink-0 shadow-lg shadow-indigo-500/30">
                U
              </div>
              <div className="hidden sm:block min-w-0 flex-1">
                <p className="text-sm font-semibold light:text-indigo-900 dark:text-indigo-50 truncate">用户名</p>
                <p className="text-xs light:text-indigo-600 dark:text-indigo-400 truncate">超级管理员</p>
              </div>
            </div>
          )}
          {isCollapsed && (
            <div className="flex justify-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/30">
                U
              </div>
            </div>
          )}
        </div>

        {/* 拖动手柄 */}
        <div
          className={`
            absolute top-0 right-0 w-1.5 h-full cursor-col-resize hover:bg-indigo-500/40 
            transition-colors hidden lg:block z-20
            ${isResizing ? 'bg-indigo-500/60' : ''}
          `}
          onMouseDown={handleMouseDown}
          onDoubleClick={handleDoubleClick}
        />
      </aside>

      {/* 移动端菜单按钮 */}
      <button
        onClick={toggleMobileMenu}
        className="lg:hidden fixed bottom-6 right-6 z-50 p-4 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/30"
      >
        {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>
    </>
  )
}