import type { Lugar, Evento } from '../../../packages/shared-types';

// ========== CONFIGURATION ==========
const TIMEOUT = 10000;
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000;

// Obtener API_URL dinámicamente (no al iniciar módulo)
const getApiUrl = (): string => {
  const envUrl = process.env.EXPO_PUBLIC_API_URL;
  if (!envUrl) {
    console.warn('⚠️ EXPO_PUBLIC_API_URL no está configurada, usando localhost');
    return 'http://localhost:5000/api/v1';
  }
  return envUrl;
};

console.log(`🌐 API Client disponible en: ${getApiUrl()}`);

// ========== MOCK DATA ==========
const MOCK_LUGARES: Lugar[] = [
  {
    id: 1,
    codigo_recurso: 'SAN-ANTONIO-001',
    nombre: 'San Antonio',
    descripcion: 'Barrio artístico y bohemio de Cali con vida nocturna vibrante',
    descripcion_corta: 'Barrio artístico con galerías y vida nocturna',
    lat: 3.4419,
    lng: -76.5301,
    direccion: 'Carrera 1 entre Calles 1 y 5',
    zona: 'oeste',
    tipo_patrimonio: 'Patrimonio Cultural',
    categorias: ['arte', 'gastronomia'],
    etiquetas: ['bohemio', 'galerias', 'vida-nocturna'],
    imagen_principal: 'https://via.placeholder.com/400x300?text=San+Antonio',
    galeria_imagenes: [
      'https://via.placeholder.com/400x300?text=San+Antonio+1',
      'https://via.placeholder.com/400x300?text=San+Antonio+2',
    ],
    audio_guia: 'https://example.com/audio/san-antonio.mp3',
    tip_caleño: 'Los mejores tragos y ambiente en la noche caleña',
    datos_curiosos: ['Es el corazón cultural de Cali', 'Famoso por sus bares de salsa desde los 70s'],
    historia: 'Barrio tradicional con historia de más de 50 años de tradición salseríl',
    horario_atencion: {
      lunes_a_viernes: { apertura: '10:00', cierre: '00:00' },
      sabado: { apertura: '10:00', cierre: '02:00' },
      domingo: { apertura: '12:00', cierre: '00:00' },
    },
    entrada_pagada: false,
    accesibilidad: {
      silla_ruedas: true,
      discapacidad_visual: false,
      discapacidad_auditiva: false,
      parqueadero: false,
      banos_accesibles: true,
    },
    amenidades: ['banos', 'wifi', 'restaurantes', 'bares'],
    rating_promedio: 4.5,
    resenas_count: 234,
    visitas_mensuales: 5000,
    created_at: new Date(),
    updated_at: new Date(),
  },
  {
    id: 2,
    codigo_recurso: 'CRISTO-REY-001',
    nombre: 'Cristo Rey',
    descripcion: 'Monumento icónico de Cali ubicado en cerro con vistas panorámicas de toda la ciudad',
    descripcion_corta: 'Monumento con vistas a toda Cali',
    lat: 3.4372,
    lng: -76.5225,
    direccion: 'Cerro de Cristo Rey, Barrio Juanchito',
    zona: 'norte',
    tipo_patrimonio: 'Patrimonio Cultural',
    categorias: ['historia', 'naturaleza'],
    etiquetas: ['monumento', 'vistas', 'simbolo', 'foto'],
    imagen_principal: 'https://via.placeholder.com/400x300?text=Cristo+Rey',
    galeria_imagenes: [
      'https://via.placeholder.com/400x300?text=Cristo+Rey+1',
      'https://via.placeholder.com/400x300?text=Cristo+Rey+2',
    ],
    tip_caleño: 'Mejor visitarlo al atardecer para las vistas más hermosas',
    datos_curiosos: ['Segunda estatua de Cristo más alta en Latinoamérica', 'Construida en 1954'],
    horario_atencion: {
      lunes_a_viernes: { apertura: '09:00', cierre: '18:00' },
      sabado: { apertura: '08:00', cierre: '19:00' },
      domingo: { apertura: '08:00', cierre: '18:00' },
    },
    entrada_pagada: true,
    costo_entrada: 5000,
    accesibilidad: {
      silla_ruedas: false,
      discapacidad_visual: false,
      discapacidad_auditiva: false,
      parqueadero: true,
      banos_accesibles: false,
    },
    amenidades: ['vistas', 'zona-fotos', 'parqueadero'],
    rating_promedio: 4.8,
    resenas_count: 567,
    visitas_mensuales: 8000,
    created_at: new Date(),
    updated_at: new Date(),
  },
  {
    id: 3,
    codigo_recurso: 'LA-SALSA-TOUR-001',
    nombre: 'Tour de Salsa en el Pacífico',
    descripcion: 'Experiencia inmersiva en la cuna de la salsa caleña',
    descripcion_corta: 'Tour por locales de salsa tradicionales',
    lat: 3.4450,
    lng: -76.5200,
    direccion: 'Varios puntos en el centro de Cali',
    zona: 'centro',
    tipo_patrimonio: 'Patrimonio Cultural',
    categorias: ['musica', 'cultura'],
    etiquetas: ['salsa', 'tour', 'musica', 'experiencia'],
    imagen_principal: 'https://via.placeholder.com/400x300?text=Salsa+Tour',
    galeria_imagenes: [],
    tip_caleño: 'La mejor experiencia para entender la salsa caleña',
    datos_curiosos: ['Cali es la capital mundial de la salsa'],
    horario_atencion: {
      viernes: { apertura: '20:00', cierre: '04:00' },
      sabado: { apertura: '20:00', cierre: '04:00' },
    },
    entrada_pagada: true,
    costo_entrada: 25000,
    accesibilidad: {
      silla_ruedas: false,
      discapacidad_visual: false,
      discapacidad_auditiva: false,
      parqueadero: false,
      banos_accesibles: true,
    },
    amenidades: ['restaurante', 'bares', 'musica-viva'],
    rating_promedio: 4.7,
    resenas_count: 189,
    visitas_mensuales: 3200,
    created_at: new Date(),
    updated_at: new Date(),
  },
];

