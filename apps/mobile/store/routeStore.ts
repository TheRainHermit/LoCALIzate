import { create } from 'zustand';

export const useRouteStore = create(set => ({
  routes: [],
  setRoutes: (routes) => set({ routes }),
}));