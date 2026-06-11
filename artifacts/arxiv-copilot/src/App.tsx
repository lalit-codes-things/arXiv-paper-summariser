import { Switch, Route, Router as WouterRouter } from 'wouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
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
import LoginPage from '@/pages/login';
import NotFound from '@/pages/not-found';

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/search" component={SearchPage} />
      <Route path="/papers" component={PapersPage} />
      <Route path="/trending" component={TrendingPage} />
      <Route path="/paper/:id" component={PaperDetailPage} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/feed" component={FeedPage} />
      <Route path="/graph" component={GraphPage} />
      <Route path="/workspace" component={WorkspacePage} />
      <Route path="/profile" component={ProfilePage} />
      <Route path="/login" component={LoginPage} />
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