const MOCK_EVENTOS: Evento[] = [
  {
    id: 1,
    nombre: 'Festival de Salsa Cali 2026',
    descripcion: 'El mayor festival de salsa de América Latina con artistas internacionales',
    descripcion_corta: 'Festival de salsa más grande de Latinoamérica',
    fecha_inicio: new Date(2026, 11, 28),
    fecha_fin: new Date(2026, 11, 30),
    hora_inicio: '20:00',
    hora_fin: '02:00',
    lat: 3.4372,
    lng: -76.5225,
    direccion: 'Parque Bolívar, Cali',
    zona: 'centro',
    organizador: 'Cali Cultura',
    categorias: ['festival', 'musica'],
    etiquetas: ['salsa', 'baile', 'cultura', 'internacional'],
    imagen: 'https://via.placeholder.com/400x300?text=Festival+Salsa',
    es_gratis: false,
    precio_general: 50000,
    tiene_entradas_online: true,
    url_entradas: 'https://example.com/tickets',
    aforo_maximo: 10000,
    rating_promedio: 4.9,
    resenas_count: 2345,
    created_at: new Date(),
    updated_at: new Date(),
  },
];

// ========== HELPER FUNCTIONS ==========

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = TIMEOUT): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function fetchWithRetry<T>(
  url: string,
  options?: RequestInit,
  maxAttempts = RETRY_ATTEMPTS,
  delayMs = RETRY_DELAY
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetchWithTimeout(url, options);

      if (!response.ok) {
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        (error as any).status = response.status;
        throw error;
      }

      const data = await response.json();
      return data;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      const status = (error as any)?.status;
      if (status && status >= 400 && status < 500 && status !== 408 && status !== 429) {
        throw lastError;
      }

      if (attempt < maxAttempts) {
        const backoff = delayMs * Math.pow(2, attempt - 1);
        console.warn(`⚠️ Intento ${attempt}/${maxAttempts} falló. Reintentando en ${backoff}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoff));
      }
    }
  }

  throw lastError || new Error('Unknown error after retries');
}

function logApiCall(method: string, url: string, status?: number, error?: string) {
  const emoji = status && status >= 200 && status < 300 ? '✅' : '❌';
  const details = error ? ` - ${error}` : '';
  console.log(`${emoji} [${method}] ${url}${details}`);
}

// ========== INDIVIDUAL FUNCTION EXPORTS ==========

export async function fetchLugares(limit = 50, offset = 0, filtros?: Record<string, any>) {
  try {
    const API_URL = getApiUrl();
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
      ...Object.fromEntries(
        Object.entries(filtros || {}).map(([k, v]) => [k, String(v)])
      ),
    });

    const url = `${API_URL}/lugares?${params}`;
    const data = await fetchWithRetry<any>(url);
    logApiCall('GET', url, 200);
    return data.results || data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('GET', `${getApiUrl()}/lugares`, undefined, err.message);
    console.warn('⚠️ Usando mock data para lugares');
    return MOCK_LUGARES;
  }
}

export async function fetchLugarDetail(id: number) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/lugares/${id}`;
    const data = await fetchWithRetry<Lugar>(url);
    logApiCall('GET', url, 200);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('GET', `${getApiUrl()}/lugares/${id}`, undefined, err.message);
    const lugar = MOCK_LUGARES.find(l => l.id === id);
    if (lugar) return lugar;
    throw err;
  }
}

export async function fetchEventos(limit = 20, offset = 0) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/eventos?limit=${limit}&offset=${offset}`;
    const data = await fetchWithRetry<any>(url);
    logApiCall('GET', url, 200);
    return data.results || data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('GET', `${getApiUrl()}/eventos`, undefined, err.message);
    console.warn('⚠️ Usando mock data para eventos');
    return MOCK_EVENTOS;
  }
}

export async function fetchGastronomia(limit = 20) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/gastronomia?limit=${limit}`;
    const data = await fetchWithRetry(url);
    logApiCall('GET', url, 200);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('GET', `${getApiUrl()}/gastronomia`, undefined, err.message);
    return MOCK_LUGARES.filter(l => l.categorias?.includes('gastronomia'));
  }
}

