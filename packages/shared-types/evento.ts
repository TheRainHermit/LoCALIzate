// packages/shared-types/evento.ts

export type CategoriaEvento = 'concierto' | 'teatro' | 'danza' | 'festival' | 'exposicion' | 'deportes' | 'gastronomia' | 'cultural' | 'otro';
export type EstadoEvento = 'proximo' | 'en_curso' | 'finalizado' | 'cancelado' | 'pospuesto';

export interface Evento {
  id: number;
  nombre: string;
  descripcion: string;
  descripcion_corta?: string;
  
  // Fechas y horarios
  fecha_inicio: Date;
  fecha_fin: Date;
  hora_inicio: string; // HH:mm
  hora_fin: string;    // HH:mm
  
  // Ubicación
  lat: number;
  lng: number;
  direccion: string;
  zona: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  lugar_id?: number;   // Si es en un lugar específico
  
  // Organizador
  organizador: string;
  contacto_organizador?: {
    telefono?: string;
    email?: string;
    sitio_web?: string;
  };
  
  // Categorización
  categorias: CategoriaEvento[];
  etiquetas: string[];
  estado: EstadoEvento;
  
  // Multimedia
  imagen: string;
  galeria_imagenes?: string[];
  video_url?: string;
  
  // Aforo y entradas
  aforo_maximo?: number;
  aforo_actual?: number;
  tiene_entradas_online: boolean;
  url_entradas?: string;
  
  // Precios
  es_gratis: boolean;
  precio_general?: number;
  precio_estudiante?: number;
  precio_niño?: number;
  precio_tercera_edad?: number;
  moneda?: string; // 'COP', 'USD'
  
  // Metadata
  rating_promedio?: number;
  resenas_count?: number;
  
  // Timestamps
  created_at: Date;
  updated_at: Date;
}

export interface CreateEventoDTO {
  nombre: string;
  descripcion: string;
  descripcion_corta?: string;
  fecha_inicio: Date;
  fecha_fin: Date;
  hora_inicio: string;
  hora_fin: string;
  lat: number;
  lng: number;
  direccion: string;
  zona: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  lugar_id?: number;
  organizador: string;
  contacto_organizador?: {
    telefono?: string;
    email?: string;
    sitio_web?: string;
  };
  categorias: CategoriaEvento[];
  etiquetas?: string[];
  imagen: string;
  galeria_imagenes?: string[];
  video_url?: string;
  aforo_maximo?: number;
  tiene_entradas_online?: boolean;
  url_entradas?: string;
  es_gratis: boolean;
  precio_general?: number;
  precio_estudiante?: number;
  precio_niño?: number;
  precio_tercera_edad?: number;
}

export interface UpdateEventoDTO {
  nombre?: string;
  descripcion?: string;
  descripcion_corta?: string;
  fecha_inicio?: Date;
  fecha_fin?: Date;
  hora_inicio?: string;
  hora_fin?: string;
  estado?: EstadoEvento;
  aforo_actual?: number;
  imagen?: string;
  galeria_imagenes?: string[];
  precio_general?: number;
  precio_estudiante?: number;
  precio_niño?: number;
  precio_tercera_edad?: number;
}

export interface EventoEnriquecido extends Evento {
  lugar?: {
    id: number;
    nombre: string;
    zona: string;
  };
}