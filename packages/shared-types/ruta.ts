// packages/shared-types/ruta.ts

export type TipoTransporte = 'a_pie' | 'carro' | 'transporte_publico' | 'bicicleta' | 'mixto';
export type NivelDificultad = 'facil' | 'moderada' | 'dificil';

export interface Parada {
  orden: number;
  lugar_id: number;
  nombre: string;
  lat: number;
  lng: number;
  distancia_anterior_km: number;
  tiempo_llegada_minutos: number;
  tiempo_estancia_recomendado_minutos: number;
  notas?: string;
}

export interface Ruta {
  id: number;
  usuario_id: number;
  nombre: string;
  descripcion?: string;
  
  // Estructura
  lugares: number[]; // IDs de lugares en orden original
  paradas_optimizadas: Parada[]; // Orden optimizado
  
  // Distancias y tiempos
  distancia_total_km: number;
  tiempo_estimado_minutos: number;
  
  // Ubicaciones
  ubicacion_inicio: { lat: number; lng: number };
  ubicacion_fin: { lat: number; lng: number };
  
  // Características
  tipo_transporte: TipoTransporte;
  dificultad: NivelDificultad;
  es_circular: boolean; // Vuelve al punto de partida
  
  // Privacidad y compartición
  es_privada: boolean;
  es_compartida: boolean;
  usuarios_compartida?: number[];
  
  // Metadata
  rating_promedio?: number;
  resenas_count?: number;
  veces_usada?: number;
  
  // Timestamps
  created_at: Date;
  updated_at: Date;
}

export interface CreateRutaDTO {
  usuario_id: number;
  nombre: string;
  descripcion?: string;
  lugares: number[];
  ubicacion_inicio: { lat: number; lng: number };
  ubicacion_fin?: { lat: number; lng: number };
  tipo_transporte: TipoTransporte;
  dificultad?: NivelDificultad;
  es_privada?: boolean;
  es_circular?: boolean;
}

export interface UpdateRutaDTO {
  nombre?: string;
  descripcion?: string;
  lugares?: number[];
  tipo_transporte?: TipoTransporte;
  dificultad?: NivelDificultad;
  es_privada?: boolean;
  es_compartida?: boolean;
  usuarios_compartida?: number[];
}

export interface RutaOptimizada {
  ruta_id: number;
  paradas_optimizadas: Parada[];
  distancia_total_km: number;
  tiempo_estimado_minutos: number;
}

export interface OptimizarRutaRequest {
  lugares: number[];
  ubicacion_inicio: { lat: number; lng: number };
  ubicacion_fin?: { lat: number; lng: number };
  tipo_transporte?: TipoTransporte;
}