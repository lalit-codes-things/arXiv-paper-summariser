import { cn } from '@/lib/utils';

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-xl bg-white/5', className)} />;
}

export function PaperCardSkeleton() {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="flex gap-2 mb-3"><Skeleton className="h-5 w-16" /><Skeleton className="h-5 w-20" /></div>
      <Skeleton className="h-6 w-3/4 mb-2" />
      <Skeleton className="h-4 w-full mb-1" />
      <Skeleton className="h-4 w-5/6 mb-3" />
      <Skeleton className="h-3 w-1/3" />
    </div>
  );
}
