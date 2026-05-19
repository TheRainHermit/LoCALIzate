export type CategoriasLugar = 'cultura' | 'naturaleza' | 'gastronomia' | 'salsa' | 'aventura' | 'arte' | 'deportes' | 'historia' | 'musica' | 'compras';
export type TipoPatrimonio = 'Patrimonio Cultural' | 'Patrimonio Natural';
export type Zona = 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';

export interface Horario {
  lunes_a_viernes?: { apertura: string; cierre: string };
  sabado?: { apertura: string; cierre: string };
  domingo?: { apertura: string; cierre: string };
  festivos?: { apertura: string; cierre: string };
  dias_cerrado?: string[];
}

export interface Contacto {
  telefono?: string;
  email?: string;
  sitio_web?: string;
  redes_sociales?: {
    facebook?: string;
    instagram?: string;
    whatsapp?: string;
  };
}

export interface Accesibilidad {
  silla_ruedas: boolean;
  discapacidad_visual: boolean;
  discapacidad_auditiva: boolean;
  parqueadero: boolean;
  banos_accesibles: boolean;
}

export interface Lugar {
  id: number;
  codigo_recurso: string;
  nombre: string;
  descripcion: string;
  descripcion_corta: string;
  
  // Ubicación
  lat: number;
  lng: number;
  direccion: string;
  zona: Zona;
  
  // Categorización
  tipo_patrimonio: TipoPatrimonio;
  categorias: CategoriasLugar[];
  etiquetas: string[];
  
  // Multimedia
  imagen_principal: string;
  galeria_imagenes: string[];
  audio_guia?: string;
  video_url?: string;
  
  // Narrativa caleña
  tip_caleño?: string;
  datos_curiosos: string[];
  historia?: string;
  
  // Información práctica
  horario_atencion: Horario;
  contacto?: Contacto;
  entrada_pagada: boolean;
  costo_entrada?: number;
  moneda?: string;
  accesibilidad: Accesibilidad;
  amenidades: string[]; // ['baños', 'wifi', 'aire_acondicionado']
  
  // Métricas
  rating_promedio: number;
  resenas_count: number;
  visitas_mensuales: number;
  
  // Timestamps
  created_at: Date;
  updated_at: Date;
}

export interface CreateLugarDTO {
  nombre: string;
  descripcion: string;
  descripcion_corta: string;
  lat: number;
  lng: number;
  direccion: string;
  zona: Zona;
  tipo_patrimonio: TipoPatrimonio;
  categorias: CategoriasLugar[];
  etiquetas?: string[];
  imagen_principal: string;
  galeria_imagenes?: string[];
  audio_guia?: string;
  video_url?: string;
  tip_caleño?: string;
  datos_curiosos?: string[];
  historia?: string;
  horario_atencion: Horario;
  contacto?: Contacto;
  entrada_pagada?: boolean;
  costo_entrada?: number;
  accesibilidad?: Accesibilidad;
  amenidades?: string[];
}

export interface UpdateLugarDTO {
  nombre?: string;
  descripcion?: string;
  descripcion_corta?: string;
  categorias?: CategoriasLugar[];
  etiquetas?: string[];
  imagen_principal?: string;
  galeria_imagenes?: string[];
  horario_atencion?: Horario;
  contacto?: Contacto;
  costo_entrada?: number;
  amenidades?: string[];
  rating_promedio?: number;
  resenas_count?: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}