import { ScrollView, View } from 'react-native';
import { useState, useEffect } from 'react';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing } from '@/components/ui';

interface Ruta {
  id: string;
  nombre: string;
  descripcion: string;
  duracion: string;
  distancia: number;
  dificultad: 'fácil' | 'media' | 'difícil';
  lugares: number;
}

const RUTAS_EJEMPLO: Ruta[] = [
  {
    id: '1',
    nombre: 'Ruta Histórica Centro',
    descripcion: 'Descubre la arquitectura colonial y moderna de Cali',
    duracion: '2 horas',
    distancia: 3.5,
    dificultad: 'fácil',
    lugares: 5,
  },
  {
    id: '2',
    nombre: 'Sabores Locales',
    descripcion: 'Gastronomía auténtica caleña: sancochos, empanadas y más',
    duracion: '3 horas',
    distancia: 2.1,
    dificultad: 'media',
    lugares: 7,
  },
];

export default function RoutesScreen() {
  const [rutas, setRutas] = useState<Ruta[]>(RUTAS_EJEMPLO);

  const difficultyColor = (dif: string) => {
    switch (dif) {
      case 'fácil':
        return 'tertiary';
      case 'media':
        return 'primary';
      case 'difícil':
        return 'error';
      default:
        return 'primary';
    }
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineMD" color="primary">
          🛣️ Rutas Inteligentes
        </ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
          Itinerarios personalizados por Cali
        </ThemedText>
      </View>

      {/* Rutas List */}
      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
          gap: Spacing.md,
        }}
      >
        {rutas.map(ruta => (
          <Card key={ruta.id} variant="elevated">
            <View style={{ gap: Spacing.md }}>
              {/* Título y dificultad */}
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <View style={{ flex: 1 }}>
                  <ThemedText variant="titleLG">{ruta.nombre}</ThemedText>
                </View>
                <Badge label={ruta.dificultad} color={difficultyColor(ruta.dificultad)} size="sm" />
              </View>

              {/* Descripción */}
              <ThemedText variant="bodyMD" color="onSurfaceVariant">
                {ruta.descripcion}
              </ThemedText>

              {/* Stats */}
              <View
                style={{
                  flexDirection: 'row',
                  gap: Spacing.lg,
                  paddingTop: Spacing.md,
                  borderTopWidth: 1,
                  borderTopColor: Colors.outlineVariant,
                }}
              >
                <View style={{ flex: 1 }}>
                  <ThemedText variant="labelSM" color="onSurfaceVariant">
                    ⏱️ Duración
                  </ThemedText>
                  <ThemedText variant="bodyMD" color="onSurface">
                    {ruta.duracion}
                  </ThemedText>
                </View>
                <View style={{ flex: 1 }}>
                  <ThemedText variant="labelSM" color="onSurfaceVariant">
                    📏 Distancia
                  </ThemedText>
                  <ThemedText variant="bodyMD" color="onSurface">
                    {ruta.distancia}km
                  </ThemedText>
                </View>
                <View style={{ flex: 1 }}>
                  <ThemedText variant="labelSM" color="onSurfaceVariant">
                    📍 Lugares
                  </ThemedText>
                  <ThemedText variant="bodyMD" color="onSurface">
                    {ruta.lugares}
                  </ThemedText>
                </View>
              </View>

              {/* CTA Button */}
              <Button
                label="Iniciar Ruta"
                variant="filled"
                size="md"
                onPress={() => {}}
                style={{ marginTop: Spacing.md }}
              />
            </View>
          </Card>
        ))}
      </ScrollView>
    </ThemedView>
  );
}