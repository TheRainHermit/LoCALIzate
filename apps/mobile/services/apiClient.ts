const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

// Mock data para desarrollo
const MOCK_LUGARES = [
  {
    id: '1',
    nombre: 'Cristo Rey',
    zona: 'San Antonio',
    descripcion_corta: 'Monumento emblemático de Cali',
    imagen: 'https://via.placeholder.com/300x200?text=Cristo+Rey',
    categoria: 'Cultura',
    rating: 4.8,
    resenas_count: 234,
  },
  {
    id: '2',
    nombre: 'San Antonio',
    zona: 'Centro',
    descripcion_corta: 'Barrio bohemio y artístico',
    imagen: 'https://via.placeholder.com/300x200?text=San+Antonio',
    categoria: 'Gastronomía',
    rating: 4.6,
    resenas_count: 189,
  },
];

export async function fetchLugares() {
  try {
    const res = await fetch(`${API_URL}/lugares`);
    return res.json();
  } catch (error) {
    console.log('Using mock data');
    return MOCK_LUGARES;
  }
}

export async function fetchEventos() {
  try {
    const res = await fetch(`${API_URL}/eventos`);
    return res.json();
  } catch (error) {
    console.log('Using mock data');
    return [];
  }
}