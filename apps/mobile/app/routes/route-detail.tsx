import { ScrollView, View } from 'react-native';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing } from '@/components/ui';

interface RouteOption {
  id: string;
  modo: 'a_pie' | 'carro' | 'transporte';
  distancia: number;
  tiempo: number;
  descripcion: string;
  precio?: number;
  riesgo: 'bajo' | 'medio' | 'alto';
}

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
  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg }}>
        <ThemedText variant="headlineLG" style={{ marginBottom: Spacing.lg }}>
          Opciones de Ruta
        </ThemedText>

        {ROUTE_OPTIONS.map(route => (
          <Card key={route.id} variant="elevated" style={{ marginBottom: Spacing.md }}>
            <View style={{ gap: Spacing.md }}>
              {/* Header */}
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.md }}>
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
                      {route.modo === 'a_pie' ? 'A pie' : route.modo === 'carro' ? 'En carro' : 'Transporte Público'}
                    </ThemedText>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      {route.tiempo}min • {route.distancia}km
                    </ThemedText>
                  </View>
                </View>
                <Badge label={route.riesgo} color={riskColors[route.riesgo]} size="sm" />
              </View>

              {/* Descripción */}
              <ThemedText variant="bodyMD" color="onSurfaceVariant">
                {route.descripcion}
              </ThemedText>

              {/* Stats */}
              <View style={{ paddingTop: Spacing.md, borderTopWidth: 1, borderTopColor: Colors.outlineVariant }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Distancia
                    </ThemedText>
                    <ThemedText variant="bodyMD" color="onSurface" bold>
                      {route.distancia}km
                    </ThemedText>
                  </View>
                  <View>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      Tiempo
                    </ThemedText>
                    <ThemedText variant="bodyMD" color="onSurface" bold>
                      {route.tiempo}min
                    </ThemedText>
                  </View>
                  {route.precio && (
                    <View>
                      <ThemedText variant="labelSM" color="onSurfaceVariant">
                        Costo
                      </ThemedText>
                      <ThemedText variant="bodyMD" color="onSurface" bold>
                        COP ${route.precio.toLocaleString()}
                      </ThemedText>
                    </View>
                  )}
                </View>
              </View>

              {/* CTA */}
              <Button
                label="Seleccionar"
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