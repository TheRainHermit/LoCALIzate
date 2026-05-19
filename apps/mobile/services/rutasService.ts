// apps/mobile/services/rutasService.ts
import { apiClient } from './apiClient';
import type { Ruta } from '../../../packages/shared-types/ruta';

export async function planificarRuta(lugarIds: number[], ubicacionActual: { lat: number; lng: number }) {
  return apiClient.optimizarRuta(lugarIds, ubicacionActual);
}

export async function calcularDistancia(lat1: number, lng1: number, lat2: number, lng2: number) {
  // Haversine formula
  const R = 6371; // Radio Tierra en km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng/2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}