const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

export const apiClient = {
  // Lugares
  async getLugares(limit = 50, filtros?: object) {
    const params = new URLSearchParams({ limit: String(limit) });
    return fetch(`${API_URL}/v1/lugares?${params}`).then(r => r.json());
  },
  
  async getLugarDetail(id: number) {
    return fetch(`${API_URL}/v1/lugares/${id}`).then(r => r.json());
  },

  // Eventos
  async getEventos(limit = 20) {
    return fetch(`${API_URL}/v1/eventos?limit=${limit}`).then(r => r.json());
  },

  // Rutas
  async optimizarRuta(lugarIds: number[], coordenada_inicio: { lat: number; lng: number }) {
    return fetch(`${API_URL}/v1/rutas/optimizar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lugares: lugarIds, inicio: coordenada_inicio })
    }).then(r => r.json());
  },

  // Chat
  async enviarMensaje(mensaje: string) {
    return fetch(`${API_URL}/v1/chat/mensaje`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mensaje })
    }).then(r => r.json());
  },

  // Gastronomía
  async getGastronomia() {
    return fetch(`${API_URL}/v1/gastronomia`).then(r => r.json());
  }
};