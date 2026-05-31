import { create } from 'zustand';

type SessionState = { token?: string; workspaceId: string; setToken: (token: string) => void; setWorkspace: (workspaceId: string) => void };
export const useSession = create<SessionState>((set) => ({ workspaceId: 'workspace-ai-lab', setToken: (token) => set({ token }), setWorkspace: (workspaceId) => set({ workspaceId }) }));
