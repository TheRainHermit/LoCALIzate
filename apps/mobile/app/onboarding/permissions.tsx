import { ScrollView, View, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import * as Location from 'expo-location';
import { useOnboardingStore } from '@/store/onboardingStore';
import { ThemedView, ThemedText, Card, Button, Colors, Spacing } from '@/components/ui';

interface Permission {
  id: string;
  name: string;
  description: string;
  emoji: string;
  required: boolean;
  action: () => Promise<boolean>;
}

export default function PermissionsScreen() {
  const router = useRouter();
  const markOnboardingComplete = useOnboardingStore(state => state.markOnboardingComplete);
  const [permissions, setPermissions] = useState<Permission[]>([
    {
      id: 'location',
      name: 'Ubicación',
      description: 'Necesaria para navegación y recomendaciones cercanas',
      emoji: '📍',
      required: true,
      action: async () => {
        const { status } = await Location.requestForegroundPermissionsAsync();
        return status === 'granted';
      },
    },
    // Notificaciones removido por compatibilidad con Expo Go
    // Se puede agregar con development build
  ]);

  const [grantedPermissions, setGrantedPermissions] = useState<string[]>([]);

  const requestPermission = async (permissionId: string) => {
    const permission = permissions.find(p => p.id === permissionId);
    if (!permission) return;

    try {
      const granted = await permission.action();
      if (granted) {
        setGrantedPermissions(prev => [...prev, permissionId]);
      } else {
        Alert.alert('Permiso denegado', `No se otorgó permiso para ${permission.name.toLowerCase()}`);
      }
    } catch (error) {
      console.error(`Error requesting ${permissionId} permission:`, error);
    }
  };

  const handleComplete = () => {
    markOnboardingComplete();
    router.replace('/(tabs)/explorer');
  };

  const allRequiredGranted = permissions
    .filter(p => p.required)
    .every(p => grantedPermissions.includes(p.id));

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingTop: Spacing.lg }}>
        <ThemedText variant="headlineLG">Permisos Necesarios</ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant" style={{ marginTop: Spacing.sm }}>
          Para una mejor experiencia, necesitamos algunos permisos
        </ThemedText>
      </View>

      {/* Permisos */}
      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.lg,
        }}
      >
        <View style={{ gap: Spacing.md }}>
          {permissions.map(permission => {
            const isGranted = grantedPermissions.includes(permission.id);

            return (
              <Card
                key={permission.id}
                variant={isGranted ? 'filled' : 'outlined'}
                style={{
                  borderLeftWidth: permission.required ? 4 : 0,
                  borderLeftColor: permission.required ? Colors.secondary : 'transparent',
                }}
              >
                <View style={{ gap: Spacing.md }}>
                  <View style={{ flexDirection: 'row', gap: Spacing.md, alignItems: 'flex-start' }}>
                    <ThemedText style={{ fontSize: 28 }}>{permission.emoji}</ThemedText>
                    <View style={{ flex: 1 }}>
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.sm }}>
                        <ThemedText variant="titleMD" color="onSurface">
                          {permission.name}
                        </ThemedText>
                        {permission.required && (
                          <ThemedText variant="labelSM" style={{ color: Colors.secondary }}>
                            Requerido
                          </ThemedText>
                        )}
                      </View>
                      <ThemedText
                        variant="bodySM"
                        color="onSurfaceVariant"
                        style={{ marginTop: Spacing.xs }}
                      >
                        {permission.description}
                      </ThemedText>
                    </View>
                  </View>

                  {isGranted ? (
                    <View
                      style={{
                        flexDirection: 'row',
                        alignItems: 'center',
                        gap: Spacing.sm,
                        paddingTop: Spacing.md,
                        borderTopWidth: 1,
                        borderTopColor: Colors.outlineVariant,
                      }}
                    >
                      <ThemedText style={{ fontSize: 20, color: Colors.tertiary }}>✓</ThemedText>
                      <ThemedText variant="labelMD" color="onTertiary">
                        Permiso otorgado
                      </ThemedText>
                    </View>
                  ) : (
                    <Button
                      label={`Permitir ${permission.name.toLowerCase()}`}
                      variant="tonal"
                      size="md"
                      onPress={() => requestPermission(permission.id)}
                      style={{ marginTop: Spacing.md }}
                    />
                  )}
                </View>
              </Card>
            );
          })}
        </View>

        {/* Nota */}
        <Card
          variant="outlined"
          style={{
            marginTop: Spacing.xl,
            backgroundColor: Colors.surfaceContainerLow,
          }}
        >
          <ThemedText variant="bodySM" color="onSurfaceVariant">
            Siempre puedes cambiar los permisos en la configuración de tu teléfono
          </ThemedText>
        </Card>
      </ScrollView>

      {/* Botones */}
      <View style={{ paddingHorizontal: Spacing.lg, paddingBottom: Spacing.xl, gap: Spacing.md }}>
        <Button
          label="Comenzar a Explorar 🚀"
          variant="filled"
          size="lg"
          onPress={handleComplete}
          disabled={!allRequiredGranted}
        />
        {!allRequiredGranted && (
          <ThemedText variant="labelSM" color="onSurfaceVariant" center>
            Completa los permisos requeridos para continuar
          </ThemedText>
        )}
      </View>
    </ThemedView>
  );
}