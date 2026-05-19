// packages/shared-types/common.ts

export interface Ubicacion {
  lat: number;
  lng: number;
  direccion: string;
  ciudad?: string;
  pais?: string;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ErrorResponse {
  success: false;
  error: string;
  error_code?: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// packages/shared-types/index.ts
// Re-export Horario explicitly from './lugar' to avoid ambiguous duplicate exports
export { Horario } from './lugar';
export * from './lugar';
export * from './evento';
export * from './ruta';
export * from './gastronomia';
export * from './usuario';
export * from './recomendacion';