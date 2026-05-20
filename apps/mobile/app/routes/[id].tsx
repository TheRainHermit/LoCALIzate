import { ScrollView, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing } from '@/components/ui';
import { fetchEventos } from '@/services/apiClient';
import type { Evento } from '../../../../packages/shared-types';

interface RouteOption {
  id: string;
  modo: 'a_pie' | 'carro' | 'transporte';
  distancia: number;
  tiempo: number;
  descripcion: string;
  precio?: number;
  riesgo: 'bajo' | 'medio' | 'alto';
}

const riskColors = {
  bajo: 'tertiary',
  medio: 'primary',
  alto: 'error',
} as const;

const modeIcons = {
  a_pie: '🚶',
  carro: '🚗',
  transporte: '🚌',
} as const;

export default function RouteDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [evento, setEvento] = useState<Evento | null>(null);
  const [loading, setLoading] = useState(true);

  const ROUTE_OPTIONS: RouteOption[] = [
    {
      id: '1',
      modo: 'a_pie',
      distancia: 1.45,
      tiempo: 18,
      descripcion: 'Caminata por calles conocidas y seguras',
      riesgo: 'bajo',
    },
    {
      id: '2',
      modo: 'carro',
      distancia: 1.45,
      tiempo: 8,
      descripcion: 'Ruta más rápida evitando tráfico',
      precio: 8500,
      riesgo: 'bajo',
    },
    {
      id: '3',
      modo: 'transporte',
      distancia: 1.45,
      tiempo: 12,
      descripcion: 'Autobús disponible en parada cercana',
      precio: 3000,
      riesgo: 'bajo',
    },
  ];

  useEffect(() => {
    loadEvento();
  }, [id]);

  const loadEvento = async () => {
    try {
      const data = await fetchEventos(50);
      const eventoEncontrado = data.find((e: Evento) => e.id === Number(id));
      setEvento(eventoEncontrado || null);
    } catch (error) {
      console.error('Error cargando evento:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </ThemedView>
    );
  }

  if (!evento) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText variant="bodyMD" color="error">
          Evento no encontrado
        </ThemedText>
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg }}>
        {/* Header del Evento */}
        <Card variant="elevated" style={{ marginBottom: Spacing.lg }}>
          <View style={{ gap: Spacing.md }}>
            <ThemedText variant="headlineLG">{evento.nombre}</ThemedText>
            <ThemedText variant="bodyMD" color="onSurfaceVariant">
              {evento.descripcion}
            </ThemedText>
            <View style={{ gap: Spacing.sm }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                <ThemedText>📍 {evento.direccion}</ThemedText>
              </View>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                <ThemedText>📅 {new Date(evento.fecha_inicio).toLocaleDateString()}</ThemedText>
              </View>
            </View>
          </View>
        </Card>

        {/* Opciones de Ruta */}
        <ThemedText variant="titleLG" style={{ marginBottom: Spacing.md }}>
          Opciones de Ruta
        </ThemedText>

        {ROUTE_OPTIONS.map(route => (
          <Card key={route.id} variant="elevated" style={{ marginBottom: Spacing.md }}>
            <View style={{ gap: Spacing.md }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md, flex: 1 }}>
                  <View
                    style={{
                      width: 50,
                      height: 50,
                      borderRadius: 25,
                      backgroundColor: Colors.primaryContainer,
                      justifyContent: 'center',
                      alignItems: 'center',
                    }}
                  >
                    <ThemedText style={{ fontSize: 24 }}>{modeIcons[route.modo]}</ThemedText>
                  </View>
                  <View>
                    <ThemedText variant="titleMD" color="onSurface">
                      {route.modo === 'a_pie' ? 'A pie' : route.modo === 'carro' ? 'En carro' : 'Transporte'}
                    </ThemedText>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      {route.tiempo}min • {route.distancia}km
                    </ThemedText>
                  </View>
                </View>
                <Badge label={route.riesgo} color={riskColors[route.riesgo]} size="sm" />
              </View>

              <ThemedText variant="bodyMD" color="onSurfaceVariant">
                {route.descripcion}
              </ThemedText>

              <View style={{ paddingTop: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.outlineVariant }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Distancia
                    </ThemedText>
                    <ThemedText variant="bodyMD" bold>
                      {route.distancia}km
                    </ThemedText>
                  </View>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Tiempo
                    </ThemedText>
                    <ThemedText variant="bodyMD" bold>
                      {route.tiempo}min
                    </ThemedText>
                  </View>
                  {route.precio && (
                    <View>
                      <ThemedText variant="labelSM" color="onSurfaceVariant">
                        Costo
                      </ThemedText>
                      <ThemedText variant="bodyMD" bold>
                        ${route.precio.toLocaleString('es-CO')}
                      </ThemedText>
                    </View>
                  )}
                </View>
              </View>

              <TouchableOpacity onPress={() => router.push('/routes/navigate')}>
                <Button 
                  label={`Ir a ${evento.nombre}`}
                  style={{ marginTop: Spacing.md }}
                />
              </TouchableOpacity>
            </View>
          </Card>
        ))}
      </ScrollView>
    </ThemedView>
  );
}