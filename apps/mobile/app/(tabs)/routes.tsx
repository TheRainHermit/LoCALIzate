import { ScrollView, View, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing } from '@/components/ui';
import { fetchEventos } from '@/services/apiClient';
import type { Evento } from '../../../../packages/shared-types';

export default function RoutesScreen() {
  const router = useRouter();
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEventos();
  }, []);

  const loadEventos = async () => {
    try {
      const data = await fetchEventos(10);
      // Convertir eventos a rutas temáticas
      setEventos(data);
    } catch (error) {
      console.error('Error cargando eventos:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (idx: number) => {
    const colors = ['tertiary', 'primary', 'error'];
    return colors[idx % colors.length];
  };

  if (loading) {
    return (
      <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineMD" color="primary">
          🛣️ Rutas Inteligentes
        </ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
          Itinerarios por eventos y lugares
        </ThemedText>
      </View>

      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
          gap: Spacing.md,
        }}
      >
        {eventos.map((evento, idx) => (
          <TouchableOpacity
            key={evento.id}
            onPress={() => router.push(`/routes/${evento.id}`)}
            activeOpacity={0.7}
          >
            <Card variant="elevated">
              <View style={{ gap: Spacing.md }}>
                {/* Header */}
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <View style={{ flex: 1 }}>
                    <ThemedText variant="titleLG">{evento.nombre}</ThemedText>
                  </View>
                  <Badge 
                    label={['Fácil', 'Media', 'Difícil'][idx % 3]} 
                    color={getDifficultyColor(idx)} 
                    size="sm" 
                  />
                </View>

                {/* Descripción */}
                <ThemedText variant="bodySM" color="onSurfaceVariant" numberOfLines={2}>
                  {evento.descripcion}
                </ThemedText>

                {/* Metadata */}
                <View style={{ gap: Spacing.sm }}>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                    <ThemedText style={{ fontSize: 14 }}>📅</ThemedText>
                    <ThemedText variant="labelSM">
                      {new Date(evento.fecha_inicio).toLocaleDateString()}
                    </ThemedText>
                  </View>
                  <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                    <ThemedText style={{ fontSize: 14 }}>📍</ThemedText>
                    <ThemedText variant="labelSM">{evento.direccion}</ThemedText>
                  </View>
                </View>

                {/* Stats */}
                <View style={{ flexDirection: 'row', gap: Spacing.lg, paddingTop: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.outline }}>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Distancia
                    </ThemedText>
                    <ThemedText variant="titleMD" color="primary">
                      2.5 km
                    </ThemedText>
                  </View>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Duración
                    </ThemedText>
                    <ThemedText variant="titleMD" color="primary">
                      2h 30m
                    </ThemedText>
                  </View>
                </View>
              </View>
            </Card>
          </TouchableOpacity>
        ))}

        {eventos.length === 0 && (
          <Card variant="outlined" style={{ alignItems: 'center', padding: Spacing.lg }}>
            <ThemedText variant="bodyMD" color="onSurfaceVariant">
              No hay rutas disponibles
            </ThemedText>
          </Card>
        )}
      </ScrollView>
    </ThemedView>
  );
}