import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { zustandStorage } from './storage';

export const useRouteStore = create()(
  persist(
    (set) => ({
      currentRoute: null,
      setCurrentRoute: (route) => set({ currentRoute: route }),
      savedRoutes: [],
      addSavedRoute: (route) =>
        set((state) => ({
          savedRoutes: [...state.savedRoutes, route],
        })),
    }),
    {
      name: 'route-storage',
      storage: createJSONStorage(() => zustandStorage),
    }
  )
);