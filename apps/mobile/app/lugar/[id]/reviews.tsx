import { ScrollView, View, FlatList } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { ThemedView, ThemedText, Card, Colors, Spacing } from '@/components/ui';

interface Review {
  id: string;
  autor: string;
  calificacion: number;
  texto: string;
  fecha: string;
  avatar: string;
}

const REVIEWS_EJEMPLO: Review[] = [
  {
    id: '1',
    autor: 'Juan García',
    calificacion: 5,
    texto: 'Lugar increíble, muy bien mantenido y con mucha historia. La guía turística fue excelente.',
    fecha: '2024-05-10',
    avatar: '👨‍💼',
  },
  {
    id: '2',
    autor: 'María López',
    calificacion: 4,
    texto: 'Hermoso lugar, aunque un poco concurrido en los fines de semana. Recomendado.',
    fecha: '2024-05-08',
    avatar: '👩‍🦱',
  },
];

export default function ReviewsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={{ paddingHorizontal: Spacing.lg, paddingVertical: Spacing.lg }}>
        <ThemedText variant="headlineMD" style={{ marginBottom: Spacing.lg }}>
          Reseñas de Visitantes
        </ThemedText>

        <FlatList
          data={REVIEWS_EJEMPLO}
          scrollEnabled={false}
          renderItem={({ item }) => (
            <Card variant="elevated" style={{ marginBottom: Spacing.md }}>
              <View style={{ gap: Spacing.md }}>
                {/* Header */}
                <View style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'center' }}>
                  <View
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: 22,
                      backgroundColor: Colors.primaryContainer,
                      justifyContent: 'center',
                      alignItems: 'center',
                    }}
                  >
                    <ThemedText style={{ fontSize: 24 }}>{item.avatar}</ThemedText>
                  </View>
                  <View style={{ flex: 1 }}>
                    <ThemedText variant="bodyMD" color="onSurface">
                      {item.autor}
                    </ThemedText>
                    <ThemedText variant="labelSM" color="onSurfaceVariant">
                      {new Date(item.fecha).toLocaleDateString()}
                    </ThemedText>
                  </View>
                </View>

                {/* Rating */}
                <View style={{ flexDirection: 'row', gap: Spacing.xs }}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <ThemedText key={i} style={{ fontSize: 16 }}>
                      {i < item.calificacion ? '⭐' : '☆'}
                    </ThemedText>
                  ))}
                </View>

                {/* Texto */}
                <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ lineHeight: 22 }}>
                  {item.texto}
                </ThemedText>
              </View>
            </Card>
          )}
          keyExtractor={item => item.id}
        />
      </ScrollView>
    </ThemedView>
  );
}