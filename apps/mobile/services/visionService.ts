import * as FileSystem from 'expo-file-system';
import API_BASE_URL from './apiClient';

interface VisionResult {
  success: boolean;
  lugar?: {
    id: string;
    nombre: string;
    descripcion: string;
    rating_promedio: number;
    zona: string;
    lat: number;
    lng: number;
    imagen_url?: string;
  };
  confidence?: number;
  audio_guia?: string;
  mensaje_caleño?: string;
  message?: string;
}

export async function detectMonument(photoUri: string): Promise<VisionResult> {
  // Usar el endpoint con FormData en lugar de base64
  return identifyWithFile(photoUri);
}

export async function identifyWithFile(photoUri: string): Promise<VisionResult> {
  try {
    const formData = new FormData();
    const filename = photoUri.split('/').pop() || 'photo.jpg';
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';

    formData.append('file', {
      uri: photoUri,
      name: filename,
      type: type,
    } as any);

    const response = await fetch(`${API_BASE_URL}/vision/detect`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error del servidor:', errorText);
      throw new Error(`Error: ${response.status}`);
    }

    const data: VisionResult = await response.json();
    console.log('✅ Resultado visión:', data);
    return data;
  } catch (error) {
    console.error('❌ Error detectando monumento:', error);
    return {
      success: false,
      message: 'Error procesando la imagen. Intenta nuevamente.',
    };
  }
}