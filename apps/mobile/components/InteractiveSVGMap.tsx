import React, { useEffect, useRef, useState } from 'react';
import { View, Dimensions, TouchableOpacity, Text, Animated, PanResponder } from 'react-native';
import { Colors } from '@/constants';
import type { Lugar } from '../../../packages/shared-types';

interface SVGMapProps {
  locations: Lugar[];
  userLocation?: { lat: number; lng: number } | null;
  onLocationPress?: (location: Lugar) => void;
  height?: number;
}

const CALI_CENTER = { lat: 3.4516, lng: -76.532 };
const CALI_BOUNDS = {
  north: 3.55,
  south: 3.35,
  east: -76.4,
  west: -76.65,
};

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

export default function InteractiveSVGMap({
  locations,
  userLocation = null,
  onLocationPress,
  height = 300,
}: SVGMapProps) {
  const screenWidth = Dimensions.get('window').width - 24; // padding
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderMove: (evt, gestureState) => {
        setOffset({
          x: gestureState.dx,
          y: gestureState.dy,
        });
      },
      onPanResponderRelease: () => {
        setOffset({ x: 0, y: 0 });
      },
    })
  ).current;

  // Convertir lat/lng a coordenadas SVG
  const latToY = (lat: number) => {
    const ratio = (CALI_BOUNDS.north - lat) / (CALI_BOUNDS.north - CALI_BOUNDS.south);
    return ratio * height;
  };

  const lngToX = (lng: number) => {
    const ratio = (lng - CALI_BOUNDS.west) / (CALI_BOUNDS.east - CALI_BOUNDS.west);
    return ratio * screenWidth;
  };

  const getCategoryColor = (lugar: Lugar): string => {
    if (lugar.categorias && lugar.categorias.length > 0) {
      const category = lugar.categorias[0].toLowerCase();
      return (categoryColors as any)[category] || categoryColors.default;
    }
    return categoryColors.default;
  };

  return (
    <View
      style={{
        height,
        backgroundColor: '#E8F4F8',
        borderRadius: 12,
        overflow: 'hidden',
        position: 'relative',
      }}
      {...panResponder.panHandlers}
    >
      {/* Grid de fondo */}
      <View
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
        }}
      >
        {Array.from({ length: 5 }).map((_, i) => (
          <View
            key={`h-${i}`}
            style={{
              position: 'absolute',
              left: 0,
              right: 0,
              height: 1,
              backgroundColor: Colors.primary,
              top: `${(i + 1) * 20}%`,
            }}
          />
        ))}
        {Array.from({ length: 5 }).map((_, i) => (
          <View
            key={`v-${i}`}
            style={{
              position: 'absolute',
              top: 0,
              bottom: 0,
              width: 1,
              backgroundColor: Colors.primary,
              left: `${(i + 1) * 20}%`,
            }}
          />
        ))}
      </View>

      {/* Centro de Cali */}
      <TouchableOpacity
        style={{
          position: 'absolute',
          left: lngToX(CALI_CENTER.lng),
          top: latToY(CALI_CENTER.lat),
          transform: [{ translateX: -15 }, { translateY: -15 }],
          zIndex: 1,
        }}
      >
        <View
          style={{
            width: 30,
            height: 30,
            borderRadius: 15,
            backgroundColor: Colors.primary,
            opacity: 0.3,
            borderWidth: 2,
            borderColor: Colors.primary,
          }}
        />
      </TouchableOpacity>

      {/* Ubicación del usuario */}
      {userLocation && (
        <View
          style={{
            position: 'absolute',
            left: lngToX(userLocation.lng),
            top: latToY(userLocation.lat),
            transform: [{ translateX: -12 }, { translateY: -12 }],
            zIndex: 2,
          }}
        >
          <View
            style={{
              width: 24,
              height: 24,
              borderRadius: 12,
              backgroundColor: Colors.primary,
              borderWidth: 3,
              borderColor: 'white',
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 2 },
              shadowOpacity: 0.25,
              shadowRadius: 3.84,
              elevation: 5,
            }}
          />
        </View>
      )}

      {/* Puntos de lugares */}
      {locations.map((lugar) => (
        <TouchableOpacity
          key={lugar.id}
          onPress={() => onLocationPress?.(lugar)}
          style={{
            position: 'absolute',
            left: lngToX(lugar.lng),
            top: latToY(lugar.lat),
            transform: [{ translateX: -8 }, { translateY: -8 }],
            zIndex: 1,
          }}
        >
          <View
            style={{
              width: 16,
              height: 16,
              borderRadius: 8,
              backgroundColor: getCategoryColor(lugar),
              borderWidth: 2,
              borderColor: 'white',
              shadowColor: '#000',
              shadowOffset: { width: 0, height: 1 },
              shadowOpacity: 0.2,
              shadowRadius: 1.5,
              elevation: 3,
            }}
          />
        </TouchableOpacity>
      ))}

      {/* Labels de zoom */}
      <View
        style={{
          position: 'absolute',
          bottom: 8,
          right: 8,
          flexDirection: 'row',
          gap: 4,
          zIndex: 10,
        }}
      >
        <TouchableOpacity
          onPress={() => setScale(Math.min(scale + 0.2, 2))}
          style={{
            width: 32,
            height: 32,
            borderRadius: 16,
            backgroundColor: 'rgba(255,255,255,0.9)',
            justifyContent: 'center',
            alignItems: 'center',
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.1,
            shadowRadius: 2,
            elevation: 2,
          }}
        >
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: Colors.primary }}>+</Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setScale(Math.max(scale - 0.2, 0.6))}
          style={{
            width: 32,
            height: 32,
            borderRadius: 16,
            backgroundColor: 'rgba(255,255,255,0.9)',
            justifyContent: 'center',
            alignItems: 'center',
            shadowColor: '#000',
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.1,
            shadowRadius: 2,
            elevation: 2,
          }}
        >
          <Text style={{ fontSize: 18, fontWeight: 'bold', color: Colors.primary }}>−</Text>
        </TouchableOpacity>
      </View>

      {/* Leyenda */}
      <View
        style={{
          position: 'absolute',
          bottom: 8,
          left: 8,
          backgroundColor: 'rgba(255,255,255,0.95)',
          borderRadius: 8,
          padding: 8,
          zIndex: 10,
          maxWidth: 120,
        }}
      >
        <Text style={{ fontSize: 10, fontWeight: '600', color: Colors.primary, marginBottom: 4 }}>
          {locations.length} lugares
        </Text>
        {userLocation && (
          <Text style={{ fontSize: 9, color: Colors.onSurfaceVariant }}>📍 Tu ubicación</Text>
        )}
      </View>
    </View>
  );
}