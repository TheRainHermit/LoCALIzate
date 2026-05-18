import { View, TouchableOpacity } from 'react-native';
import { useState } from 'react';
import { ThemedView, ThemedText, Button, Card, Colors, Spacing } from '@/components/ui';

export default function CameraScreen() {
  const [isCapturing, setIsCapturing] = useState(false);

  const handleCameraOpen = () => {
    setIsCapturing(true);
    // Lógica para abrir la cámara
  };

  const handleCapture = () => {
    // Lógica para procesar la imagen con visión
  };

  return (
    <ThemedView variant="surface" style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: Spacing.lg }}>
      <View style={{ alignItems: 'center', gap: Spacing.xl }}>
        {/* Icono grande */}
        <View
          style={{
            width: 120,
            height: 120,
            borderRadius: 60,
            backgroundColor: Colors.primaryContainer,
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <ThemedText style={{ fontSize: 60 }}>📸</ThemedText>
        </View>

        {/* Título */}
        <ThemedText variant="headlineLG" color="onBackground" center>
          Reconocimiento Visual
        </ThemedText>

        {/* Descripción */}
        <ThemedText variant="bodyMD" color="onSurfaceVariant" center>
          Apunta a un monumento o lugar emblemático para descubrir información fascinante
        </ThemedText>

        {/* CTA */}
        <Button
          label="Abrir Cámara"
          size="lg"
          onPress={handleCameraOpen}
          style={{ alignSelf: 'center', width: '80%' }}
        />

        {/* Info Card */}
        <Card variant="filled" style={{ marginTop: Spacing.lg, width: '100%' }}>
          <ThemedText variant="labelLG" color="onSurface">
            💡 Funciona mejor con:
          </ThemedText>
          <ThemedText variant="bodySM" color="onSurfaceVariant" style={{ marginTop: Spacing.sm }}>
            • Buena iluminación
          </ThemedText>
          <ThemedText variant="bodySM" color="onSurfaceVariant">
            • Vista clara del monumento
          </ThemedText>
          <ThemedText variant="bodySM" color="onSurfaceVariant">
            • Distancia de 1-5 metros
          </ThemedText>
        </Card>
      </View>
    </ThemedView>
  );
}