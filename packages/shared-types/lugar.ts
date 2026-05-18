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
  zona: 'centro' | 'sur' | 'norte' | 'este' | 'oeste' | 'pance';
  
  // Categorización
  tipo_patrimonio: 'Patrimonio Cultural' | 'Patrimonio Natural';
  categorias: string[];  // ['salsa', 'cultura', 'naturaleza']
  etiquetas: string[];   // ['monumento', 'iglesia', 'gotico']
  
  // Multimedia
  imagen_principal: string;
  galeria_imagenes: string[];
  audio_guia: string;
  
  // Narrativa caleña
  tip_caleño: string;    // "¡Oís, esta iglesia es chimba!"
  datos_curiosos: string[];
  
  // Métricas
  rating_promedio: number;
  visitas_mensuales: number;
  
  // Timestamps
  created_at: Date;
  updated_at: Date;
}

// DTO para crear lugar (sin id ni timestamps)
export interface CreateLugarDTO {
  nombre: string;
  descripcion: string;
  lat: number;
  lng: number;
  // ... resto de campos
}

// Respuesta de API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}