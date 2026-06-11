import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/research/shell';
import { Card, CardContent } from '@/components/ui/card';
import { v3 } from '@/lib/api';

export default function ProfilePage() {
  const { data } = useQuery({
    queryKey: ['profile'],
    queryFn: () => v3.userProfile('anonymous'),
  });
  return (
    <AppShell>
      <h1 className="text-4xl font-semibold">Your research profile</h1>
      <p className="mt-2 text-zinc-400">Topics and interests learned from your reading history.</p>
      {data && (
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <Card>
            <CardContent className="p-5">
              <h2 className="font-medium mb-4">Interests</h2>
              <div className="flex flex-wrap gap-2">
                {data.interests.map((interest) => (
                  <span
                    key={interest}
                    className="rounded-full border border-indigo-400/30 bg-indigo-400/10 px-3 py-1 text-sm text-indigo-200"
                  >
                    {interest}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-5">
              <h2 className="font-medium mb-4">Topic activity</h2>
              <div className="space-y-2">
                {Object.entries(data.topic_clusters)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 10)
                  .map(([topic, count]) => (
                    <div key={topic} className="flex items-center justify-between">
                      <span className="text-sm text-zinc-300">{topic}</span>
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 rounded-full bg-white/10">
                          <div
                            className="h-full rounded-full bg-indigo-400"
                            style={{ width: `${Math.min(100, count * 10)}%` }}
                          />
                        </div>
                        <span className="text-xs text-zinc-500">{count}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
