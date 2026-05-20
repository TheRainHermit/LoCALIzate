import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, Alert, TouchableOpacity, Text, ScrollView, FlatList } from 'react-native';
import * as Location from 'expo-location';
import { Colors, Spacing } from '@/constants';
import { fetchLugares } from '@/services/apiClient';
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

const CALI_CENTER = { lat: 3.4516, lng: -76.532 };

// Calcular distancia simple entre dos puntos
const calcDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
  const R = 6371; // Radio de la tierra en km
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
      {/* Resumen Visual del Mapa */}
      <View
        style={{
          height: 200,
          backgroundColor: Colors.primary,
          justifyContent: 'center',
          alignItems: 'center',
          position: 'relative',
        }}
      >
        <Text style={{ fontSize: 48, marginBottom: 8 }}>🗺️</Text>
        <Text style={{ color: 'white', fontSize: 14, fontWeight: '600' }}>
          {allLocations.length} lugares en Cali
        </Text>
        {userPos && (
          <Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12, marginTop: 4 }}>
            📍 Tu ubicación detectada
          </Text>
        )}

        {/* Botones flotantes */}
        <View
          style={{
            position: 'absolute',
            bottom: 12,
            flexDirection: 'row',
            gap: 8,
            paddingHorizontal: 12,
          }}
        >
          <TouchableOpacity
            style={{
              paddingVertical: 8,
              paddingHorizontal: 12,
              backgroundColor: 'rgba(255,255,255,0.2)',
              borderRadius: 20,
              borderWidth: 1,
              borderColor: 'rgba(255,255,255,0.4)',
            }}
          >
            <Text style={{ color: 'white', fontSize: 11, fontWeight: '600' }}>🏙️ Centro</Text>
          </TouchableOpacity>

          {userPos && (
            <TouchableOpacity
              style={{
                paddingVertical: 8,
                paddingHorizontal: 12,
                backgroundColor: 'rgba(255,255,255,0.2)',
                borderRadius: 20,
                borderWidth: 1,
                borderColor: 'rgba(255,255,255,0.4)',
              }}
            >
              <Text style={{ color: 'white', fontSize: 11, fontWeight: '600' }}>📍 Mi ubicación</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Lista de Lugares */}
      <View style={{ paddingHorizontal: 12, paddingVertical: 12 }}>
        <Text style={{ fontSize: 12, fontWeight: '700', color: Colors.onSurface, marginBottom: 8 }}>
          Lugares cercanos a ti
        </Text>

        {sortedLocations.slice(0, 5).map((lugar) => {
          const distance = userPos ? calcDistance(userPos.lat, userPos.lng, lugar.lat, lugar.lng) : null;

          return (
            <TouchableOpacity
              key={lugar.id}
              onPress={() => onMarkerPress?.(lugar)}
              style={{
                flexDirection: 'row',
                alignItems: 'center',
                paddingVertical: 10,
                paddingHorizontal: 10,
                marginBottom: 8,
                backgroundColor: Colors.surface,
                borderRadius: 12,
                borderLeftWidth: 4,
                borderLeftColor: getCategoryColor(lugar),
              }}
            >
              {/* Color indicator */}
              <View
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: getCategoryColor(lugar),
                  marginRight: 10,
                }}
              />

              {/* Info */}
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 13, fontWeight: '600', color: Colors.onSurface }}>
                  {lugar.nombre}
                </Text>
                <Text style={{ fontSize: 11, color: Colors.onSurfaceVariant, marginTop: 2 }}>
                  {lugar.zona || lugar.direccion || 'Cali'}
                </Text>
              </View>

              {/* Distancia */}
              {distance !== null && (
                <Text style={{ fontSize: 11, fontWeight: '600', color: Colors.primary, marginLeft: 8 }}>
                  {distance < 1 ? `${(distance * 1000).toFixed(0)}m` : `${distance.toFixed(1)}km`}
                </Text>
              )}

              {/* Rating */}
              <Text style={{ fontSize: 12, marginLeft: 8 }}>⭐ {lugar.rating_promedio || 4.5}</Text>
            </TouchableOpacity>
          );
        })}

        {sortedLocations.length > 5 && (
          <Text style={{ fontSize: 11, color: Colors.onSurfaceVariant, textAlign: 'center', marginTop: 8 }}>
            +{sortedLocations.length - 5} lugares más
          </Text>
        )}
      </View>
    </View>
  );
}