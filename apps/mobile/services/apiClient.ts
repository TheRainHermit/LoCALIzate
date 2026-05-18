const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchLugares() {
  try {
    const res = await fetch(`${API_URL}/lugares`);
    return res.json();
  } catch (error) {
    console.error('Error fetching lugares:', error);
    return [];
  }
}

export async function fetchEventos() {
  try {
    const res = await fetch(`${API_URL}/eventos`);
    return res.json();
  } catch (error) {
    console.error('Error fetching eventos:', error);
    return [];
  }
}