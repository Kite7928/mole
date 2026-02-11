'use client'

import { Sun, Moon } from 'lucide-react'
import { useThemeStore } from '@/lib/theme-store'

export default function BrightnessControl() {
  const { theme, toggleTheme } = useThemeStore()

  return (
    <button
      onClick={toggleTheme}
      className="p-2.5 rounded-xl hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors light:text-slate-700 dark:text-slate-300 light:hover:text-slate-900 dark:hover:text-white touch-friendly"
      title="切换主题"
    >
      {theme === 'dark' ? <Sun size={22} /> : <Moon size={22} />}
    </button>
  )
}