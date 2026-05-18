import { Stack } from 'expo-router';
import { Colors } from '@/constants';

export default function LugarLayout() {
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
        name="[id]"
        options={{
          title: 'Detalles',
          headerTransparent: true,
          headerBlurEffect: 'light',
        }}
      />
    </Stack>
  );
}