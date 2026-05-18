import { Stack } from 'expo-router';
import { Colors } from '@/constants';

export default function RoutesLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerBackTitle: 'Atrás',
        headerTintColor: Colors.primary,
        headerTitleStyle: {
          fontSize: 18,
          fontWeight: '600',
        },
        cardStyle: {
          backgroundColor: Colors.surface,
        },
      }}
    >
      <Stack.Screen
        name="navigate"
        options={{
          title: 'Navegación',
        }}
      />
      <Stack.Screen
        name="route-detail"
        options={{
          title: 'Detalles de Ruta',
        }}
      />
    </Stack>
  );
}