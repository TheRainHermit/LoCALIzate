export async function getRecommendedPlaces(profile, location) {
  // Lógica para obtener recomendaciones personalizadas
  // Ejemplo: fetch a tu backend con perfil y ubicación
  const res = await fetch('https://tu-backend.com/api/recommendations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile, location }),
  });
  return res.json();
}