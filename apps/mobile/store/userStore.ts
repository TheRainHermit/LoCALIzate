import { create } from 'zustand';

interface UserStore {
  userInterests: string[];
  setUserInterests: (interests: string[]) => void;
  userLocation: { lat: number; lng: number } | null;
  setUserLocation: (location: { lat: number; lng: number } | null) => void;
}

export const useUserStore = create<UserStore>(set => ({
  userInterests: [],
  setUserInterests: (interests) => set({ userInterests: interests }),
  userLocation: null,
  setUserLocation: (location) => set({ userLocation: location }),
}));