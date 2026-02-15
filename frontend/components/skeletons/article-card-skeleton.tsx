import { Skeleton } from '@/components/ui/skeleton'

export default function ArticleCardSkeleton() {
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl border border-gray-200 p-4">
      <div className="flex items-start gap-4">
        {/* Drag Handle */}
        <div className="flex items-center gap-2 pt-1">
          <Skeleton className="w-5 h-5 rounded" />
          <Skeleton className="w-6 h-6 rounded" />
        </div>

        {/* Thumbnail */}
        <div className="w-32 h-20 rounded-lg bg-gradient-to-br from-gray-100 to-gray-200">
          <Skeleton className="w-full h-full rounded-lg" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title Row */}
          <div className="flex items-start gap-3 mb-2">
            <Skeleton className="h-6 w-3/4 rounded" />
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>

          {/* Tags */}
          <div className="flex items-center gap-2 mb-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>

          {/* Stats Row */}
          <div className="flex items-center gap-6">
            <Skeleton className="h-5 w-16 rounded" />
            <Skeleton className="h-5 w-12 rounded" />
          </div>
        </div>

        {/* Time */}
        <div className="flex flex-col items-end gap-1">
          <Skeleton className="h-5 w-24 rounded" />
          <Skeleton className="h-4 w-20 rounded" />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1">
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
          <Skeleton className="w-10 h-10 rounded-lg" />
        </div>
      </div>
    </div>
  )
}

export function ArticleCardSkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <ArticleCardSkeleton key={i} />
      ))}
    </div>
  )
}