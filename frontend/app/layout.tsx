import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import ResizableSidebar from '@/components/layout/resizable-sidebar'
import Header from '@/components/layout/header'
import Notifications from '@/components/ui/notifications'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI公众号自动写作助手 Pro',
  description: '基于AI的智能微信公众号内容生成与发布系统',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" className="light">
      <body className={inter.className}>
        <div className="tyndall-effect"></div>
        <div className="flex h-screen overflow-hidden relative z-10">
          <ResizableSidebar />
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            <Header />
            <main className="flex-1 overflow-y-auto overflow-x-hidden">
              <div className="p-4 md:p-6 lg:p-8 max-w-[2560px] mx-auto w-full">
                {children}
              </div>
            </main>
          </div>
        </div>
        <Notifications />
      </body>
    </html>
  )
}