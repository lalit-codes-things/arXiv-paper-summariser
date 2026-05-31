import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type BookmarkStore = {
  bookmarks: string[];
  toggle: (id: string) => void;
  has: (id: string) => boolean;
};

export const useBookmarks = create<BookmarkStore>()(
  persist(
    (set, get) => ({
      bookmarks: [],
      toggle: (id) =>
        set((state) => ({
          bookmarks: state.bookmarks.includes(id)
            ? state.bookmarks.filter((bookmark) => bookmark !== id)
            : [...state.bookmarks, id],
        })),
      has: (id) => get().bookmarks.includes(id),
    }),
    { name: 'arxiv-bookmarks' },
  ),
);
