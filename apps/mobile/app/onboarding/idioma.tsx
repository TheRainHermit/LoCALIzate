import React, { useState } from 'react';
import { View, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Colors, Spacing } from '@/constants';
import { ThemedText, ThemedView } from '@/components/ui';

interface Language {
  code: string;
  name: string;
  flag: string;
}

const LANGUAGES: Language[] = [
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
];

export default function IdiomaScreen() {
  const router = useRouter();
  const [selectedLanguage, setSelectedLanguage] = useState<string>('es');

  const handleContinue = async () => {
    // TODO: Guardar idioma en AsyncStorage o Zustand store
    console.log(`Idioma: ${selectedLanguage}`);
    router.push('/onboarding/welcome');
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1 }}>
      {/* Header */}
      <View
        style={{
          paddingHorizontal: Spacing.lg,
          paddingTop: Spacing.lg,
          paddingBottom: Spacing.md,
        }}
      >
        <ThemedText variant="headlineLG" style={{ marginBottom: Spacing.md }}>
          ¡Bienvenido a LoCALIzate!
        </ThemedText>
        <ThemedText variant="bodyMD" color="onSurfaceVariant">
          Selecciona tu idioma
        </ThemedText>
      </View>

      <ScrollView
        contentContainerStyle={{
          paddingHorizontal: Spacing.lg,
          paddingVertical: Spacing.md,
          flex: 1,
          justifyContent: 'center',
        }}
        showsVerticalScrollIndicator={false}
      >
        {/* Sección de Idioma */}
        <View style={{ marginBottom: Spacing.xl }}>
          <View
            style={{
              flexDirection: 'row',
              gap: Spacing.lg,
              justifyContent: 'center',
            }}
          >
            {LANGUAGES.map(lang => (
              <TouchableOpacity
                key={lang.code}
                onPress={() => setSelectedLanguage(lang.code)}
                style={{
                  flex: 1,
                  borderRadius: 12,
                  borderWidth: 2,
                  borderColor:
                    selectedLanguage === lang.code
                      ? Colors.primary
                      : Colors['surface-container'],
                  paddingVertical: Spacing.lg,
                  paddingHorizontal: Spacing.lg,
                  justifyContent: 'center',
                  alignItems: 'center',
                  backgroundColor:
                    selectedLanguage === lang.code
                      ? Colors['surface-container']
                      : 'transparent',
                }}
              >
                <ThemedText
                  style={{
                    fontSize: 48,
                    marginBottom: Spacing.md,
                  }}
                >
                  {lang.flag}
                </ThemedText>
                <ThemedText
                  variant="titleMD"
                  style={{
                    fontWeight:
                      selectedLanguage === lang.code ? '600' : '400',
                    color:
                      selectedLanguage === lang.code
                        ? Colors.primary
                        : Colors['on-surface-variant'],
                    textAlign: 'center',
                  }}
                >
                  {lang.name}
                </ThemedText>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Botón Continuar */}
        <View style={{ marginTop: Spacing.xl, marginBottom: Spacing.xl }}>
          <TouchableOpacity
            onPress={handleContinue}
            style={{
              backgroundColor: Colors.primary,
              borderRadius: 12,
              paddingVertical: Spacing.lg,
              paddingHorizontal: Spacing.lg,
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <ThemedText
              variant="labelLG"
              style={{
                color: 'white',
                fontWeight: '600',
              }}
            >
              Continuar
            </ThemedText>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </ThemedView>
  );
}
