import { Switch, Route, Router as WouterRouter } from 'wouter';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import NotFound from '@/pages/not-found';
import Home from '@/pages/home';
import DashboardPage from '@/pages/dashboard';
import FeedPage from '@/pages/feed';
import PapersPage from '@/pages/papers';
import PaperDetailPage from '@/pages/paper-detail';
import SearchPage from '@/pages/search';
import TrendingPage from '@/pages/trending';
import GraphPage from '@/pages/graph';
import WorkspacePage from '@/pages/workspace';
import ProfilePage from '@/pages/profile';
import LoginPage from '@/pages/login';

const queryClient = new QueryClient();

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/dashboard" component={DashboardPage} />
      <Route path="/feed" component={FeedPage} />
      <Route path="/papers" component={PapersPage} />
      <Route path="/papers/detail" component={PaperDetailPage} />
      <Route path="/search" component={SearchPage} />
      <Route path="/trending" component={TrendingPage} />
      <Route path="/graph" component={GraphPage} />
      <Route path="/workspace" component={WorkspacePage} />
      <Route path="/profile" component={ProfilePage} />
      <Route path="/login" component={LoginPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
        <Router />
      </WouterRouter>
    </QueryClientProvider>
  );
}

export default App;
