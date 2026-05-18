import { ScrollView, View, TouchableOpacity } from 'react-native';
import { useUserStore } from '@/store/userStore';
import { ThemedView, ThemedText, Card, Badge, Button, Colors, Spacing } from '@/components/ui';

const INTERESTS = ['Cultura', 'Gastronomía', 'Naturaleza', 'Deportes', 'Vida Nocturna', 'Compras', 'Fotografía'];

export default function ProfileScreen() {
  const { userInterests, setUserInterests } = useUserStore();

  const toggleInterest = (interest: string) => {
    if (userInterests.includes(interest)) {
      setUserInterests(userInterests.filter(i => i !== interest));
    } else {
      setUserInterests([...userInterests, interest]);
    }
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineMD" color="primary">
          👤 Mi Perfil
        </ThemedText>
      </View>

      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
          gap: Spacing.lg,
        }}
      >
        {/* User Info Card */}
        <Card variant="elevated">
          <View style={{ alignItems: 'center', gap: Spacing.md }}>
            <View
              style={{
                width: 80,
                height: 80,
                borderRadius: 40,
                backgroundColor: Colors.primaryContainer,
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <ThemedText style={{ fontSize: 40 }}>👤</ThemedText>
            </View>
            <ThemedText variant="titleLG">Usuario Cali</ThemedText>
            <ThemedText variant="bodySM" color="onSurfaceVariant">
              Viajero local | Miembro desde 2024
            </ThemedText>
          </View>
        </Card>

        {/* Intereses */}
        <View>
          <ThemedText variant="titleLG" style={{ marginBottom: Spacing.md }}>
            Mis Intereses
          </ThemedText>
          <View style={{ gap: Spacing.sm }}>
            {INTERESTS.map(interest => (
              <TouchableOpacity
                key={interest}
                onPress={() => toggleInterest(interest)}
                activeOpacity={0.7}
              >
                <Card
                  variant={userInterests.includes(interest) ? 'filled' : 'outlined'}
                  style={{
                    flexDirection: 'row',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingHorizontal: Spacing.md,
                    paddingVertical: Spacing.sm,
                  }}
                >
                  <ThemedText
                    variant="bodyMD"
                    color={userInterests.includes(interest) ? 'onSurface' : 'onSurfaceVariant'}
                  >
                    {interest}
                  </ThemedText>
                  <ThemedText style={{ fontSize: 18 }}>
                    {userInterests.includes(interest) ? '✓' : ''}
                  </ThemedText>
                </Card>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Stats */}
        <View style={{ gap: Spacing.sm }}>
          <ThemedText variant="titleLG">Estadísticas</ThemedText>
          <View style={{ flexDirection: 'row', gap: Spacing.md }}>
            <Card variant="filled" style={{ flex: 1, alignItems: 'center', paddingVertical: Spacing.lg }}>
              <ThemedText variant="headlineMD" color="primary">
                0
              </ThemedText>
              <ThemedText variant="labelSM" color="onSurfaceVariant">
                Lugares Visitados
              </ThemedText>
            </Card>
            <Card variant="filled" style={{ flex: 1, alignItems: 'center', paddingVertical: Spacing.lg }}>
              <ThemedText variant="headlineMD" color="secondary">
                0
              </ThemedText>
              <ThemedText variant="labelSM" color="onSurfaceVariant">
                Guardados
              </ThemedText>
            </Card>
          </View>
        </View>

        {/* Actions */}
        <View style={{ gap: Spacing.md, marginBottom: Spacing.xl }}>
          <Button label="Editar Perfil" variant="outlined" size="md" onPress={() => {}} />
          <Button label="Cerrar Sesión" variant="outlined" size="md" onPress={() => {}} />
        </View>
      </ScrollView>
    </ThemedView>
  );
}