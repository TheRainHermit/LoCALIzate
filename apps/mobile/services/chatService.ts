// apps/mobile/services/chatService.ts
import { apiClient } from './apiClient';

export async function chat(mensaje: string) {
  return apiClient.enviarMensaje(mensaje);
}