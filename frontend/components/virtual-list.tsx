/**
 * 虚拟滚动列表组件
 * 用于大数据量文章列表的性能优化
 */

'use client'

import { useMemo } from 'react'

interface VirtualListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  itemHeight: number
  loadMoreItems?: () => Promise<void>
  hasMore?: boolean
  overscanCount?: number
}

export default function VirtualList<T>({
  items,
  renderItem,
  itemHeight: _itemHeight,
  loadMoreItems,
  hasMore = false,
  overscanCount = 5,
}: VirtualListProps<T>) {
  const visibleItems = useMemo(() => items, [items])

  const handleLoadMore = async () => {
    if (loadMoreItems) {
      await loadMoreItems()
    }
  }

  return (
    <div className="h-[600px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
      {visibleItems.map((item, index) => (
        <div key={index} className="px-4">
          {renderItem(item, index)}
        </div>
      ))}
      {hasMore && (
        <div className="py-4 text-center">
          <button
            onClick={handleLoadMore}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            加载更多
          </button>
        </div>
      )}
    </div>
  )
}
