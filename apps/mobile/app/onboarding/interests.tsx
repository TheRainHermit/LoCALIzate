import { ScrollView, View, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { useUserStore } from '@/store/userStore';
import { ThemedView, ThemedText, Card, Button, Colors, Spacing } from '@/components/ui';

const INTEREST_CATEGORIES = [
  { id: 'cultura', name: 'Cultura', emoji: '🏛️' },
  { id: 'gastronomia', name: 'Gastronomía', emoji: '🍴' },
  { id: 'naturaleza', name: 'Naturaleza', emoji: '🌿' },
  { id: 'deportes', name: 'Deportes', emoji: '⚽' },
  { id: 'vida-nocturna', name: 'Vida Nocturna', emoji: '🎉' },
  { id: 'compras', name: 'Compras', emoji: '🛍️' },
  { id: 'fotografia', name: 'Fotografía', emoji: '📸' },
  { id: 'historia', name: 'Historia', emoji: '📚' },
  { id: 'musica', name: 'Música', emoji: '🎵' },
  { id: 'aventura', name: 'Aventura', emoji: '🧗' },
];

export default function InterestsScreen() {
  const router = useRouter();
  const { userInterests, setUserInterests } = useUserStore();
  const [selectedInterests, setSelectedInterests] = useState<string[]>(userInterests);

  const toggleInterest = (interestId: string) => {
    setSelectedInterests(prev => {
      if (prev.includes(interestId)) {
        return prev.filter(i => i !== interestId);
      } else if (prev.length < 5) {
        return [...prev, interestId];
      }
      return prev;
    });
  };

  const handleContinue = () => {
    setUserInterests(selectedInterests.map(id => INTEREST_CATEGORIES.find(i => i.id === id)?.name || id));
    router.push('/onboarding/permissions');
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineLG">¿Cuáles son tus intereses?</ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.sm }}>
          Selecciona hasta 5 para recomendaciones personalizadas
        </ThemedText>
      </View>

      {/* Grid de intereses */}
      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
        }}
      >
        <View style={{ gap: Spacing.md }}>
          {INTEREST_CATEGORIES.map(interest => {
            const isSelected = selectedInterests.includes(interest.id);
            return (
              <TouchableOpacity
                key={interest.id}
                onPress={() => toggleInterest(interest.id)}
                activeOpacity={0.7}
              >
                <Card
                  variant={isSelected ? 'filled' : 'outlined'}
                  style={{
                    flexDirection: 'row',
                    alignItems: 'center',
                    gap: Spacing.md,
                    paddingHorizontal: Spacing.lg,
                    paddingVertical: Spacing.md,
                    borderWidth: isSelected ? 0 : 1,
                    borderColor: isSelected ? 'transparent' : Colors.outline,
                    backgroundColor: isSelected ? Colors.primaryContainer : Colors.surface,
                  }}
                >
                  <ThemedText style={{ fontSize: 24 }}>{interest.emoji}</ThemedText>
                  <View style={{ flex: 1 }}>
                    <ThemedText
                      variant="bodyMD"
                      color={isSelected ? 'onPrimaryContainer' : 'onSurface'}
                    >
                      {interest.name}
                    </ThemedText>
                  </View>
                  {isSelected && (
                    <ThemedText style={{ fontSize: 20, color: Colors.primary }}>✓</ThemedText>
                  )}
                </Card>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Info */}
        <Card
          variant="outlined"
          style={{
            marginTop: Spacing.xl,
            borderLeftWidth: 4,
            borderLeftColor: Colors.tertiary,
          }}
        >
          <View style={{ gap: Spacing.sm }}>
            <ThemedText variant="titleSM" color="onTertiaryContainer">
              💡 Consejo
            </ThemedText>
            <ThemedText variant="bodySM" color="onSurfaceVariant">
              Puedes cambiar tus preferencias en cualquier momento desde tu perfil
            </ThemedText>
          </View>
        </Card>
      </ScrollView>

      {/* Botones */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingBottom: Spacing.xl, gap: Spacing.md }}>
        <Button
          label="Continuar"
          variant="filled"
          size="lg"
          onPress={handleContinue}
          disabled={selectedInterests.length === 0}
        />
      </View>
    </ThemedView>
  );
}