import { Stack } from 'expo-router';
import { Colors } from '@/constants';

export default function OnboardingLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        cardStyle: {
          backgroundColor: Colors.surface,
        },
      }}
    >
      <Stack.Screen name="welcome" />
      <Stack.Screen name="interests" />
      <Stack.Screen name="permissions" />
    </Stack>
  );
}