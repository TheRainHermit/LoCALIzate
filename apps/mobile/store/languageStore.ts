import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { zustandStorage } from './storage';

interface LanguageStore {
  language: string;
  setLanguage: (lang: string) => void;
  sessionId: string;
  setSessionId: (id: string) => void;
}

export const useLanguageStore = create<LanguageStore>()(
  persist(
    (set) => ({
      language: 'es',
      setLanguage: (lang: string) => set({ language: lang }),
      sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      setSessionId: (id: string) => set({ sessionId: id }),
    }),
    {
      name: 'language-storage',
      storage: createJSONStorage(() => zustandStorage),
    }
  )
);