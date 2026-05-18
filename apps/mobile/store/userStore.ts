import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { zustandStorage } from './storage';

interface UserStore {
  userInterests: string[];
  setUserInterests: (interests: string[]) => void;
  userLocation: { lat: number; lng: number } | null;
  setUserLocation: (location: { lat: number; lng: number } | null) => void;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      userInterests: [],
      setUserInterests: (interests: string[]) => set({ userInterests: interests }),
      userLocation: null,
      setUserLocation: (location: { lat: number; lng: number } | null) =>
        set({ userLocation: location }),
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => zustandStorage),
    }
  )
);