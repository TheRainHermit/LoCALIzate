// packages/shared-types/gastronomia.ts

export type TipoCocina = 'colombiana' | 'internacional' | 'italiana' | 'asiática' | 'árabe' | 'vegana' | 'fusion' | 'otro';
export type RangoPrecios = '<10mil' | '10-20mil' | '20-50mil' | '>50mil';

export interface Horario {
  lunes_a_viernes?: { apertura: string; cierre: string };
  sabado?: { apertura: string; cierre: string };
  domingo?: { apertura: string; cierre: string };
  festivos?: { apertura: string; cierre: string };
  dias_cerrado?: string[];
}

export interface Gastronomia {
  id: number;
  nombre: string;
  descripcion: string;
  descripcion_corta?: string;
  
  // Ubicación
  lat: number;
  lng: number;
  direccion: string;
  zona: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  telefono?: string;
  whatsapp?: string;
  
  // Categorización
  tipo_cocina: TipoCocina;
  especialidades: string[]; // ['ajiaco', 'sancocho', 'pandebono']
  etiquetas: string[]; // ['vegano', 'gluten_free', 'local']
  
  // Precios
  rango_precios: RangoPrecios;
  precio_promedio?: number;
  moneda?: string; // 'COP'
  
  // Horarios
  horario_atencion: Horario;
  horario_almuerzo?: { inicio: string; fin: string };
  horario_cena?: { inicio: string; fin: string };
  
  // Servicios
  tiene_delivery: boolean;
  tiene_reserva: boolean;
  tiene_estacionamiento: boolean;
  precio_estacionamiento?: number;
  tiene_wifi: boolean;
  tiene_aire_acondicionado: boolean;
  tiene_terraza: boolean;
  es_familiar: boolean;
  mascota_friendly: boolean;
  
  // Accesibilidad
  accesible_silla_ruedas: boolean;
  
  // Multimedia
  imagen_principal: string;
  galeria_imagenes?: string[];
  menu_url?: string;
  
  // Narrativa caleña
  tip_caleño?: string; // "¡Oís, la comida aquí es chimba!"
  historia?: string;
  
  // Métricas
  rating_promedio: number;
  resenas_count: number;
  visitas_mensuales?: number;
  
  // Redes
  instagram?: string;
  facebook?: string;
  sitio_web?: string;
  
  // Timestamps
  created_at: Date;
  updated_at: Date;
}

export interface CreateGastronomiaDTO {
  nombre: string;
  descripcion: string;
  descripcion_corta?: string;
  lat: number;
  lng: number;
  direccion: string;
  zona: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  telefono?: string;
  whatsapp?: string;
  tipo_cocina: TipoCocina;
  especialidades: string[];
  etiquetas?: string[];
  rango_precios: RangoPrecios;
  precio_promedio?: number;
  horario_atencion: Horario;
  horario_almuerzo?: { inicio: string; fin: string };
  horario_cena?: { inicio: string; fin: string };
  tiene_delivery?: boolean;
  tiene_reserva?: boolean;
  tiene_estacionamiento?: boolean;
  precio_estacionamiento?: number;
  tiene_wifi?: boolean;
  tiene_aire_acondicionado?: boolean;
  tiene_terraza?: boolean;
  es_familiar?: boolean;
  mascota_friendly?: boolean;
  accesible_silla_ruedas?: boolean;
  imagen_principal: string;
  galeria_imagenes?: string[];
  menu_url?: string;
  tip_caleño?: string;
  historia?: string;
  instagram?: string;
  facebook?: string;
  sitio_web?: string;
}

export interface UpdateGastronomiaDTO {
  nombre?: string;
  descripcion?: string;
  descripcion_corta?: string;
  telefono?: string;
  rango_precios?: RangoPrecios;
  precio_promedio?: number;
  horario_atencion?: Horario;
  tiene_delivery?: boolean;
  tiene_reserva?: boolean;
  imagen_principal?: string;
  galeria_imagenes?: string[];
  menu_url?: string;
  rating_promedio?: number;
  resenas_count?: number;
  instagram?: string;
  facebook?: string;
  sitio_web?: string;
}