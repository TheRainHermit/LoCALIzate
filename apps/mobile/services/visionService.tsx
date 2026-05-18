export async function identifyMonument(imageBase64: string) {
  // Envía la imagen al backend para reconocimiento visual
  const res = await fetch('https://tu-backend.com/api/vision/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageBase64 }),
  });
  return res.json();
}