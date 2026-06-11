import { Switch, Route, Router as WouterRouter } from 'wouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthGuard } from '@/components/auth-guard';
import Home from '@/pages/home';
import SearchPage from '@/pages/search';
import PapersPage from '@/pages/papers';
import TrendingPage from '@/pages/trending';
import PaperDetailPage from '@/pages/paper-detail';
import DashboardPage from '@/pages/dashboard';
import FeedPage from '@/pages/feed';
import GraphPage from '@/pages/graph';
import WorkspacePage from '@/pages/workspace';
import ProfilePage from '@/pages/profile';
import NotFound from '@/pages/not-found';

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

function Guarded({ component: Page }: { component: React.ComponentType }) {
  return <AuthGuard><Page /></AuthGuard>;
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/search"    component={() => <Guarded component={SearchPage} />} />
      <Route path="/papers"    component={() => <Guarded component={PapersPage} />} />
      <Route path="/trending"  component={() => <Guarded component={TrendingPage} />} />
      <Route path="/paper/:id" component={() => <Guarded component={PaperDetailPage} />} />
      <Route path="/dashboard" component={() => <Guarded component={DashboardPage} />} />
      <Route path="/feed"      component={() => <Guarded component={FeedPage} />} />
      <Route path="/graph"     component={() => <Guarded component={GraphPage} />} />
      <Route path="/workspace" component={() => <Guarded component={WorkspacePage} />} />
      <Route path="/profile"   component={() => <Guarded component={ProfilePage} />} />
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
        <Router />
      </WouterRouter>
    </QueryClientProvider>
  );
}
