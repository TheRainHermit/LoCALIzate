import { Audio } from 'expo-av';

export async function playAudio(url: string) {
  const { sound } = await Audio.Sound.createAsync({ uri: url });
  await sound.playAsync();
  // Puedes manejar el ciclo de vida del audio aquí
}