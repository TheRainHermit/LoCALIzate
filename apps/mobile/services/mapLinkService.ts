import * as Linking from 'expo-linking';
import { Platform } from 'react-native';

interface MapLocation {
  name: string;
  lat: number;
  lng: number;
}

export async function openDirectionsInMaps(
  start: MapLocation,
  end: MapLocation
) {
  if (Platform.OS === 'ios') {
    // Apple Maps
    const url = `maps://?saddr=${start.lat},${start.lng}&daddr=${end.lat},${end.lng}`;
    try {
      await Linking.openURL(url);
    } catch {
      // Fallback a Google Maps
      await openGoogleMapsDirections(start, end);
    }
  } else {
    // Android - intenta Google Maps primero
    await openGoogleMapsDirections(start, end);
  }
}

export async function openGoogleMapsDirections(
  start: MapLocation,
  end: MapLocation
) {
  const url = `google.navigation:q=${end.lat},${end.lng}`;
  
  try {
    await Linking.openURL(url);
  } catch {
    // Fallback a URL HTTP
    const httpUrl = `https://www.google.com/maps/dir/?saddr=${start.lat},${start.lng}&daddr=${end.lat},${end.lng}`;
    await Linking.openURL(httpUrl);
  }
}

export function getMapUrl(start: MapLocation, end: MapLocation): string {
  return `https://www.google.com/maps/dir/?saddr=${start.lat},${start.lng}&daddr=${end.lat},${end.lng}`;
}