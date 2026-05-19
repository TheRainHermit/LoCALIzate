// packages/shared-types/usuario.ts

export type InteresCategoria = 'cultura' | 'naturaleza' | 'gastronomia' | 'salsa' | 'aventura' | 'arte' | 'deportes' | 'historia' | 'musica' | 'compras';
export type RolUsuario = 'turista' | 'local' | 'guia' | 'admin';
export type FrecuenciaRecomendaciones = 'diaria' | 'semanal' | 'mensual' | 'nunca';

export interface Usuario {
  id: number;
  nombre: string;
  email: string;
  telefono?: string;
  fotografia?: string;
  
  // Preferencias y intereses
  intereses: InteresCategoria[];
  zona_preferida?: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  rango_edad?: '18-25' | '26-35' | '36-45' | '46-55' | '56+';
  idioma_preferido: string; // 'es', 'en', 'fr'
  
  // Ubicación actual
  ubicacion_actual?: {
    lat: number;
    lng: number;
    timestamp: Date;
  };
  
  // Historial
  lugares_visitados: number[];
  lugares_favoritos: number[];
  eventos_asistidos: number[];
  rutas_guardadas: number[];
  
  // Preferencias de notificación
  notificaciones_habilitadas: boolean;
  recibir_recomendaciones: boolean;
  frecuencia_recomendaciones: FrecuenciaRecomendaciones;
  
  // Control de cuenta
  activo: boolean;
  verificado: boolean;
  rol: RolUsuario;
  bio?: string;
  
  // Timestamps
  fecha_registro: Date;
  ultimo_acceso?: Date;
  updated_at: Date;
}

export interface CreateUsuarioDTO {
  nombre: string;
  email: string;
  telefono?: string;
  fotografia?: string;
  intereses: InteresCategoria[];
  idioma_preferido?: string;
}

export interface UpdateUsuarioDTO {
  nombre?: string;
  telefono?: string;
  fotografia?: string;
  intereses?: InteresCategoria[];
  zona_preferida?: string;
  rango_edad?: string;
  idioma_preferido?: string;
  notificaciones_habilitadas?: boolean;
  recibir_recomendaciones?: boolean;
  frecuencia_recomendaciones?: FrecuenciaRecomendaciones;
  bio?: string;
}

export interface UsuarioPublico {
  id: number;
  nombre: string;
  fotografia?: string;
  rol: RolUsuario;
  bio?: string;
}

export interface PerfilUsuario extends Usuario {
  total_lugares_visitados: number;
  total_eventos_asistidos: number;
  total_rutas_creadas: number;
}