import { useEffect, useRef } from "react";
import { Switch, Route, useLocation, Router as WouterRouter, Redirect } from 'wouter';
import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import { ClerkProvider, SignIn, SignUp, Show, useClerk } from '@clerk/react';
import { publishableKeyFromHost } from '@clerk/react/internal';
import { shadcn } from '@clerk/themes';
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

const clerkPubKey = publishableKeyFromHost(
  window.location.hostname,
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
);

const clerkProxyUrl = import.meta.env.VITE_CLERK_PROXY_URL;

const basePath = import.meta.env.BASE_URL.replace(/\/$/, "");

function stripBase(path: string): string {
  return basePath && path.startsWith(basePath)
    ? path.slice(basePath.length) || "/"
    : path;
}

if (!clerkPubKey) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY');
}

const clerkAppearance = {
  theme: shadcn,
  cssLayerName: "clerk",
  options: {
    logoPlacement: "inside" as const,
    logoLinkUrl: basePath || "/",
    logoImageUrl: `${window.location.origin}${basePath}/logo.svg`,
    socialButtonsPlacement: "top" as const,
    socialButtonsVariant: "blockButton" as const,
  },
  variables: {
    colorPrimary: "#191A23",
    colorForeground: "#191A23",
    colorMutedForeground: "#898989",
    colorDanger: "#ef4444",
    colorBackground: "#ffffff",
    colorInput: "#ffffff",
    colorInputForeground: "#191A23",
    colorNeutral: "#191A23",
    fontFamily: "'Space Grotesk', sans-serif",
    borderRadius: "12px",
  },
  elements: {
    rootBox: "w-full flex justify-center",
    cardBox: "bg-white border border-[#191A23] rounded-2xl w-[440px] max-w-full overflow-hidden shadow-[4px_4px_0_#191A23]",
    card: "!shadow-none !border-0 !bg-transparent !rounded-none",
    footer: "!shadow-none !border-0 !bg-transparent !rounded-none",
    headerTitle: "text-[#191A23] font-bold",
    headerSubtitle: "text-[#898989]",
    socialButtonsBlockButtonText: "text-[#191A23] font-medium",
    formFieldLabel: "text-[#191A23] font-medium",
    footerActionLink: "text-[#191A23] font-semibold underline",
    footerActionText: "text-[#898989]",
    dividerText: "text-[#898989]",
    identityPreviewEditButton: "text-[#191A23]",
    formFieldSuccessText: "text-green-600",
    alertText: "text-[#191A23]",
    logoBox: "flex justify-center py-2",
    logoImage: "h-12 w-12",
    socialButtonsBlockButton: "border border-[#191A23] hover:bg-[#F3F3F3] transition-colors rounded-xl",
    formButtonPrimary: "bg-[#191A23] text-white hover:opacity-90 rounded-xl",
    formFieldInput: "border border-[#191A23] rounded-xl bg-white text-[#191A23]",
    footerAction: "bg-[#F3F3F3]",
    dividerLine: "bg-[#191A23]/10",
    alert: "rounded-xl",
    otpCodeFieldInput: "border border-[#191A23] rounded-xl",
    formFieldRow: "gap-2",
    main: "gap-4",
  },
};

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false } },
});

function ClerkQueryClientCacheInvalidator() {
  const { addListener } = useClerk();
  const qc = useQueryClient();
  const prevUserIdRef = useRef<string | null | undefined>(undefined);

  useEffect(() => {
    const unsubscribe = addListener(({ user }) => {
      const userId = user?.id ?? null;
      if (prevUserIdRef.current !== undefined && prevUserIdRef.current !== userId) {
        qc.clear();
      }
      prevUserIdRef.current = userId;
    });
    return unsubscribe;
  }, [addListener, qc]);

  return null;
}

function SignInPage() {
  return (
    <div className="min-h-screen bg-[#F3F3F3] flex items-center justify-center px-4">
      <SignIn routing="path" path={`${basePath}/sign-in`} signUpUrl={`${basePath}/sign-up`} />
    </div>
  );
}

function SignUpPage() {
  return (
    <div className="min-h-screen bg-[#F3F3F3] flex items-center justify-center px-4">
      <SignUp routing="path" path={`${basePath}/sign-up`} signInUrl={`${basePath}/sign-in`} />
    </div>
  );
}

function Guarded({ component: Page }: { component: React.ComponentType }) {
  return (
    <>
      <Show when="signed-in"><Page /></Show>
      <Show when="signed-out"><Redirect to="/" /></Show>
    </>
  );
}

function HomeRedirect() {
  return (
    <>
      <Show when="signed-in"><Redirect to="/search" /></Show>
      <Show when="signed-out"><Home /></Show>
    </>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/"           component={HomeRedirect} />
      <Route path="/sign-in/*?" component={SignInPage} />
      <Route path="/sign-up/*?" component={SignUpPage} />
      <Route path="/search"     component={() => <Guarded component={SearchPage} />} />
      <Route path="/papers"     component={() => <Guarded component={PapersPage} />} />
      <Route path="/trending"   component={() => <Guarded component={TrendingPage} />} />
      <Route path="/paper/:id"  component={() => <Guarded component={PaperDetailPage} />} />
      <Route path="/dashboard"  component={() => <Guarded component={DashboardPage} />} />
      <Route path="/feed"       component={() => <Guarded component={FeedPage} />} />
      <Route path="/graph"      component={() => <Guarded component={GraphPage} />} />
      <Route path="/workspace"  component={() => <Guarded component={WorkspacePage} />} />
      <Route path="/profile"    component={() => <Guarded component={ProfilePage} />} />
      <Route component={NotFound} />
    </Switch>
  );
}

function ClerkProviderWithRoutes() {
  const [, setLocation] = useLocation();
  return (
    <ClerkProvider
      publishableKey={clerkPubKey}
      proxyUrl={clerkProxyUrl}
      appearance={clerkAppearance}
      signInUrl={`${basePath}/sign-in`}
      signUpUrl={`${basePath}/sign-up`}
      localization={{
        signIn: { start: { title: "Welcome back", subtitle: "Sign in to continue researching" } },
        signUp: { start: { title: "Create your account", subtitle: "Start reading smarter today" } },
      }}
      routerPush={(to) => setLocation(stripBase(to))}
      routerReplace={(to) => setLocation(stripBase(to), { replace: true })}
    >
      <QueryClientProvider client={queryClient}>
        <ClerkQueryClientCacheInvalidator />
        <Router />
      </QueryClientProvider>
    </ClerkProvider>
  );
}

export default function App() {
  return (
    <WouterRouter base={basePath}>
      <ClerkProviderWithRoutes />
    </WouterRouter>
  );
}
