import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, Alert, TouchableOpacity, Text } from 'react-native';
import * as Location from 'expo-location';
import { Colors } from '@/constants';
import { fetchLugares } from '@/services/apiClient';
import { openDirectionsInMaps } from '@/services/mapLinkService';
import LeafletMapView from './LeafletMapView';
import type { Lugar } from '../../../packages/shared-types';

interface MapViewProps {
  locations?: Lugar[];
  userLocation?: { lat: number; lng: number } | null;
  destination?: { lat: number; lng: number; name: string } | null;
  onMarkerPress?: (location: Lugar) => void;
  showUserLocation?: boolean;
}

const categoryColors = {
  cultura: '#FF6B35',
  naturaleza: '#2ECC71',
  gastronomia: '#E74C3C',
  salsa: '#9B59B6',
  aventura: '#3498DB',
  historia: '#FF8C61',
  musica: '#F7931E',
  arte: '#1ABC9C',
  default: '#95A5A6',
};

const calcDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
  const R = 6371;
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLng = (lng2 - lng1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

export default function MapViewComponent({
  locations = [],
  userLocation = null,
  destination = null,
  onMarkerPress,
  showUserLocation = true,
}: MapViewProps) {
  const [allLocations, setAllLocations] = useState<Lugar[]>(locations);
  const [loading, setLoading] = useState(!locations.length);
  const [userPos, setUserPos] = useState(userLocation);
  const [selectedLocation, setSelectedLocation] = useState<Lugar | null>(null);
  const [routeLocations, setRouteLocations] = useState<Lugar[]>([]);

  useEffect(() => {
    if (!locations.length) {
      loadLocations();
    }
  }, []);

  useEffect(() => {
    if (showUserLocation) {
      getUserLocation();
    }
  }, [showUserLocation]);

  const getUserLocation = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        console.warn('Location permission not granted');
        return;
      }

      const location = await Location.getCurrentPositionAsync({});
      setUserPos({
        lat: location.coords.latitude,
        lng: location.coords.longitude,
      });
    } catch (error) {
      console.error('Error getting user location:', error);
    }
  };

  const loadLocations = async () => {
    try {
      const data = await fetchLugares(100);
      setAllLocations(data);
    } catch (error) {
      console.error('Error loading locations:', error);
      Alert.alert('Error', 'No se pudieron cargar los lugares');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (lugar: Lugar): string => {
    if (lugar.categorias && lugar.categorias.length > 0) {
      const category = lugar.categorias[0].toLowerCase();
      return (categoryColors as any)[category] || categoryColors.default;
    }
    return categoryColors.default;
  };

  const handleViewRoute = async (location: Lugar) => {
    if (!userPos) {
      Alert.alert('Error', 'No se pudo obtener tu ubicación');
      return;
    }

    try {
      await openDirectionsInMaps(
        { name: 'Tu ubicación', lat: userPos.lat, lng: userPos.lng },
        { name: location.nombre, lat: location.lat, lng: location.lng }
      );
    } catch (error) {
      console.error('Error opening maps:', error);
      Alert.alert('Error', 'No se pudo abrir el mapa');
    }
  };

  const sortedLocations = userPos
    ? [...allLocations].sort((a, b) => {
        const distA = calcDistance(userPos.lat, userPos.lng, a.lat, a.lng);
        const distB = calcDistance(userPos.lat, userPos.lng, b.lat, b.lng);
        return distA - distB;
      })
    : allLocations;

  if (loading) {
    return (
      <View
        style={{
          height: 300,
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: Colors.surfaceContainerLow,
          borderRadius: 16,
        }}
      >
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <View style={{ backgroundColor: Colors.surfaceContainerLow, borderRadius: 16, overflow: 'hidden' }}>
      {/* Mapa Leaflet interactivo con WebView */}
      <LeafletMapView
        locations={allLocations}
        userLocation={userPos}
        onLocationPress={(location) => {
          setSelectedLocation(location);
          onMarkerPress?.(location);
        }}
        onRouteSelected={(locations) => {
          setRouteLocations(locations);
        }}
        height={280}
      />

      {/* Info del lugar seleccionado + botón de ruta */}
      {selectedLocation && (
        <View style={{ padding: 12, backgroundColor: Colors.surface }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 14, fontWeight: '700', color: Colors.onSurface }}>
                {selectedLocation.nombre}
              </Text>
              <Text style={{ fontSize: 12, color: Colors.onSurfaceVariant, marginTop: 4 }}>
                {selectedLocation.zona || selectedLocation.direccion || 'Cali'}
              </Text>
            </View>
            <Text style={{ fontSize: 12 }}>⭐ {selectedLocation.rating_promedio || 4.5}</Text>
          </View>

          <TouchableOpacity
            onPress={() => handleViewRoute(selectedLocation)}
            style={{
              paddingVertical: 10,
              paddingHorizontal: 12,
              backgroundColor: Colors.primary,
              borderRadius: 8,
              alignItems: 'center',
            }}
          >
            <Text style={{ color: 'white', fontSize: 13, fontWeight: '600' }}>
              🗺️ Ver ruta en Google Maps
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Info de ruta seleccionada */}
      {routeLocations.length > 0 && (
        <View style={{ paddingHorizontal: 12, paddingVertical: 8, backgroundColor: Colors.primaryContainer }}>
          <Text style={{ fontSize: 11, fontWeight: '600', color: Colors.primary }}>
            Ruta: {routeLocations.length} lugar{routeLocations.length > 1 ? 'es' : ''} seleccionado{routeLocations.length > 1 ? 's' : ''}
          </Text>
        </View>
      )}
    </View>
  );
}