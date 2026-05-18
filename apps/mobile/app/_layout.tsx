import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { useOnboardingStore } from '@/store/onboardingStore';
import { Colors } from '@/constants';
import * as Font from 'expo-font';

export default function RootLayout() {
  useEffect(() => {
    Font.loadAsync({
      'Plus Jakarta Sans': require('../assets/fonts/PlusJakartaSans-Regular.ttf'),
      'Be Vietnam Pro': require('../assets/fonts/BeVietnamPro-Regular.ttf'),
    });
  }, []);

  const hasCompletedOnboarding = useOnboardingStore(state => state.hasCompletedOnboarding);

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        cardStyle: {
          backgroundColor: Colors.surface,
        },
      }}
    >
      {!hasCompletedOnboarding ? (
        <Stack.Screen name="onboarding" options={{ animationEnabled: false }} />
      ) : (
        <Stack.Screen name="(tabs)" options={{ animationEnabled: false }} />
      )}
      <Stack.Screen name="lugar" options={{ presentation: 'modal' }} />
      <Stack.Screen name="routes" />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}