export async function fetchLugarResenas(lugarId: number) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/lugares/${lugarId}/resenas`;
    const data = await fetchWithRetry(url);
    logApiCall('GET', url, 200);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('GET', `${getApiUrl()}/lugares/${lugarId}/resenas`, undefined, err.message);
    console.warn('⚠️ No hay reseñas disponibles');
    return [];
  }
}

export async function crearResena(lugarId: number, rating: number, comentario?: string) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/lugares/${lugarId}/resenas`;
    const data = await fetchWithRetry(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating, comentario }),
    });
    logApiCall('POST', url, 201);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('POST', `${getApiUrl()}/lugares/${lugarId}/resenas`, undefined, err.message);
    throw err;
  }
}

export async function optimizarRuta(lugarIds: number[], coordenada_inicio: { lat: number; lng: number }) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/rutas/optimizar`;
    const data = await fetchWithRetry(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lugares: lugarIds,
        inicio: coordenada_inicio,
      }),
    });
    logApiCall('POST', url, 200);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('POST', `${getApiUrl()}/rutas/optimizar`, undefined, err.message);
    throw err;
  }
}

export async function identifyMonument(imageBase64: string) {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL}/vision/identificar`;
    const data = await fetchWithRetry(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageBase64 }),
    });
    logApiCall('POST', url, 200);
    return data;
  } catch (error) {
    const err = error instanceof Error ? error : new Error(String(error));
    logApiCall('POST', `${getApiUrl()}/vision/identificar`, undefined, err.message);
    throw err;
  }
}

export async function healthCheck() {
  try {
    const API_URL = getApiUrl();
    const url = `${API_URL.replace('/api/v1', '')}/health`;
    const response = await fetchWithTimeout(url, {}, 5000);
    const data = await response.json();
    logApiCall('GET', url, response.status);
    return { status: 'online', data };
  } catch (error) {
    console.error('❌ Backend no está disponible:', error);
    return { status: 'offline', error: String(error) };
  }
}

export const apiClient = {
  getLugares: fetchLugares,
  getLugarDetail: fetchLugarDetail,
  getEventos: fetchEventos,
  getGastronomia: fetchGastronomia,
  getLugarResenas: fetchLugarResenas,
  crearResena,
  optimizarRuta,
  identifyMonument,
  healthCheck,
  getConfig: () => ({
    API_URL: getApiUrl(),
    TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_DELAY,
    environment: process.env.NODE_ENV || 'development',
    apiVersion: '1.0',
  }),
};

export const getBackendBaseUrl = (): string => {
  const apiUrl = getApiUrl();
  return apiUrl.replace('/api/v1', '');
};

export default apiClient;