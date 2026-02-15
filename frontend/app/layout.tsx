"use client"

import './globals.css'
import { useEffect } from 'react'
import ResizableSidebar from '@/components/layout/resizable-sidebar'
import Header from '@/components/layout/header'
import Notifications from '@/components/ui/notifications'
import { OnboardingProvider } from '@/components/onboarding/onboarding-provider'
import { initGlobalClientErrorReporter } from '@/lib/client-error-reporter'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    initGlobalClientErrorReporter()
  }, [])

  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="antialiased font-sans">
        <OnboardingProvider>
          <div className="flex h-screen overflow-hidden bg-[#F5F5F7]">
            <ResizableSidebar />
            <div className="flex-1 flex flex-col overflow-hidden min-w-0">
              <Header />
              <main className="flex-1 overflow-y-auto overflow-x-hidden">
                {children}
              </main>
            </div>
          </div>
          <Notifications />
        </OnboardingProvider>
      </body>
    </html>
  )
}
