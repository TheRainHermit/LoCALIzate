/**
 * Storage adapter para Zustand - Compatible con Expo Go
 * Usa memoria simple sin persistencia en desarrollo
 */

// En memoria simple para Expo Go
const memoryStorage: Record<string, string> = {};

export const zustandStorage = {
  getItem: (name: string) => {
    try {
      const item = memoryStorage[name];
      return item ? item : null;
    } catch (error) {
      console.warn(`Failed to get item ${name}:`, error);
      return null;
    }
  },
  setItem: (name: string, value: string) => {
    try {
      memoryStorage[name] = value;
    } catch (error) {
      console.warn(`Failed to set item ${name}:`, error);
    }
  },
  removeItem: (name: string) => {
    try {
      delete memoryStorage[name];
    } catch (error) {
      console.warn(`Failed to remove item ${name}:`, error);
    }
  },
};