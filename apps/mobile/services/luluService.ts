import { getBackendBaseUrl } from './apiClient';

interface LuluMessage {
  response: string;
  lugares: string[];
}

const LULU_BASE_URL = process.env.EXPO_PUBLIC_LULU_URL || 'http://localhost:3000';

export async function chatWithLulu(
  message: string,
  sessionId: string,
  language: string = 'es'
): Promise<LuluMessage> {
  try {
    console.log('📤 Enviando a Lulú:', { message, sessionId, language });
    const response = await fetch(`${LULU_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        sessionId,
        idioma: language,
      }),
    });

    const responseText = await response.text();
    console.log('📥 Respuesta del servidor:', responseText);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${responseText}`);
    }

    const data: LuluMessage = JSON.parse(responseText);
    return data;
  } catch (error) {
    console.error('❌ Error chatting with Lulu:', error);
    throw error;
  }
}

export async function transcribeAudio(
  audioUri: string,
  language: string = 'es'
): Promise<string> {
  try {
    const formData = new FormData();
    formData.append('audio', {
      uri: audioUri,
      type: 'audio/webm',
      name: 'audio.webm',
    } as any);

    const response = await fetch(`${LULU_BASE_URL}/transcribir`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    return data.texto;
  } catch (error) {
    console.error('Error transcribing audio:', error);
    throw error;
  }
}

export async function generateSpeech(text: string): Promise<ArrayBuffer> {
  try {
    console.log('🎙️ Generando speech para:', text.substring(0, 50) + '...');
    console.log('🔗 URL:', `${LULU_BASE_URL}/speak`);
    
    const response = await fetch(`${LULU_BASE_URL}/speak`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    console.log('📊 Status:', response.status);
    console.log('📋 Headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Error response:', errorText);
      throw new Error(`Error: ${response.status} - ${errorText}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    console.log('✅ Audio recibido, tamaño:', arrayBuffer.byteLength, 'bytes');
    return arrayBuffer;
  } catch (error) {
    console.error('❌ Error generating speech:', error);
    throw error;
  }
}