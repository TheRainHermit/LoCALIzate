import * as Location from 'expo-location';

export async function getCurrentLocation() {
  try {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      throw new Error('Permiso de ubicación denegado');
    }
    const location = await Location.getCurrentPositionAsync({});
    return location.coords;
  } catch (error) {
    console.error('Error getting location:', error);
    return null;
  }
}