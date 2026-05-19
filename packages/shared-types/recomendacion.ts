// packages/shared-types/recomendacion.ts

export type TipoRecomendacion = 'personalizada' | 'tendencia' | 'proximidad' | 'similar' | 'combo' | 'evento_especial';
export type RazonRecomendacion = 'interes_coincide' | 'visitó_similar' | 'cerca_de_ti' | 'popular_ahora' | 'complementa_ruta' | 'amigos_visitaron' | 'evento_especial';

export interface Recomendacion {
  id: number;
  
  // Referencias
  usuario_id: number;
  lugar_id: number;
  
  // Tipo y razón
  tipo: TipoRecomendacion;
  razon: RazonRecomendacion;
  descripcion: string;
  
  // Puntuación ML
  score_relevancia: number; // 0-100
  score_personalizacion: number; // 0-100
  
  // Metadata
  datos_evento?: {
    fecha?: Date;
    promocion?: string;
    descuento_porcentaje?: number;
  };
  
  // Control
  activo: boolean;
  mostrada: boolean;
  fecha_mostrada?: Date;
  clickeada: boolean;
  fecha_clickeada?: Date;
  visitada: boolean;
  fecha_visitada?: Date;
  
  // Timestamps
  created_at: Date;
  expires_at?: Date;
}

export interface CreateRecomendacionDTO {
  usuario_id: number;
  lugar_id: number;
  tipo: TipoRecomendacion;
  razon: RazonRecomendacion;
  descripcion: string;
  score_relevancia: number;
  score_personalizacion: number;
  datos_evento?: {
    fecha?: Date;
    promocion?: string;
    descuento_porcentaje?: number;
  };
  expires_at?: Date;
}

export interface RecomendacionEnriquecida extends Recomendacion {
  lugar: {
    id: number;
    nombre: string;
    imagen_principal: string;
    categorias: string[];
    rating_promedio: number;
    zona: string;
  };
}

export interface RecomendacionesPorUsuario {
  usuario_id: number;
  total: number;
  recomendaciones: RecomendacionEnriquecida[];
  ultima_actualizacion: Date;
}

export interface EstadisticasRecomendacion {
  total_generadas: number;
  total_mostradas: number;
  total_clickeadas: number;
  total_visitadas: number;
  tasa_conversion_clicks: number;
  tasa_conversion_visitas: number;
  tipo_mas_efectivo: TipoRecomendacion;
  razon_mas_efectiva: RazonRecomendacion;
}