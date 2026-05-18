import { Image, TouchableOpacity, View } from 'react-native';
import { useRouter } from 'expo-router';
import { Card, ThemedText, Badge, Colors, Spacing } from '@/components/ui';

interface Lugar {
  id: string;
  nombre: string;
  zona: string;
  descripcion_corta: string;
  imagen?: string;
  categoria?: string;
  rating?: number;
  distancia?: number;
}

export default function LocationCard({ lugar }: { lugar: Lugar }) {
  const router = useRouter();

  const handlePress = () => {
    router.push({
      pathname: '/lugar/[id]',
      params: { id: lugar.id },
    });
  };

  return (
    <TouchableOpacity onPress={handlePress} activeOpacity={0.8}>
      <Card variant="elevated">
        {/* Imagen */}
        {lugar.imagen && (
          <Image
            source={{ uri: lugar.imagen }}
            style={{
              width: '100%',
              height: 160,
              borderRadius: 12,
              marginBottom: Spacing.md,
              backgroundColor: Colors.surfaceContainerLow,
            }}
          />
        )}

        {/* Contenido */}
        <View style={{ gap: Spacing.xs }}>
          {/* Header con nombre y badge */}
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <View style={{ flex: 1 }}>
              <ThemedText variant="titleLG" color="onSurface">
                {lugar.nombre}
              </ThemedText>
              <ThemedText variant="bodySM" color="onSurfaceVariant" style={{ marginTop: Spacing.xs }}>
                {lugar.zona}
              </ThemedText>
            </View>
            {lugar.categoria && (
              <Badge label={lugar.categoria} color="primary" size="sm" />
            )}
          </View>

          {/* Descripción */}
          <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.sm }}>
            {lugar.descripcion_corta}
          </ThemedText>

          {/* Footer con rating y distancia */}
          {(lugar.rating || lugar.distancia) && (
            <View
              style={{
                flexDirection: 'row',
                gap: Spacing.lg,
                marginTop: Spacing.md,
                paddingTop: Spacing.md,
                borderTopWidth: 1,
                borderTopColor: Colors.outlineVariant,
              }}
            >
              {lugar.rating && (
                <View style={{ flexDirection: 'row', gap: Spacing.xs }}>
                  <ThemedText style={{ fontSize: 16 }}>⭐</ThemedText>
                  <ThemedText variant="labelMD" color="onSurfaceVariant">
                    {lugar.rating.toFixed(1)}
                  </ThemedText>
                </View>
              )}
              {lugar.distancia && (
                <View style={{ flexDirection: 'row', gap: Spacing.xs }}>
                  <ThemedText style={{ fontSize: 16 }}>📍</ThemedText>
                  <ThemedText variant="labelMD" color="onSurfaceVariant">
                    {lugar.distancia}m
                  </ThemedText>
                </View>
              )}
            </View>
          )}
        </View>
      </Card>
    </TouchableOpacity>
  );
}