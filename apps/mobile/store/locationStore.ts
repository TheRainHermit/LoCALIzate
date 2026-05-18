import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { zustandStorage } from './storage';

export const useLocationStore = create()(
  persist(
    (set) => ({
      location: null,
      setLocation: (location) => set({ location }),
    }),
    {
      name: 'location-storage',
      storage: createJSONStorage(() => zustandStorage),
    }
  )
);